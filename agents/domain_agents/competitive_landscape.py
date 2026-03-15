"""Competitive landscape domain agent implementation."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from pydantic import BaseModel, Field

from agents.orchestrator.state import OrchestrationState
from agents.tools.advertising_tool import search_meta_ads
from agents.tools.firecrawl_tool import scrape_url, search_web
from agents.tools.patent_tool import search_patents
from agents.utils.logger import get_logger

logger = get_logger(__name__)

_AGENT_NAME = "competitive_landscape_agent"
_AGENT_TIMEOUT_SECONDS = 60


class Competitor(BaseModel):
    """Normalized competitor record."""

    name: str
    positioning: str
    estimated_market_share_pct: float = Field(ge=0, le=100)
    key_strengths: list[str]
    key_weaknesses: list[str]


class FeatureComparisonRow(BaseModel):
    """Feature comparison matrix row."""

    feature: str
    our_company: str
    competitors: dict[str, str]


class CompetitiveLandscapeAnalysis(BaseModel):
    """Structured output for competitive landscape analysis."""

    competitors: list[Competitor]
    feature_comparison_matrix: list[FeatureComparisonRow]
    pricing_and_positioning: list[dict[str, str]]
    market_share_estimation_notes: str
    strategic_threats: list[str]
    opportunities_vs_competitors: list[str]
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


def _extract_competitor_candidates(web_data: dict[str, Any]) -> list[str]:
    """Extract likely competitor names from search titles/domains."""
    candidates: list[str] = []
    for item in web_data.get("results", [])[:10]:
        title = str(item.get("title") or "").strip()
        if title:
            candidate = title.split("-")[0].split("|")[0].strip()
            if candidate and len(candidate) > 2:
                candidates.append(candidate)

        url = str(item.get("url") or item.get("link") or "")
        if url:
            domain = url.split("//")[-1].split("/")[0].replace("www.", "")
            if domain:
                candidates.append(domain)

    deduped: list[str] = []
    for candidate in candidates:
        if candidate not in deduped:
            deduped.append(candidate)
    return deduped[:5]


async def _run_competitive_landscape_analysis(
    state: OrchestrationState,
) -> dict[str, Any]:
    """Gather web, patent, ads, and company data for analysis."""
    from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore[import]

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
    structured_llm = llm.with_structured_output(CompetitiveLandscapeAnalysis)

    user_query = state["user_query"]

    competitor_search_task = search_web(f"{user_query} competitors alternatives")
    patent_search_task = search_patents(user_query)

    competitor_search, patent_search = await asyncio.gather(
        competitor_search_task,
        patent_search_task,
    )

    competitor_candidates: list[str] = []
    if competitor_search.success and competitor_search.data:
        competitor_candidates = _extract_competitor_candidates(competitor_search.data)

    ad_targets = competitor_candidates[:3] if competitor_candidates else [user_query]
    ad_tasks = [search_meta_ads(target) for target in ad_targets]
    ad_results_raw = await asyncio.gather(*ad_tasks) if ad_tasks else []

    scrape_targets: list[str] = []
    if competitor_search.success and competitor_search.data:
        for result in competitor_search.data.get("results", [])[:2]:
            url = result.get("url") or result.get("link")
            if url:
                scrape_targets.append(url)
    scrape_tasks = [scrape_url(url) for url in scrape_targets]
    scrape_results_raw = await asyncio.gather(*scrape_tasks) if scrape_tasks else []

    ad_results = [_tool_payload(result) for result in ad_results_raw]
    scraped_company_data = []
    for idx, result in enumerate(scrape_results_raw):
        payload = _tool_payload(result)
        if payload["success"]:
            payload["data"]["source_url"] = scrape_targets[idx]
        scraped_company_data.append(payload)

    prompt_payload = {
        "user_query": user_query,
        "business_context": state.get("business_context") or "None provided",
        "competitor_search": _tool_payload(competitor_search),
        "patent_search": _tool_payload(patent_search),
        "ad_intelligence": ad_results,
        "company_data": scraped_company_data,
        "competitor_candidates": competitor_candidates,
    }

    analysis_prompt = (
        "You are a competitive intelligence analyst. Produce a structured competitive landscape "
        "analysis from the provided evidence only. Include competitor discovery and tracking, "
        "feature/capability comparison matrix, pricing and positioning analysis, market share "
        "estimation notes, strategic threats, and opportunities.\n\n"
        f"Evidence payload:\n{json.dumps(prompt_payload, default=str)}"
    )

    analysis = await structured_llm.ainvoke(
        [{"role": "user", "content": analysis_prompt}]
    )

    return {
        "analysis": analysis.model_dump(),
        "competitor_tracking": {
            "discovered_competitors": competitor_candidates,
            "tracked_count": len(competitor_candidates),
        },
        "sources": {
            "web_search_success": competitor_search.success,
            "patent_search_success": patent_search.success,
            "ads_calls": len(ad_results),
            "company_pages_scraped": len(scraped_company_data),
        },
        "raw_inputs": prompt_payload,
    }


async def competitive_landscape_agent(state: OrchestrationState) -> OrchestrationState:
    """Analyze competitive landscape and positioning."""
    try:
        result = await asyncio.wait_for(
            _run_competitive_landscape_analysis(state),
            timeout=_AGENT_TIMEOUT_SECONDS,
        )

        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "completed",
            "result": result,
            "error": None,
        }
        logger.info(
            "competitive_landscape_agent_completed",
            session_id=state["session_id"],
            confidence_score=result["analysis"]["confidence_score"],
            discovered=result["competitor_tracking"]["tracked_count"],
        )
    except asyncio.TimeoutError:
        logger.error(
            "competitive_landscape_agent_timeout",
            session_id=state["session_id"],
            timeout_seconds=_AGENT_TIMEOUT_SECONDS,
        )
        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "failed",
            "result": None,
            "error": "Competitive landscape analysis timed out after 60 seconds",
        }
    except Exception as exc:
        logger.error("competitive_landscape_agent_failed", error=str(exc))
        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "failed",
            "result": None,
            "error": str(exc),
        }

    return state
