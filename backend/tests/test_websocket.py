from fastapi.testclient import TestClient

from app.core.app import create_app
from app.websocket.manager import get_connection_manager
from app.websocket.protocol import final_message


def _reset_manager_state() -> None:
    manager = get_connection_manager()
    manager.active_connections.clear()
    manager.client_metadata.clear()
    manager.offline_queue.clear()


def test_websocket_connect_and_broadcast() -> None:
    _reset_manager_state()
    client = TestClient(create_app())

    with client.websocket_connect("/api/v1/ws/chat?session_id=session-1") as websocket:
        connected_message = websocket.receive_json()
        assert connected_message["type"] == "status"
        assert connected_message["content"] == "connected"
        assert connected_message["session_id"] == "session-1"

        websocket.send_json(
            {
                "type": "final",
                "session_id": "session-1",
                "content": "Finished synthesis",
                "agent": "orchestrator",
                "metadata": {"tokens": 128},
            }
        )

        broadcast_message = websocket.receive_json()
        assert broadcast_message["type"] == "final"
        assert broadcast_message["content"] == "Finished synthesis"
        assert broadcast_message["agent"] == "orchestrator"
        assert broadcast_message["metadata"] == {"tokens": 128}


def test_websocket_offline_queue_replays_messages_on_connect() -> None:
    _reset_manager_state()
    manager = get_connection_manager()
    client = TestClient(create_app())

    import anyio

    anyio.run(
        manager.broadcast,
        "session-queued",
        final_message("session-queued", "Queued while offline", agent="orchestrator"),
    )

    with client.websocket_connect("/api/v1/ws/chat?session_id=session-queued") as websocket:
        replayed_message = websocket.receive_json()
        assert replayed_message["type"] == "final"
        assert replayed_message["content"] == "Queued while offline"

        connected_message = websocket.receive_json()
        assert connected_message["content"] == "connected"


def test_websocket_invalid_payload_returns_error() -> None:
    _reset_manager_state()
    client = TestClient(create_app())

    with client.websocket_connect("/api/v1/ws/chat?session_id=session-err") as websocket:
        websocket.receive_json()
        websocket.send_text("not-json")

        error_payload = websocket.receive_json()
        assert error_payload["type"] == "error"
        assert error_payload["session_id"] == "session-err"
