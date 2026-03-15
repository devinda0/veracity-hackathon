"""Synthesis agent that aggregates domain outputs into a unified response."""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any

from pydantic import BaseModel, Field

from agents.orchestrator.state import OrchestrationState
from agents.utils.logger import get_logger

logger = get_logger(__name__)

_SYNTHESIS_TIMEOUT_SECONDS = 90


class Insight(BaseModel):
    """A synthesized key insight with confidence and citations."""

    title: str
    detail: str
    confidence_score: int = Field(ge=0, le=100)
    source_citations: list[str]


class Recommendation(BaseModel):
    """A prioritized recommendation with confidence and citations."""

    action: str
    rationale: str
    priority: str
    confidence_score: int = Field(ge=0, le=100)
    source_citations: list[str]


class RiskOpportunityItem(BaseModel):
    """Risk/opportunity matrix entry."""

    item: str
    category: str
    impact: str
    likelihood: str
    confidence_score: int = Field(ge=0, le=100)
    source_citations: list[str]


class SynthesisOutput(BaseModel):
    """Structured synthesis response from the LLM."""

    executive_summary: str
    key_insights: list[Insight]
    recommended_actions: list[Recommendation]
    risk_opportunity_matrix: list[RiskOpportunityItem]
    next_steps: list[str]


def _collect_completed_agent_outputs(state: OrchestrationState) -> dict[str, Any]:
    """Collect only successful agent outputs for synthesis input."""
    completed: dict[str, Any] = {}
    for agent_name, output in state.get("agent_outputs", {}).items():
        if output.get("status") == "completed":
            completed[agent_name] = output.get("result") or {}
    return completed


def _extract_urls(value: Any, sink: list[str], limit: int = 30) -> None:
    """Recursively extract URL-like fields from nested payloads."""
    if len(sink) >= limit:
        return

    if isinstance(value, dict):
        for key, child in value.items():
            if len(sink) >= limit:
                return
            if key in {"url", "link", "source_url"} and isinstance(child, str):
                if child.startswith("http") and child not in sink:
                    sink.append(child)
            else:
                _extract_urls(child, sink, limit)
        return

    if isinstance(value, list):
        for child in value:
            if len(sink) >= limit:
                return
            _extract_urls(child, sink, limit)


def _build_source_trail(agent_summaries: dict[str, Any]) -> list[dict[str, Any]]:
    """Build source trail catalog used for citation grounding."""
    source_entries: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    for agent_name, result in agent_summaries.items():
        source_names: list[str] = []
        for key in ("sources", "research_sources", "messaging_sources", "sentiment_sources"):
            candidate = result.get(key)
            if isinstance(candidate, list):
                source_names.extend([str(item) for item in candidate if item])

        for source_name in source_names:
            dedupe_key = (agent_name, source_name, "")
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            source_entries.append(
                {
                    "source_id": f"S{len(source_entries) + 1}",
                    "agent_name": agent_name,
                    "source_name": source_name,
                    "citation": source_name,
                }
            )

        raw_inputs = result.get("raw_inputs")
        urls: list[str] = []
        _extract_urls(raw_inputs, urls)
        for url in urls:
            dedupe_key = (agent_name, "url", url)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            source_entries.append(
                {
                    "source_id": f"S{len(source_entries) + 1}",
                    "agent_name": agent_name,
                    "source_name": "url",
                    "citation": url,
                }
            )

    return source_entries


def _validate_citations(
    synthesis: SynthesisOutput,
    source_trail: list[dict[str, Any]],
) -> SynthesisOutput:
    """Filter citations to only known source identifiers."""
    valid_ids = {entry["source_id"] for entry in source_trail}

    for insight in synthesis.key_insights:
        insight.source_citations = [
            source_id for source_id in insight.source_citations if source_id in valid_ids
        ]

    for recommendation in synthesis.recommended_actions:
        recommendation.source_citations = [
            source_id
            for source_id in recommendation.source_citations
            if source_id in valid_ids
        ]

    for item in synthesis.risk_opportunity_matrix:
        item.source_citations = [
            source_id for source_id in item.source_citations if source_id in valid_ids
        ]

    return synthesis


def _score_status(score: int) -> str:
    if score >= 75:
        return "strong"
    if score >= 60:
        return "moderate"
    return "opportunity"


