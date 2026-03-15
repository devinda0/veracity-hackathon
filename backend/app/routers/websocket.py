import json

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.logger import get_logger
from app.websocket.manager import get_connection_manager
from app.websocket.protocol import (
    MessageType,
    WSMessage,
    error_message,
    final_message,
    status_message,
    thinking_message,
)

router = APIRouter()
logger = get_logger(__name__)


@router.websocket("/ws/chat")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    session_id: str = Query(..., min_length=1),
) -> None:
    manager = get_connection_manager()

    try:
        await manager.connect(session_id, websocket)
        await manager.send_personal(
            websocket,
            status_message(session_id, "system", "connected"),
        )

        while True:
            raw_message = await websocket.receive_text()

            try:
                payload = json.loads(raw_message)
                message = WSMessage.model_validate(payload)
            except (json.JSONDecodeError, ValueError) as exc:
                await manager.send_personal(
                    websocket,
                    error_message(session_id, f"Invalid websocket payload: {exc}"),
                )
                continue

            logger.info(
                "websocket_received",
                session_id=session_id,
                type=message.type.value,
                agent=message.agent,
            )

            if message.type == MessageType.STATUS:
                await manager.broadcast(
                    session_id,
                    status_message(
                        session_id,
                        message.agent or "client",
                        message.content,
                    ),
                )
            elif message.type == MessageType.THINKING:
                await manager.broadcast(
                    session_id,
                    thinking_message(
                        session_id,
                        message.agent or "client",
                        message.content,
                    ),
                )
            elif message.type == MessageType.FINAL:
                await manager.broadcast(
                    session_id,
                    final_message(
                        session_id,
                        message.content,
                        agent=message.agent or "client",
                        metadata=message.metadata,
                    ),
                )
            else:
                await manager.broadcast(session_id, message.to_payload())

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as exc:
        logger.error("websocket_error", session_id=session_id, error=str(exc))
        await manager.send_personal(websocket, error_message(session_id, str(exc)))
        manager.disconnect(websocket)

