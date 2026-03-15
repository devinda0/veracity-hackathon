"""Validation helpers for orchestrator inputs."""

from agents.orchestrator.state import OrchestrationState


def validate_user_query(query: str) -> bool:
    """Return True when query contains meaningful user input."""
    return bool(query and query.strip())


def validate_state(state: OrchestrationState) -> bool:
    """Minimal guard to ensure required state fields are present."""
    required_fields = ["user_query", "user_id", "session_id", "agent_outputs", "trace_data"]
    return all(field in state for field in required_fields)
