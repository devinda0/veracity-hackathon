"""Pricing and packaging domain agent implementation."""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any

from pydantic import BaseModel, Field

from agents.orchestrator.state import OrchestrationState
from agents.tools.firecrawl_tool import scrape_url, search_web
from agents.tools.serpapi_tool import google_search
from agents.utils.logger import get_logger

logger = get_logger(__name__)

_AGENT_NAME = "pricing_packaging_agent"
_AGENT_TIMEOUT_SECONDS = 60
_PRICE_RE = re.compile(r"(?:\$|USD\s*)(\d+(?:[\.,]\d{1,2})?)", flags=re.IGNORECASE)


class PricingTier(BaseModel):
    """Recommended packaging tier."""

    tier_name: str
    target_segment: str
    value_drivers: list[str]
    indicative_price_range: str


class ValueBasedPricingEstimate(BaseModel):
    """Value-based pricing estimate details."""

    estimated_price_anchor: str
    willingness_to_pay_signals: list[str]
    assumptions: list[str]


class RevenueOptimizationRecommendation(BaseModel):
    """Revenue optimization recommendation item."""

    recommendation: str
    impact: str
    effort: str


class PricingPackagingAnalysis(BaseModel):
    """Structured output for pricing and packaging analysis."""

    competitor_pricing_extraction: list[dict[str, Any]]
    pricing_model_analysis: list[dict[str, str]]
    value_based_pricing_estimation: ValueBasedPricingEstimate
    packaging_options_mapping: list[PricingTier]
    revenue_optimization_recommendations: list[RevenueOptimizationRecommendation]
    price_elasticity_insights: list[str]
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


def _extract_price_signals(text: str) -> list[str]:
    """Extract normalized price tokens from snippets/content."""
    matches = _PRICE_RE.findall(text or "")
    normalized = []
    for value in matches:
        normalized_value = value.replace(",", "")
        if normalized_value not in normalized:
            normalized.append(normalized_value)
    return normalized[:10]


def _extract_pricing_from_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    extracted: list[dict[str, Any]] = []
    for item in results[:10]:
        title = str(item.get("title") or "")
        link = str(item.get("url") or item.get("link") or "")
        snippet = str(item.get("snippet") or "")
        price_signals = _extract_price_signals(f"{title} {snippet}")
        if not price_signals:
            continue
        extracted.append(
            {
                "title": title,
                "link": link,
                "snippet": snippet,
                "price_signals": price_signals,
            }
        )
    return extracted


async def _run_pricing_packaging_analysis(state: OrchestrationState) -> dict[str, Any]:
    """Gather pricing evidence and produce structured pricing analysis."""
    from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore[import]

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.3)
    structured_llm = llm.with_structured_output(PricingPackagingAnalysis)

    user_query = state["user_query"]

    competitor_pricing_task = search_web(f"{user_query} pricing comparison")
    pricing_models_task = search_web(f"{user_query} pricing models alternatives cost")
    serp_google_task = google_search(f"{user_query} pricing tiers monthly annual")

    competitor_pricing, pricing_models, serp_google = await asyncio.gather(
        competitor_pricing_task,
        pricing_models_task,
        serp_google_task,
    )

    competitor_payload = _tool_payload(competitor_pricing)
    model_payload = _tool_payload(pricing_models)
    serp_payload = _tool_payload(serp_google)

    combined_results: list[dict[str, Any]] = []
    for payload in (competitor_payload, model_payload, serp_payload):
        combined_results.extend(payload.get("data", {}).get("results", []))

    extracted_pricing = _extract_pricing_from_results(combined_results)

    # Deepen evidence with page scrapes from top pricing links.
    scrape_targets = [row.get("link") for row in extracted_pricing if row.get("link")][:2]
    scrape_tasks = [scrape_url(url) for url in scrape_targets]
    scrape_results = await asyncio.gather(*scrape_tasks) if scrape_tasks else []

    scraped_pricing_signals: list[dict[str, Any]] = []
    for index, result in enumerate(scrape_results):
        payload = _tool_payload(result)
        if payload["success"]:
            content = str(payload["data"].get("content") or "")
            price_tokens = _extract_price_signals(content)
            if price_tokens:
                scraped_pricing_signals.append(
                    {
                        "source_url": scrape_targets[index],
                        "price_signals": price_tokens,
                    }
                )

    prompt_payload = {
        "user_query": user_query,
        "business_context": state.get("business_context") or "None provided",
        "competitor_pricing": competitor_payload,
        "pricing_models": model_payload,
        "serp_google": serp_payload,
        "extracted_pricing_rows": extracted_pricing,
        "scraped_pricing_signals": scraped_pricing_signals,
    }

    analysis_prompt = (
        "You are a pricing strategy analyst. Use only the supplied evidence to produce a structured "
        "pricing and packaging recommendation including competitor pricing extraction, pricing model "
        "analysis, value-based pricing, packaging options, and revenue optimization recommendations.\n\n"
        f"Evidence payload:\n{json.dumps(prompt_payload, default=str)}"
    )

    analysis = await structured_llm.ainvoke(
        [{"role": "user", "content": analysis_prompt}]
    )

    return {
        "analysis": analysis.model_dump(),
        "pricing_evidence_summary": {
            "pricing_rows_extracted": len(extracted_pricing),
            "scraped_signal_count": len(scraped_pricing_signals),
            "data_sources": len(
                [
                    source
                    for source in [
                        competitor_payload.get("data", {}).get("source"),
                        model_payload.get("data", {}).get("source"),
                        serp_payload.get("data", {}).get("source"),
                    ]
                    if source
                ]
            ),
        },
        "raw_inputs": prompt_payload,
    }


async def pricing_packaging_agent(state: OrchestrationState) -> OrchestrationState:
    """Analyze pricing strategy and packaging options."""
    try:
        result = await asyncio.wait_for(
            _run_pricing_packaging_analysis(state),
            timeout=_AGENT_TIMEOUT_SECONDS,
        )

        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "completed",
            "result": result,
            "error": None,
        }
        logger.info(
            "pricing_packaging_agent_completed",
            session_id=state["session_id"],
            confidence_score=result["analysis"]["confidence_score"],
            extracted_rows=result["pricing_evidence_summary"]["pricing_rows_extracted"],
        )
    except asyncio.TimeoutError:
        logger.error(
            "pricing_packaging_agent_timeout",
            session_id=state["session_id"],
            timeout_seconds=_AGENT_TIMEOUT_SECONDS,
        )
        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "failed",
            "result": None,
            "error": "Pricing/packaging analysis timed out after 60 seconds",
        }
    except Exception as exc:
        logger.error("pricing_packaging_agent_failed", error=str(exc))
        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "failed",
            "result": None,
            "error": str(exc),
        }

    return {"agent_outputs": {_AGENT_NAME: state["agent_outputs"][_AGENT_NAME]}}
