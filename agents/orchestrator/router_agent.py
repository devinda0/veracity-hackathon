"""Router/planner agent that determines which domain agents to invoke."""

from __future__ import annotations

import asyncio
from typing import Any, List

from pydantic import BaseModel, Field

from agents.orchestrator.state import OrchestrationState
from agents.utils.logger import get_logger

logger = get_logger(__name__)

DOMAIN_AGENTS: List[str] = [
    "market_trend_agent",
    "competitive_landscape_agent",
    "win_loss_agent",
    "pricing_packaging_agent",
    "positioning_messaging_agent",
    "adjacent_market_agent",
]

_ROUTER_TIMEOUT = 10  # seconds (per acceptance criteria)


class RouterPlan(BaseModel):
    """Structured output from the router LLM call."""

    selected_agents: List[str] = Field(
        description="List of domain agents to invoke"
    )
    reasoning: str = Field(
        description="Why these agents were selected"
    )
    priority_order: List[str] = Field(
        description="Order to execute agents"
    )
    needs_clarification: bool = Field(
        description="Does the user query need clarification"
    )
    clarification_prompt: str = Field(
        default="",
        description="Question to ask user if clarification needed",
    )


def _fallback_plan() -> RouterPlan:
    """Return a safe fallback plan selecting all agents."""
    return RouterPlan(
        selected_agents=DOMAIN_AGENTS,
        reasoning="Query complexity or LLM failure — all domains selected as fallback",
        priority_order=DOMAIN_AGENTS,
        needs_clarification=False,
    )


async def router_node(state: OrchestrationState) -> dict[str, Any]:
    """Route query to appropriate domain agents using LLM reasoning.

    Uses OpenAI function calling via with_structured_output to produce a
    validated RouterPlan. Falls back to all agents on timeout or error.
    Enforces a 10-second timeout per acceptance criteria.
    """
    # Deferred import: langchain_openai may not be installed in the editor
    # environment during development. Importing at call-time avoids top-level
    # unresolved-import warnings without affecting runtime behaviour.
    from langchain_openai import ChatOpenAI  # type: ignore[import]  # deferred: not installed in editor env

    llm = ChatOpenAI(model="gpt-4", temperature=0)
    structured_llm = llm.with_structured_output(RouterPlan)

    system_prompt = (
        "You are a query router for a market intelligence system.\n"
        "Analyze the user query and business context to determine which domain agents to invoke.\n\n"
        "Available agents:\n"
        "- market_trend_agent: Market trends, growth signals, emerging opportunities\n"
        "- competitive_landscape_agent: Competitor analysis, market share, positioning\n"
        "- win_loss_agent: Win/loss reasons, customer preferences, decision criteria\n"
        "- pricing_packaging_agent: Pricing strategy, packaging, monetization models\n"
        "- positioning_messaging_agent: Messaging, value proposition, positioning\n"
        "- adjacent_market_agent: Adjacent/neighboring markets, expansion opportunities\n\n"
        f"User query: {state['user_query']}\n"
        f"Business context: {state.get('business_context') or 'None provided'}\n\n"
        "Select the most relevant agents (1-6). "
        "If the query is ambiguous, set needs_clarification=true."
    )

    # Start with a safe fallback; overwrite if LLM succeeds.
    plan = _fallback_plan()
    valid_agents: List[str] = DOMAIN_AGENTS
    valid_priority: List[str] = DOMAIN_AGENTS

    try:
        raw_plan: RouterPlan = await asyncio.wait_for(
            structured_llm.ainvoke([{"role": "user", "content": system_prompt}]),
            timeout=_ROUTER_TIMEOUT,
        )

        # Validate that returned agent names are known to the system.
        candidates = [a for a in raw_plan.selected_agents if a in DOMAIN_AGENTS]
        if candidates:
            plan = raw_plan
            valid_agents = candidates
            valid_priority = (
                [a for a in raw_plan.priority_order if a in DOMAIN_AGENTS]
                or candidates
            )
        else:
            logger.warning(
                "router_plan_invalid_agents",
                session_id=state["session_id"],
                returned=raw_plan.selected_agents,
            )

    except asyncio.TimeoutError:
        logger.warning(
            "router_node_timeout",
            session_id=state["session_id"],
            timeout_seconds=_ROUTER_TIMEOUT,
        )
    except Exception as exc:
        logger.error("router_node_failed", error=str(exc))

    state["planned_agents"] = valid_agents
    state["trace_data"]["router_plan"] = {
        "selected_agents": valid_agents,
        "reasoning": plan.reasoning,
        "priority_order": valid_priority,
        "needs_clarification": plan.needs_clarification,
        "clarification_prompt": plan.clarification_prompt,
    }

    logger.info(
        "router_plan_created",
        session_id=state["session_id"],
        agents=valid_agents,
        needs_clarification=plan.needs_clarification,
    )

    return state
