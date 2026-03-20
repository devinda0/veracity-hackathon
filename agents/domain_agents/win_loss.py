"""Win/loss intelligence domain agent implementation."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from pydantic import BaseModel, Field

from agents.orchestrator.state import OrchestrationState
from agents.tools.community_tool import search_hackernews, search_reddit
from agents.tools.firecrawl_tool import search_web
from agents.utils.logger import get_logger

logger = get_logger(__name__)

_AGENT_NAME = "win_loss_agent"
_AGENT_TIMEOUT_SECONDS = 60


class CustomerPreference(BaseModel):
    """Customer preference mapping row."""

    segment: str
    preference: str
    importance: int = Field(ge=1, le=10)


class CompetitiveWinRateEstimate(BaseModel):
    """Competitive win-rate estimate details."""

    estimated_win_rate_pct: float = Field(ge=0, le=100)
    rationale: str
    confidence: int = Field(ge=0, le=100)


class WinLossAnalysis(BaseModel):
    """Structured output for win/loss intelligence."""

    community_sentiment_analysis: dict[str, int]
    win_reasons: list[str]
    loss_reasons: list[str]
    customer_preference_mapping: list[CustomerPreference]
    objections_and_friction_points: list[str]
    decision_criteria: list[str]
    implementation_challenges: list[str]
    competitive_win_rate_estimation: CompetitiveWinRateEstimate
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


def _sentiment_counts(reddit_data: dict[str, Any], hn_data: dict[str, Any]) -> dict[str, int]:
    """Aggregate sentiment counts from Reddit and HN source payloads."""
    counts = {"positive": 0, "neutral": 0, "negative": 0}

    for post in reddit_data.get("posts", []):
        sentiment = post.get("sentiment", "neutral")
        if sentiment in counts:
            counts[sentiment] += 1
        for comment in post.get("top_comments", []):
            c_sentiment = comment.get("sentiment", "neutral")
            if c_sentiment in counts:
                counts[c_sentiment] += 1

    for story in hn_data.get("stories", []):
        sentiment = story.get("sentiment", "neutral")
        if sentiment in counts:
            counts[sentiment] += 1

    return counts


def _heuristic_win_rate(sentiments: dict[str, int]) -> float:
    total = sentiments["positive"] + sentiments["neutral"] + sentiments["negative"]
    if total == 0:
        return 50.0
    weighted_positive = sentiments["positive"] + (0.5 * sentiments["neutral"])
    return round((weighted_positive / total) * 100, 2)


async def _run_win_loss_analysis(state: OrchestrationState) -> dict[str, Any]:
    """Gather community/case-study signals and produce structured win/loss output."""
    from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore[import]

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.3)
    structured_llm = llm.with_structured_output(WinLossAnalysis)

    user_query = state["user_query"]

    reddit_task = search_reddit(user_query)
    hn_task = search_hackernews(f"{user_query} discussion")
    case_studies_task = search_web(f"{user_query} case study ROI implementation")

    reddit_insights, hn_insights, case_studies = await asyncio.gather(
        reddit_task,
        hn_task,
        case_studies_task,
    )

    reddit_payload = _tool_payload(reddit_insights)
    hn_payload = _tool_payload(hn_insights)
    case_payload = _tool_payload(case_studies)

    sentiment_counts = _sentiment_counts(
        reddit_payload.get("data", {}),
        hn_payload.get("data", {}),
    )
    heuristic_win_rate_pct = _heuristic_win_rate(sentiment_counts)

    prompt_payload = {
        "user_query": user_query,
        "business_context": state.get("business_context") or "None provided",
        "reddit_discussions": reddit_payload,
        "hn_discussions": hn_payload,
        "case_studies": case_payload,
        "derived_sentiment_counts": sentiment_counts,
        "heuristic_win_rate_pct": heuristic_win_rate_pct,
    }

    analysis_prompt = (
        "You are a GTM win/loss analyst. Based only on provided evidence, produce a structured analysis "
        "covering sentiment analysis, win/loss reasons, customer preferences, objection and friction points, "
        "decision criteria, implementation challenges, and a competitive win-rate estimate.\n\n"
        f"Evidence payload:\n{json.dumps(prompt_payload, default=str)}"
    )

    analysis = await structured_llm.ainvoke(
        [{"role": "user", "content": analysis_prompt}]
    )

    return {
        "analysis": analysis.model_dump(),
        "sentiment_sources": [
            source
            for source in [
                reddit_payload.get("data", {}).get("source"),
                hn_payload.get("data", {}).get("source"),
                case_payload.get("data", {}).get("source"),
            ]
            if source
        ],
        "derived_sentiment_counts": sentiment_counts,
        "heuristic_win_rate_pct": heuristic_win_rate_pct,
        "raw_inputs": prompt_payload,
    }


async def win_loss_agent(state: OrchestrationState) -> OrchestrationState:
    """Analyze win/loss reasons and customer preferences."""
    try:
        result = await asyncio.wait_for(
            _run_win_loss_analysis(state),
            timeout=_AGENT_TIMEOUT_SECONDS,
        )

        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "completed",
            "result": result,
            "error": None,
        }
        logger.info(
            "win_loss_agent_completed",
            session_id=state["session_id"],
            confidence_score=result["analysis"]["confidence_score"],
            estimated_win_rate=result["analysis"]["competitive_win_rate_estimation"]["estimated_win_rate_pct"],
        )
    except asyncio.TimeoutError:
        logger.error(
            "win_loss_agent_timeout",
            session_id=state["session_id"],
            timeout_seconds=_AGENT_TIMEOUT_SECONDS,
        )
        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "failed",
            "result": None,
            "error": "Win/loss analysis timed out after 60 seconds",
        }
    except Exception as exc:
        logger.error("win_loss_agent_failed", error=str(exc))
        state["agent_outputs"][_AGENT_NAME] = {
            "agent_name": _AGENT_NAME,
            "status": "failed",
            "result": None,
            "error": str(exc),
        }

    return {"agent_outputs": {_AGENT_NAME: state["agent_outputs"][_AGENT_NAME]}}
