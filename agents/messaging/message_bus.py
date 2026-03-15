"""Pub/sub message bus implementation for inter-agent communication."""

import asyncio
import inspect
from datetime import datetime, timedelta, timezone
from typing import Any, Awaitable, Callable, Optional

from agents.messaging.a2a_protocol import A2AMessage, MessageType
from agents.utils.logger import get_logger

logger = get_logger(__name__)

SubscriberCallback = Callable[[A2AMessage], Any | Awaitable[Any]]


class MessageBus:
    """Pub/Sub message bus for inter-agent communication."""

    def __init__(self, default_timeout_seconds: int = 30, max_history: int = 1000):
        self._subscribers: dict[str, list[SubscriberCallback]] = {}
        self._pending_messages: dict[str, dict[str, Any]] = {}
        self._delivery_status: dict[str, dict[str, Any]] = {}
        self._message_history: list[A2AMessage] = []
        self._response_waiters: dict[str, asyncio.Future[A2AMessage]] = {}
        self._default_timeout_seconds = default_timeout_seconds
        self._max_history = max_history
        self._lock = asyncio.Lock()

    async def publish(self, message: A2AMessage, timeout_seconds: Optional[int] = None) -> None:
        """Publish a message to subscribers based on recipient routing."""
        created_at = datetime.now(timezone.utc)
        effective_timeout = timeout_seconds or self._default_timeout_seconds
        recipients = self._resolve_recipients(message.recipient)

        logger.info(
            "message_published",
            message_id=message.message_id,
            sender=message.sender,
            recipient=message.recipient,
            message_type=message.message_type.value,
            routed_recipients=len(recipients),
        )

        async with self._lock:
            self._message_history.append(message)
            if len(self._message_history) > self._max_history:
                self._message_history.pop(0)

            self._pending_messages[message.message_id] = {
                "message": message,
                "created_at": created_at,
                "timeout_at": created_at + timedelta(seconds=effective_timeout),
                "recipients": recipients,
            }

            self._delivery_status[message.message_id] = {
                "state": "pending",
                "created_at": created_at,
                "completed_at": None,
                "recipients": recipients,
                "delivered": [],
                "failed": {},
                "timeout_seconds": effective_timeout,
            }

        if not recipients:
            await self._finalize_delivery(
                message_id=message.message_id,
                delivered=[],
                failed={"routing": "No subscribers found for recipient."},
            )
            return

        delivered: list[str] = []
        failed: dict[str, str] = {}

        for recipient in recipients:
            callbacks = list(self._subscribers.get(recipient, []))
            if not callbacks:
                failed[recipient] = "No subscriber callback registered."
                continue

            callback_errors: list[str] = []
            for callback in callbacks:
                try:
                    result = callback(message)
                    if inspect.isawaitable(result):
                        await result
                except Exception as exc:  # pragma: no cover - defensive callback handling
                    callback_errors.append(str(exc))
                    logger.error(
                        "message_callback_failed",
                        recipient=recipient,
                        callback=getattr(callback, "__name__", "anonymous"),
                        error=str(exc),
                    )

            if callback_errors:
                failed[recipient] = "; ".join(callback_errors)
            else:
                delivered.append(recipient)

        await self._finalize_delivery(message.message_id, delivered=delivered, failed=failed)
        await self._resolve_response_waiter(message)
        await self._cleanup_timeouts()

    def subscribe(self, agent_name: str, callback: SubscriberCallback) -> None:
        """Subscribe an agent callback for direct recipient routing."""
        self._subscribers.setdefault(agent_name, []).append(callback)
        logger.info("agent_subscribed", agent=agent_name)

    def unsubscribe(self, agent_name: str, callback: SubscriberCallback) -> None:
        """Unsubscribe a callback from an agent channel."""
        callbacks = self._subscribers.get(agent_name, [])
        if callback in callbacks:
            callbacks.remove(callback)
            logger.info("agent_unsubscribed", agent=agent_name)

        if not callbacks and agent_name in self._subscribers:
            del self._subscribers[agent_name]

    async def request_response(
        self,
        message: A2AMessage,
        timeout_seconds: int = 30,
    ) -> Optional[A2AMessage]:
        """Send a request message and await a correlated response or error."""
        correlation_id = message.message_id
        message.message_type = MessageType.REQUEST

        loop = asyncio.get_running_loop()
        response_future: asyncio.Future[A2AMessage] = loop.create_future()

        async with self._lock:
            self._response_waiters[correlation_id] = response_future

        await self.publish(message, timeout_seconds=timeout_seconds)

        try:
            response = await asyncio.wait_for(response_future, timeout=timeout_seconds)
            return response
        except asyncio.TimeoutError:
            logger.warning("request_response_timeout", correlation_id=correlation_id)
            return None
        finally:
            async with self._lock:
                self._response_waiters.pop(correlation_id, None)

    def get_history(self, sender: Optional[str] = None) -> list[A2AMessage]:
        """Get message history, optionally filtered by sender."""
        if sender:
            return [message for message in self._message_history if message.sender == sender]
        return list(self._message_history)

    def get_delivery_status(self, message_id: str) -> Optional[dict[str, Any]]:
        """Return delivery status snapshot for a specific message."""
        status = self._delivery_status.get(message_id)
        if not status:
            return None
        return dict(status)

    def clear_history(self) -> None:
        """Clear history and delivery tracking state."""
        self._message_history.clear()
        self._delivery_status.clear()
        self._pending_messages.clear()

    def _resolve_recipients(self, recipient: str) -> list[str]:
        """Resolve recipient targets for direct or broadcast delivery."""
        if recipient == "broadcast":
            return list(self._subscribers.keys())
        return [recipient]

    async def _resolve_response_waiter(self, message: A2AMessage) -> None:
        """Resolve response waiter for correlated response and error messages."""
        if message.message_type not in (MessageType.RESPONSE, MessageType.ERROR):
            return
        if not message.correlation_id:
            return

        async with self._lock:
            future = self._response_waiters.get(message.correlation_id)

        if future and not future.done():
            future.set_result(message)

    async def _finalize_delivery(
        self,
        message_id: str,
        delivered: list[str],
        failed: dict[str, str],
    ) -> None:
        """Finalize delivery status and release pending message tracking."""
        completed_at = datetime.now(timezone.utc)

        if delivered and not failed:
            final_state = "delivered"
        elif delivered and failed:
            final_state = "partial"
        else:
            final_state = "failed"

        async with self._lock:
            status = self._delivery_status.get(message_id)
            if status:
                status["state"] = final_state
                status["completed_at"] = completed_at
                status["delivered"] = delivered
                status["failed"] = failed

            self._pending_messages.pop(message_id, None)

    async def _cleanup_timeouts(self) -> None:
        """Mark pending messages as timed out once their deadline has passed."""
        now = datetime.now(timezone.utc)
        timed_out_ids: list[str] = []

        async with self._lock:
            for message_id, pending in self._pending_messages.items():
                timeout_at = pending["timeout_at"]
                if now > timeout_at:
                    timed_out_ids.append(message_id)

            for message_id in timed_out_ids:
                status = self._delivery_status.get(message_id)
                if status:
                    status["state"] = "timed_out"
                    status["completed_at"] = now
                    if not status["failed"]:
                        status["failed"] = {"timeout": "Message delivery timed out."}

                self._pending_messages.pop(message_id, None)


# Global message bus instance
_message_bus: Optional[MessageBus] = None


def get_message_bus() -> MessageBus:
    """Get or create singleton message bus instance."""
    global _message_bus
    if _message_bus is None:
        _message_bus = MessageBus()
    return _message_bus
