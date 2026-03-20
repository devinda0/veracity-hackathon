"""Competitive landscape domain agent implementation."""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

from agents.orchestrator.state import OrchestrationState
from agents.tools.advertising_tool import search_meta_ads
from agents.tools.firecrawl_tool import scrape_url, search_web
from agents.tools.patent_tool import search_patents
from agents.utils.logger import get_logger

logger = get_logger(__name__)

_AGENT_NAME = "competitive_landscape_agent"
_AGENT_TIMEOUT_SECONDS = 60


def _to_str(v: object, default: str = "") -> str:
    return default if v is None else str(v)


def _to_str_list(v: object) -> list[str]:
    if v is None:
        return []
    if isinstance(v, list):
        return [str(i) for i in v if i is not None]
    return [str(v)]


def _clamp_int(v: object, default: int = 50) -> int:
    try:
        return max(0, min(100, int(v if v is not None else default)))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _clamp_float(v: object, default: float = 0.0) -> float:
    try:
        return max(0.0, min(100.0, float(v if v is not None else default)))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


class Competitor(BaseModel):
    """Normalized competitor record."""

    name: str = ""
    positioning: str = ""
    estimated_market_share_pct: float = 0.0
    key_strengths: list[str] = Field(default_factory=list)
    key_weaknesses: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def coerce_fields(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        data["name"] = _to_str(data.get("name"))
        data["positioning"] = _to_str(data.get("positioning"))
        data["estimated_market_share_pct"] = _clamp_float(data.get("estimated_market_share_pct"))
        data["key_strengths"] = _to_str_list(data.get("key_strengths"))
        data["key_weaknesses"] = _to_str_list(data.get("key_weaknesses"))
        return data


class FeatureComparisonRow(BaseModel):
    """Feature comparison matrix row."""

    feature: str = ""
    our_company: str = ""
    competitors: dict[str, str] = Field(default_factory=dict)

    @field_validator("competitors", mode="before")
    @classmethod
    def coerce_competitors(cls, v: object) -> dict[str, str]:
        if isinstance(v, dict):
            return {str(k): str(val) for k, val in v.items() if val is not None}
        return {}

    @model_validator(mode="before")
    @classmethod
    def coerce_fields(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        data["feature"] = _to_str(data.get("feature"))
        data["our_company"] = _to_str(data.get("our_company"))
        return data


class CompetitiveLandscapeAnalysis(BaseModel):
    """Structured output for competitive landscape analysis."""

    competitors: list[Competitor] = Field(default_factory=list)
    feature_comparison_matrix: list[FeatureComparisonRow] = Field(default_factory=list)
    pricing_and_positioning: list[dict[str, str]] = Field(default_factory=list)
    market_share_estimation_notes: str = ""
    strategic_threats: list[str] = Field(default_factory=list)
    opportunities_vs_competitors: list[str] = Field(default_factory=list)
    confidence_score: int = 50
    summary: str = ""

    @model_validator(mode="before")
    @classmethod
    def coerce_fields(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        data["market_share_estimation_notes"] = _to_str(data.get("market_share_estimation_notes"))
        data["summary"] = _to_str(data.get("summary"))
        data["confidence_score"] = _clamp_int(data.get("confidence_score"))
        data["strategic_threats"] = _to_str_list(data.get("strategic_threats"))
        data["opportunities_vs_competitors"] = _to_str_list(data.get("opportunities_vs_competitors"))

        raw_pricing = data.get("pricing_and_positioning")
        if isinstance(raw_pricing, list):
            data["pricing_and_positioning"] = [
                {str(k): str(v) for k, v in item.items() if v is not None}
                for item in raw_pricing
                if isinstance(item, dict)
            ]
        else:
            data["pricing_and_positioning"] = []

        raw_competitors = data.get("competitors")
        if not isinstance(raw_competitors, list):
            data["competitors"] = []

        raw_matrix = data.get("feature_comparison_matrix")
        if not isinstance(raw_matrix, list):
            data["feature_comparison_matrix"] = []

        return data


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

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.3)

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
    # If the query mentions a domain, scrape it directly
    domain_match = re.search(
        r"(?:https?://)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)",
        user_query,
    )
    if domain_match:
        domain = domain_match.group(0)
        direct_url = domain if domain.startswith("http") else f"https://{domain}"
        scrape_targets.append(direct_url)
    if competitor_search.success and competitor_search.data:
        for result in competitor_search.data.get("results", [])[:2]:
            url = result.get("url") or result.get("link")
            if url and url not in scrape_targets:
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

    structured_llm = llm.with_structured_output(CompetitiveLandscapeAnalysis, include_raw=True)

    raw_result = await structured_llm.ainvoke(
        [{"role": "user", "content": analysis_prompt}]
    )

    analysis: CompetitiveLandscapeAnalysis
    if raw_result.get("parsed") is not None:
        analysis = raw_result["parsed"]
    else:
        # Fallback: extract JSON from raw response text
        content = ""
        raw_msg = raw_result.get("raw")
        if raw_msg is not None and hasattr(raw_msg, "content"):
            content = raw_msg.content or ""
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            try:
                analysis = CompetitiveLandscapeAnalysis.model_validate(
                    json.loads(json_match.group())
                )
            except (json.JSONDecodeError, ValidationError):
                analysis = CompetitiveLandscapeAnalysis()
        else:
            analysis = CompetitiveLandscapeAnalysis()

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

    return {"agent_outputs": {_AGENT_NAME: state["agent_outputs"][_AGENT_NAME]}}
