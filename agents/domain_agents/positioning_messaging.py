"""Positioning and messaging domain agent implementation."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from pydantic import BaseModel, Field

from agents.orchestrator.state import OrchestrationState
from agents.tools.advertising_tool import search_meta_ads
from agents.tools.firecrawl_tool import scrape_url, search_web
from agents.utils.logger import get_logger

logger = get_logger(__name__)

_AGENT_NAME = "positioning_messaging_agent"
_AGENT_TIMEOUT_SECONDS = 60


class AudienceSegment(BaseModel):
    """Target audience segment."""

    segment_name: str
    needs: list[str]
    pain_points: list[str]
    preferred_messages: list[str]


class MessagingPillar(BaseModel):
    """Messaging pillar recommendation."""

    pillar: str
    supporting_proof_points: list[str]
    target_segments: list[str]


class BrandDifferentiationItem(BaseModel):
    """Differentiation opportunity against competitors."""

    competitor_or_archetype: str
    current_positioning: str
    differentiation_opportunity: str


class PositioningMessagingAnalysis(BaseModel):
    """Structured output for positioning and messaging analysis."""

    competitor_messaging_analysis: list[dict[str, Any]]
    value_proposition_mapping: list[dict[str, str]]
    target_audience_segmentation: list[AudienceSegment]
    messaging_pillars: list[MessagingPillar]
    brand_differentiation_analysis: list[BrandDifferentiationItem]
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


def _company_hint_from_query(query: str) -> str:
    """Derive a lightweight company hint for ad lookup."""
    tokens = [token.strip(" ,.;:()[]{}") for token in query.split() if token.strip()]
    if not tokens:
        return query
    return tokens[0]


async def _run_positioning_messaging_analysis(
    state: OrchestrationState,
) -> dict[str, Any]:
    """Gather web and ad messaging evidence and synthesize structured output."""
    from langchain_openai import ChatOpenAI  # type: ignore[import]

    llm = ChatOpenAI(model="gpt-4", temperature=0.3)
    structured_llm = llm.with_structured_output(PositioningMessagingAnalysis)

    user_query = state["user_query"]
    ad_company_hint = _company_hint_from_query(user_query)

    competitor_messaging_task = search_web(
        f"{user_query} value proposition messaging tagline"
    )
    ad_analysis_task = search_meta_ads(ad_company_hint)

    competitor_messaging, ad_analysis = await asyncio.gather(
        competitor_messaging_task,
        ad_analysis_task,
    )

    messaging_payload = _tool_payload(competitor_messaging)
    ads_payload = _tool_payload(ad_analysis)

    scrape_targets = []
    for row in messaging_payload.get("data", {}).get("results", [])[:2]:
        url = row.get("url") or row.get("link")
        if url:
            scrape_targets.append(url)

    scrape_tasks = [scrape_url(url) for url in scrape_targets]
    scrape_results = await asyncio.gather(*scrape_tasks) if scrape_tasks else []

    scraped_messages: list[dict[str, Any]] = []
    for idx, result in enumerate(scrape_results):
        payload = _tool_payload(result)
        if payload["success"]:
            content = str(payload["data"].get("content") or "")
            scraped_messages.append(
                {
                    "source_url": scrape_targets[idx],
                    "excerpt": content[:1500],
                }
            )

    prompt_payload = {
        "user_query": user_query,
        "business_context": state.get("business_context") or "None provided",
        "web_messaging": messaging_payload,
        "ad_creative_analysis": ads_payload,
        "scraped_messages": scraped_messages,
    }

    analysis_prompt = (
        "You are a product marketing strategist. Analyze competitor messaging and advertising evidence "
        "to produce structured recommendations for value proposition, target audience segmentation, "
        "messaging pillars, and brand differentiation. Use only evidence provided in the payload.\n\n"
        f"Evidence payload:\n{json.dumps(prompt_payload, default=str)}"
    )

    analysis = await structured_llm.ainvoke(
        [{"role": "user", "content": analysis_prompt}]
    )

    return {
        "analysis": analysis.model_dump(),
        "messaging_sources": [
            source
            for source in [
                messaging_payload.get("data", {}).get("source"),
                ads_payload.get("data", {}).get("source"),
            ]
            if source
        ],
        "evidence_summary": {
            "web_result_count": len(messaging_payload.get("data", {}).get("results", [])),
            "ad_count": len(ads_payload.get("data", {}).get("ads", [])),
            "scraped_pages": len(scraped_messages),
        },
        "raw_inputs": prompt_payload,
    }


async def positioning_messaging_agent(state: OrchestrationState) -> OrchestrationState:
    """Analyze positioning and messaging strategy."""
    try:
        result = await asyncio.wait_for(
            _run_positioning_messaging_analysis(state),
            timeout=_AGENT_TIMEOUT_SECONDS,
        )

        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "completed",
            "result": result,
            "error": None,
        }
        logger.info(
            "positioning_messaging_agent_completed",
            session_id=state["session_id"],
            confidence_score=result["analysis"]["confidence_score"],
            scraped_pages=result["evidence_summary"]["scraped_pages"],
        )
    except asyncio.TimeoutError:
        logger.error(
            "positioning_messaging_agent_timeout",
            session_id=state["session_id"],
            timeout_seconds=_AGENT_TIMEOUT_SECONDS,
        )
        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "failed",
            "result": None,
            "error": "Positioning/messaging analysis timed out after 60 seconds",
        }
    except Exception as exc:
        logger.error("positioning_messaging_agent_failed", error=str(exc))
        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "failed",
            "result": None,
            "error": str(exc),
        }

    return state
