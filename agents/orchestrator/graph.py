"""Graph factory for the orchestrator workflow."""

from langgraph.graph import StateGraph

from agents.domain_agents.adjacent_market import adjacent_market_agent
from agents.domain_agents.competitive_landscape import competitive_landscape_agent
from agents.domain_agents.market_trend import market_trend_agent
from agents.domain_agents.pricing_packaging import pricing_packaging_agent
from agents.domain_agents.positioning_messaging import positioning_messaging_agent
from agents.domain_agents.win_loss import win_loss_agent
from agents.orchestrator.router_agent import router_node
from agents.orchestrator.nodes import synthesis_node
from agents.orchestrator.state import OrchestrationState
from agents.utils.logger import get_logger

logger = get_logger(__name__)


def _route_after_router(state: OrchestrationState) -> str:
    """Route to the first implemented agent selected by the router."""
    planned_agents = state.get("planned_agents") or []
    for agent_name in planned_agents:
        if agent_name in {
            "market_trend_agent",
            "competitive_landscape_agent",
            "win_loss_agent",
            "pricing_packaging_agent",
            "positioning_messaging_agent",
            "adjacent_market_agent",
        }:
            return agent_name
    return "synthesis"


def create_orchestrator_graph() -> StateGraph:
    """Create and compile the base LangGraph orchestrator."""
    graph = StateGraph(OrchestrationState)

    graph.add_node("router", router_node)
    graph.add_node("market_trend_agent", market_trend_agent)
    graph.add_node("competitive_landscape_agent", competitive_landscape_agent)
    graph.add_node("win_loss_agent", win_loss_agent)
    graph.add_node("pricing_packaging_agent", pricing_packaging_agent)
    graph.add_node("positioning_messaging_agent", positioning_messaging_agent)
    graph.add_node("adjacent_market_agent", adjacent_market_agent)
    graph.add_node("synthesis", synthesis_node)

    graph.add_edge("__start__", "router")
    graph.add_conditional_edges(
        "router",
        _route_after_router,
        {
            "market_trend_agent": "market_trend_agent",
            "competitive_landscape_agent": "competitive_landscape_agent",
            "win_loss_agent": "win_loss_agent",
            "pricing_packaging_agent": "pricing_packaging_agent",
            "positioning_messaging_agent": "positioning_messaging_agent",
            "adjacent_market_agent": "adjacent_market_agent",
            "synthesis": "synthesis",
        },
    )
    graph.add_edge("market_trend_agent", "synthesis")
    graph.add_edge("competitive_landscape_agent", "synthesis")
    graph.add_edge("win_loss_agent", "synthesis")
    graph.add_edge("pricing_packaging_agent", "synthesis")
    graph.add_edge("positioning_messaging_agent", "synthesis")
    graph.add_edge("adjacent_market_agent", "synthesis")
    graph.add_edge("synthesis", "__end__")

    compiled = graph.compile()
    logger.info("orchestrator_graph_compiled")
    return compiled
