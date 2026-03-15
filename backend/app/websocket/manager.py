from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from fastapi import WebSocket

from app.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class ClientMeta:
    session_id: str
    connected_at: str


class ConnectionManager:
    """Track active websocket clients per session and buffer recent messages."""

    def __init__(self, offline_queue_size: int = 50) -> None:
        self.active_connections: dict[str, dict[int, WebSocket]] = defaultdict(dict)
        self.client_metadata: dict[int, ClientMeta] = {}
        self.offline_queue: dict[str, deque[dict[str, Any]]] = defaultdict(
            lambda: deque(maxlen=offline_queue_size)
        )

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        await websocket.accept()

        client_id = id(websocket)
        self.active_connections[session_id][client_id] = websocket
        self.client_metadata[client_id] = ClientMeta(
            session_id=session_id,
            connected_at=datetime.now(UTC).isoformat(),
        )

        logger.info(
            "websocket_connected",
            session_id=session_id,
            clients=self.get_session_clients(session_id),
        )

        queued_messages = list(self.offline_queue.get(session_id, ()))
        if queued_messages:
            for message in queued_messages:
                await self.send_personal(websocket, message)
            self.offline_queue[session_id].clear()

    def disconnect(self, websocket: WebSocket) -> None:
        client_id = id(websocket)
        metadata = self.client_metadata.pop(client_id, None)
        if metadata is None:
            return

        session_connections = self.active_connections.get(metadata.session_id)
        if session_connections is not None:
            session_connections.pop(client_id, None)
            if not session_connections:
                self.active_connections.pop(metadata.session_id, None)

        logger.info(
            "websocket_disconnected",
            session_id=metadata.session_id,
            clients=self.get_session_clients(metadata.session_id),
        )

    async def broadcast(self, session_id: str, message: dict[str, Any]) -> None:
        connections = self.active_connections.get(session_id, {})
        if not connections:
            self._queue_offline_message(session_id, message)
            return

        disconnected: list[WebSocket] = []
        for connection in list(connections.values()):
            try:
                await connection.send_json(message)
            except Exception as exc:  # pragma: no cover - defensive network cleanup
                logger.warning(
                    "websocket_send_failed",
                    session_id=session_id,
                    error=str(exc),
                )
                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect(connection)
            self._queue_offline_message(session_id, message)

    async def send_personal(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        try:
            await websocket.send_json(message)
        except Exception as exc:  # pragma: no cover - defensive network cleanup
            logger.warning("websocket_send_failed", error=str(exc))
            self.disconnect(websocket)

    def get_session_clients(self, session_id: str) -> int:
        return len(self.active_connections.get(session_id, {}))

    def get_client_session(self, websocket: WebSocket) -> str | None:
        metadata = self.client_metadata.get(id(websocket))
        return metadata.session_id if metadata else None

    def _queue_offline_message(self, session_id: str, message: dict[str, Any]) -> None:
        self.offline_queue[session_id].append(message)
        logger.debug(
            "websocket_offline_message_queued",
            session_id=session_id,
            queued=len(self.offline_queue[session_id]),
        )


_manager: ConnectionManager | None = None


def get_connection_manager() -> ConnectionManager:
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager

