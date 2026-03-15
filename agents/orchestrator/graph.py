"""Graph factory for the orchestrator workflow."""

from langgraph.graph import StateGraph

from agents.domain_agents.market_trend import market_trend_agent
from agents.orchestrator.router_agent import router_node
from agents.orchestrator.nodes import synthesis_node
from agents.orchestrator.state import OrchestrationState
from agents.utils.logger import get_logger

logger = get_logger(__name__)


def _route_after_router(state: OrchestrationState) -> str:
    """Route to the market trend agent only when it was selected by the router."""
    planned_agents = state.get("planned_agents") or []
    if "market_trend_agent" in planned_agents:
        return "market_trend_agent"
    return "synthesis"


def create_orchestrator_graph() -> StateGraph:
    """Create and compile the base LangGraph orchestrator."""
    graph = StateGraph(OrchestrationState)

    graph.add_node("router", router_node)
    graph.add_node("market_trend_agent", market_trend_agent)
    graph.add_node("synthesis", synthesis_node)

    # Domain agents are introduced in later issues.
    # graph.add_node("competitive_landscape_agent", competitive_landscape_agent)

    graph.add_edge("__start__", "router")
    graph.add_conditional_edges(
        "router",
        _route_after_router,
        {
            "market_trend_agent": "market_trend_agent",
            "synthesis": "synthesis",
        },
    )
    graph.add_edge("market_trend_agent", "synthesis")
    graph.add_edge("synthesis", "__end__")

    compiled = graph.compile()
    logger.info("orchestrator_graph_compiled")
    return compiled
