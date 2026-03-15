"""Typed state definitions for the orchestration graph."""

from typing import Any, List, Optional, TypedDict


class AgentOutput(TypedDict):
    """Output contract produced by each domain agent."""

    agent_name: str
    status: str  # pending, running, completed, failed
    result: Optional[dict[str, Any]]
    error: Optional[str]


class OrchestrationState(TypedDict):
    """State schema shared across all LangGraph nodes."""

    # Input
    user_query: str
    user_id: str
    session_id: str

    # Context
    business_context: Optional[str]
    # Runtime expectation: list of langchain_core.messages.BaseMessage objects.
    conversation_history: List[Any]

    # Processing
    planned_agents: Optional[List[str]]
    current_agent: Optional[str]

    # Outputs
    agent_outputs: dict[str, AgentOutput]
    synthesis_result: Optional[dict[str, Any]]
    artifacts: Optional[List[dict[str, Any]]]

    # Metadata
    start_time: Optional[float]
    trace_data: dict[str, Any]
    tokens_used: Optional[int]
    cost_estimate: Optional[float]
