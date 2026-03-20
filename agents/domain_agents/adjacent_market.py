"""Adjacent market domain agent implementation."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from pydantic import BaseModel, Field

from agents.orchestrator.state import OrchestrationState
from agents.tools.firecrawl_tool import scrape_url, search_web
from agents.tools.patent_tool import search_patents
from agents.utils.logger import get_logger

logger = get_logger(__name__)

_AGENT_NAME = "adjacent_market_agent"
_AGENT_TIMEOUT_SECONDS = 60


class ExpansionOpportunity(BaseModel):
    """Scored expansion opportunity."""

    opportunity_name: str
    opportunity_type: str = Field(
        description="One of: geographic, vertical, use_case, partnership"
    )
    rationale: str
    estimated_market_size: str
    expansion_score: int = Field(ge=0, le=100)
    recommended_entry_motion: str


class PartnershipOpportunity(BaseModel):
    """Potential partner/alliance opportunity."""

    partner_type: str
    partner_examples: list[str]
    strategic_benefit: str
    joint_go_to_market_motion: str


class AdjacentMarketAnalysis(BaseModel):
    """Structured output for adjacent market strategy analysis."""

    adjacent_market_identification: list[ExpansionOpportunity]
    geographic_expansion_candidates: list[ExpansionOpportunity]
    adjacent_use_case_extensions: list[ExpansionOpportunity]
    partnership_and_alliance_opportunities: list[PartnershipOpportunity]
    market_size_estimation_by_segment: list[dict[str, str]]
    go_to_market_recommendations: list[str]
    confidence_score: int = Field(ge=0, le=100)
    summary: str


def _tool_payload(result: Any) -> dict[str, Any]:
    if result.success:
        return {
            "success": True,
            "data": result.data or {},
            "error": None,
            "error_type": None,
        }
    return {
        "success": False,
        "data": {},
        "error": result.error,
        "error_type": str(result.error_type) if result.error_type else None,
    }


async def _run_adjacent_market_analysis(state: OrchestrationState) -> dict[str, Any]:
    """Gather adjacent-market evidence and generate scored recommendations."""
    from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore[import]

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.3)
    structured_llm = llm.with_structured_output(AdjacentMarketAnalysis)

    user_query = state["user_query"]

    adjacent_search_task = search_web(
        f"{user_query} adjacent markets expansion vertical use cases"
    )
    patent_landscape_task = search_patents(f"{user_query} related technology")

    adjacent_search, patent_landscape = await asyncio.gather(
        adjacent_search_task,
        patent_landscape_task,
    )

    adjacent_payload = _tool_payload(adjacent_search)
    patent_payload = _tool_payload(patent_landscape)

    scrape_targets = []
    for row in adjacent_payload.get("data", {}).get("results", [])[:2]:
        url = row.get("url") or row.get("link")
        if url:
            scrape_targets.append(url)

    scrape_tasks = [scrape_url(url) for url in scrape_targets]
    scrape_results = await asyncio.gather(*scrape_tasks) if scrape_tasks else []

    scraped_market_signals: list[dict[str, Any]] = []
    for idx, result in enumerate(scrape_results):
        payload = _tool_payload(result)
        if payload["success"]:
            content = str(payload["data"].get("content") or "")
            scraped_market_signals.append(
                {
                    "source_url": scrape_targets[idx],
                    "excerpt": content[:1500],
                }
            )

    prompt_payload = {
        "user_query": user_query,
        "business_context": state.get("business_context") or "None provided",
        "market_research": adjacent_payload,
        "patent_landscape": patent_payload,
        "scraped_market_signals": scraped_market_signals,
    }

    analysis_prompt = (
        "You are a growth strategy analyst. From the supplied evidence, identify adjacent market "
        "opportunities and score expansion potential. Include geographic expansion, vertical expansion, "
        "adjacent use cases, partnership opportunities, market size estimates, and GTM recommendations. "
        "Use evidence only from the payload.\n\n"
        f"Evidence payload:\n{json.dumps(prompt_payload, default=str)}"
    )

    analysis = await structured_llm.ainvoke(
        [{"role": "user", "content": analysis_prompt}]
    )

    return {
        "analysis": analysis.model_dump(),
        "research_sources": [
            source
            for source in [
                adjacent_payload.get("data", {}).get("source"),
                patent_payload.get("data", {}).get("source"),
            ]
            if source
        ],
        "evidence_summary": {
            "adjacent_results": len(adjacent_payload.get("data", {}).get("results", [])),
            "patent_count": len(patent_payload.get("data", {}).get("patents", [])),
            "scraped_pages": len(scraped_market_signals),
        },
        "raw_inputs": prompt_payload,
    }


async def adjacent_market_agent(state: OrchestrationState) -> OrchestrationState:
    """Identify adjacent market opportunities."""
    try:
        result = await asyncio.wait_for(
            _run_adjacent_market_analysis(state),
            timeout=_AGENT_TIMEOUT_SECONDS,
        )

        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "completed",
            "result": result,
            "error": None,
        }
        logger.info(
            "adjacent_market_agent_completed",
            session_id=state["session_id"],
            confidence_score=result["analysis"]["confidence_score"],
            scraped_pages=result["evidence_summary"]["scraped_pages"],
        )
    except asyncio.TimeoutError:
        logger.error(
            "adjacent_market_agent_timeout",
            session_id=state["session_id"],
            timeout_seconds=_AGENT_TIMEOUT_SECONDS,
        )
        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "failed",
            "result": None,
            "error": "Adjacent market analysis timed out after 60 seconds",
        }
    except Exception as exc:
        logger.error("adjacent_market_agent_failed", error=str(exc))
        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "failed",
            "result": None,
            "error": str(exc),
        }

    return {"agent_outputs": {_AGENT_NAME: state["agent_outputs"][_AGENT_NAME]}}