def _generate_artifacts(
    agent_summaries: dict[str, Any],
    synthesis: SynthesisOutput,
) -> list[dict[str, Any]]:
    """Generate visual artifacts for frontend rendering (3-5 required)."""
    agent_confidences: dict[str, int] = {}
    for agent_name, payload in agent_summaries.items():
        confidence = payload.get("analysis", {}).get("confidence_score")
        if isinstance(confidence, int):
            agent_confidences[agent_name] = confidence

    overall_score = 70
    if synthesis.recommended_actions:
        overall_score = int(
            sum(item.confidence_score for item in synthesis.recommended_actions)
            / len(synthesis.recommended_actions)
        )

    categories = {
        "market_trends": agent_confidences.get("market_trend_agent", overall_score),
        "competition": agent_confidences.get("competitive_landscape_agent", overall_score),
        "win_loss": agent_confidences.get("win_loss_agent", overall_score),
        "pricing": agent_confidences.get("pricing_packaging_agent", overall_score),
        "positioning": agent_confidences.get("positioning_messaging_agent", overall_score),
        "expansion": agent_confidences.get("adjacent_market_agent", overall_score),
    }

    scorecard_artifact = {
        "id": str(uuid.uuid4()),
        "type": "scorecard",
        "title": "Growth Intelligence Score",
        "data": {
            "overall_score": overall_score,
            "categories": {
                name: {"score": score, "status": _score_status(score)}
                for name, score in categories.items()
            },
        },
    }

    timeline_artifact = {
        "id": str(uuid.uuid4()),
        "type": "timeline",
        "title": "Strategic Insights Timeline",
        "data": {
            "events": [
                {
                    "sequence": idx + 1,
                    "event": insight.title,
                    "confidence": insight.confidence_score,
                }
                for idx, insight in enumerate(synthesis.key_insights[:5])
            ]
        },
    }

    heatmap_artifact = {
        "id": str(uuid.uuid4()),
        "type": "heatmap",
        "title": "Risk Opportunity Heatmap",
        "data": {
            "dimensions": ["Impact", "Likelihood", "Confidence"],
            "items": [
                {
                    "item": matrix_item.item,
                    "category": matrix_item.category,
                    "impact": matrix_item.impact,
                    "likelihood": matrix_item.likelihood,
                    "confidence": matrix_item.confidence_score,
                }
                for matrix_item in synthesis.risk_opportunity_matrix[:10]
            ],
        },
    }

    recommendation_artifact = {
        "id": str(uuid.uuid4()),
        "type": "recommendation_board",
        "title": "Recommended Action Board",
        "data": {
            "actions": [
                {
                    "action": rec.action,
                    "priority": rec.priority,
                    "confidence": rec.confidence_score,
                    "rationale": rec.rationale,
                }
                for rec in synthesis.recommended_actions[:5]
            ]
        },
    }

    return [
        scorecard_artifact,
        timeline_artifact,
        heatmap_artifact,
        recommendation_artifact,
    ]


def _format_frontend_response(
    synthesis: SynthesisOutput,
    source_trail: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Format synthesis output for frontend consumption."""
    markdown_lines = [
        "## Executive Summary",
        synthesis.executive_summary,
        "",
        "## Key Insights",
    ]
    for insight in synthesis.key_insights[:5]:
        markdown_lines.append(
            f"- {insight.title} (confidence: {insight.confidence_score})"
        )
    markdown_lines.append("")
    markdown_lines.append("## Recommended Actions")
    for rec in synthesis.recommended_actions[:5]:
        markdown_lines.append(
            f"- {rec.action} [{rec.priority}] (confidence: {rec.confidence_score})"
        )

    return {
        "executive_summary": synthesis.executive_summary,
        "insight_cards": [insight.model_dump() for insight in synthesis.key_insights],
        "recommendation_cards": [
            recommendation.model_dump() for recommendation in synthesis.recommended_actions
        ],
        "risk_opportunity_matrix": [
            row.model_dump() for row in synthesis.risk_opportunity_matrix
        ],
        "next_steps": synthesis.next_steps,
        "source_trail": source_trail,
        "artifacts": artifacts,
        "markdown": "\n".join(markdown_lines),
    }


async def synthesis_agent(state: OrchestrationState) -> OrchestrationState:
    """Synthesize all domain outputs into a coherent final response."""
    try:
        from langchain_openai import ChatOpenAI  # type: ignore[import]

        agent_summaries = _collect_completed_agent_outputs(state)
        source_trail = _build_source_trail(agent_summaries)

        llm = ChatOpenAI(model="gpt-4", temperature=0.2)
        structured_llm = llm.with_structured_output(SynthesisOutput)

        synthesis_prompt = (
            "You are a synthesis expert for growth intelligence reports. Aggregate the provided agent "
            "outputs into one coherent strategic narrative. For insights, recommendations, and matrix items, "
            "include source_citations using the provided source_id values.\n\n"
            "Requirements:\n"
            "1) Executive summary (2-3 sentences)\n"
            "2) Top key insights with confidence\n"
            "3) Recommended actions (3-5) with confidence\n"
            "4) Risk/opportunity matrix\n"
            "5) Next steps\n\n"
            f"Business context: {state.get('business_context') or 'None provided'}\n"
            f"Agent summaries: {json.dumps(agent_summaries, default=str)}\n"
            f"Source trail: {json.dumps(source_trail, default=str)}"
        )

        synthesis = await asyncio.wait_for(
            structured_llm.ainvoke([{"role": "user", "content": synthesis_prompt}]),
            timeout=_SYNTHESIS_TIMEOUT_SECONDS,
        )
        synthesis = _validate_citations(synthesis, source_trail)

        artifacts = _generate_artifacts(agent_summaries, synthesis)
        frontend_response = _format_frontend_response(synthesis, source_trail, artifacts)

        state["synthesis_result"] = {
            "executive_summary": synthesis.executive_summary,
            "key_insights": [item.model_dump() for item in synthesis.key_insights],
            "recommendations": [item.model_dump() for item in synthesis.recommended_actions],
            "risk_opportunity_matrix": [
                item.model_dump() for item in synthesis.risk_opportunity_matrix
            ],
            "next_steps": synthesis.next_steps,
            "frontend_response": frontend_response,
            "source_trail": source_trail,
        }
        state["artifacts"] = artifacts

        logger.info(
            "synthesis_completed",
            session_id=state["session_id"],
            completed_agents=len(agent_summaries),
            artifact_count=len(artifacts),
        )

    except Exception as exc:
        logger.error("synthesis_agent_failed", error=str(exc))
        state["synthesis_result"] = {
            "error": str(exc),
            "executive_summary": "Synthesis failed.",
            "key_insights": [],
            "recommendations": [],
            "risk_opportunity_matrix": [],
            "next_steps": [],
            "source_trail": [],
            "frontend_response": {
                "executive_summary": "Synthesis failed.",
                "insight_cards": [],
                "recommendation_cards": [],
                "risk_opportunity_matrix": [],
                "next_steps": [],
                "source_trail": [],
                "artifacts": [],
                "markdown": "## Executive Summary\nSynthesis failed.",
            },
        }
        state["artifacts"] = []

    return state
