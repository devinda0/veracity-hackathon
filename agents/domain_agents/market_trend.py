"""Market trend domain agent implementation."""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any

from pydantic import BaseModel, Field, field_validator

from agents.orchestrator.state import OrchestrationState
from agents.tools.firecrawl_tool import scrape_url, search_web
from agents.tools.serpapi_tool import google_news, google_trends
from agents.utils.logger import get_logger

logger = get_logger(__name__)

_AGENT_NAME = "market_trend_agent"
_AGENT_TIMEOUT_SECONDS = 60


class MarketTrendAnalysis(BaseModel):
    """Structured output for market trend analysis."""

    growth_indicators: list[str] = Field(default_factory=list)
    market_size_tam: str = ""
    emerging_opportunities: list[str] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)
    confidence_score: int = Field(default=50)
    summary: str = ""

    @field_validator("confidence_score", mode="before")
    @classmethod
    def clamp_confidence(cls, v: object) -> int:
        try:
            return max(0, min(100, int(v if v is not None else 50)))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 50

    @field_validator("growth_indicators", "emerging_opportunities", "risk_factors", mode="before")
    @classmethod
    def coerce_str_list(cls, v: object) -> list[str]:
        if v is None:
            return []
        if isinstance(v, list):
            return [str(i) for i in v if i is not None]
        return [str(v)]


def _tool_result_payload(result: Any) -> dict[str, Any]:
    """Convert ToolResult objects into a stable prompt-friendly payload."""
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


async def _run_market_trend_analysis(
    state: OrchestrationState,
) -> dict[str, Any]:
    """Gather inputs and return structured market trend analysis."""
    # Deferred import keeps editor diagnostics clean until dependencies are installed.
    from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore[import]

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.3)
    structured_llm = llm.with_structured_output(MarketTrendAnalysis)

    trend_task = google_trends(state["user_query"])
    news_task = google_news(state["user_query"])
    web_task = search_web(f"{state['user_query']} market growth trends")

    trend_results, news_results, web_results = await asyncio.gather(
        trend_task,
        news_task,
        web_task,
    )

    # If the query contains a domain/URL, scrape it directly first
    scraped_source: dict[str, Any] = {}
    domain_match = re.search(
        r"(?:https?://)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)",
        state["user_query"],
    )
    if domain_match:
        domain = domain_match.group(0)
        direct_url = domain if domain.startswith("http") else f"https://{domain}"
        scraped_result = await scrape_url(direct_url)
        scraped_source = _tool_result_payload(scraped_result)
        if scraped_source["success"]:
            scraped_source["data"] = {**scraped_source["data"], "source_url": direct_url}

    # Fall back to top search result if direct scrape failed or no domain in query
    if not scraped_source.get("success") and web_results.success and web_results.data:
        results = web_results.data.get("results", [])
        if results:
            top_link = results[0].get("url") or results[0].get("link")
            if top_link:
                scraped_result = await scrape_url(top_link)
                scraped_source = _tool_result_payload(scraped_result)
                if scraped_source["success"]:
                    scraped_source["data"] = {
                        **scraped_source["data"],
                        "source_url": top_link,
                    }

    prompt_payload = {
        "user_query": state["user_query"],
        "business_context": state.get("business_context") or "None provided",
        "trends": _tool_result_payload(trend_results),
        "news": _tool_result_payload(news_results),
        "web": _tool_result_payload(web_results),
        "scraped_source": scraped_source,
    }

    analysis_prompt = (
        "You are a market trend analyst for a competitive intelligence system. "
        "Review the supplied sources and produce a structured analysis focused on growth signals, "
        "market size/TAM, emerging opportunities, and risks. Only use evidence grounded in the inputs.\n\n"
        f"Source payload:\n{json.dumps(prompt_payload, default=str)}"
    )

    analysis = await structured_llm.ainvoke(
        [{"role": "user", "content": analysis_prompt}]
    )

    successful_sources = []
    for name, result in (
        ("serpapi_trends", trend_results),
        ("serpapi_news", news_results),
        ("firecrawl_search", web_results),
    ):
        if result.success:
            successful_sources.append(name)
    if scraped_source.get("success"):
        successful_sources.append("firecrawl_scrape")

    return {
        "analysis": analysis.model_dump(),
        "sources": successful_sources,
        "raw_inputs": prompt_payload,
    }


async def market_trend_agent(state: OrchestrationState) -> OrchestrationState:
    """Analyze market trends and growth signals."""
    try:
        result = await asyncio.wait_for(
            _run_market_trend_analysis(state),
            timeout=_AGENT_TIMEOUT_SECONDS,
        )

        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "completed",
            "result": result,
            "error": None,
        }
        logger.info(
            "market_trend_agent_completed",
            session_id=state["session_id"],
            confidence_score=result["analysis"]["confidence_score"],
        )
    except asyncio.TimeoutError:
        logger.error(
            "market_trend_agent_timeout",
            session_id=state["session_id"],
            timeout_seconds=_AGENT_TIMEOUT_SECONDS,
        )
        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "failed",
            "result": None,
            "error": "Market trend analysis timed out after 60 seconds",
        }
    except Exception as exc:
        logger.error("market_trend_agent_failed", error=str(exc))
        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "failed",
            "result": None,
            "error": str(exc),
        }

    return {"agent_outputs": {_AGENT_NAME: state["agent_outputs"][_AGENT_NAME]}}
