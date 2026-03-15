"""Base orchestrator nodes used by the graph shell."""

from agents.orchestrator.state import OrchestrationState
from agents.utils.logger import get_logger

logger = get_logger(__name__)


async def router_node(state: OrchestrationState) -> OrchestrationState:
    """Router/Planner node placeholder to be implemented in Issue #13."""
    logger.info("router_node_invoked", session_id=state["session_id"])
    state["planned_agents"] = []
    return state


async def synthesis_node(state: OrchestrationState) -> OrchestrationState:
    """Synthesis node placeholder to be implemented in Issue #25."""
    logger.info("synthesis_node_invoked", session_id=state["session_id"])
    state["synthesis_result"] = {}
    return state
