"""Typed state definitions for the orchestration graph."""

from typing import Annotated, Any, List, Optional, TypedDict


def _merge_dicts(a: dict, b: dict) -> dict:
    """Reducer: merge two dicts, with b's values taking precedence."""
    return {**a, **b}


def _add_ints(a: Optional[int], b: Optional[int]) -> int:
    return (a or 0) + (b or 0)


def _add_floats(a: Optional[float], b: Optional[float]) -> float:
    return (a or 0.0) + (b or 0.0)


class AgentOutput(TypedDict):
    """Output contract produced by each domain agent."""

    agent_name: str
    status: str  # pending, running, completed, failed
    result: Optional[dict[str, Any]]
    error: Optional[str]


class OrchestrationState(TypedDict):
    """State schema shared across all LangGraph nodes."""

    # Input (immutable — single writer: router)
    user_query: str
    user_id: str
    session_id: str

    # Context
    business_context: Optional[str]
    conversation_history: List[Any]

    # Processing
    planned_agents: Optional[List[str]]
    current_agent: Optional[str]

    # Outputs — annotated so parallel agents can merge without conflict
    agent_outputs: Annotated[dict[str, AgentOutput], _merge_dicts]
    synthesis_result: Optional[dict[str, Any]]
    artifacts: Optional[List[dict[str, Any]]]

    # Metadata — accumulate across parallel agents
    start_time: Optional[float]
    trace_data: Annotated[dict[str, Any], _merge_dicts]
    tokens_used: Annotated[Optional[int], _add_ints]
    cost_estimate: Annotated[Optional[float], _add_floats]
