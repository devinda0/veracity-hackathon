"""Graph factory for the orchestrator workflow."""

from langgraph.graph import StateGraph

from agents.orchestrator.nodes import router_node, synthesis_node
from agents.orchestrator.state import OrchestrationState
from agents.utils.logger import get_logger

logger = get_logger(__name__)


def create_orchestrator_graph() -> StateGraph:
    """Create and compile the base LangGraph orchestrator."""
    graph = StateGraph(OrchestrationState)

    graph.add_node("router", router_node)
    graph.add_node("synthesis", synthesis_node)

    # Domain agents are introduced in later issues.
    # graph.add_node("market_trend_agent", market_trend_agent)
    # graph.add_node("competitive_landscape_agent", competitive_landscape_agent)

    graph.add_edge("__start__", "router")

    # Issue #13 will add conditional routing to domain agents.
    # graph.add_conditional_edges(
    #     "router",
    #     route_to_agents,
    #     {agent: agent for agent in DOMAIN_AGENTS},
    # )
    # graph.add_edge([agent for agent in DOMAIN_AGENTS], "synthesis")

    graph.add_edge("router", "synthesis")
    graph.add_edge("synthesis", "__end__")

    compiled = graph.compile()
    logger.info("orchestrator_graph_compiled")
    return compiled
