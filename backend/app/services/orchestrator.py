from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.logger import get_logger
from app.services.embedding import EmbeddingService
from app.services.session import SessionService
from app.websocket.manager import ConnectionManager, get_connection_manager
from app.websocket.protocol import artifact_message, error_message, final_message, status_message

logger = get_logger(__name__)


class OrchestratorService:
    """Bridge chat requests to the agent graph with a safe local fallback."""

    _EXECUTABLE_GRAPH_AGENTS = (
        "market_trend_agent",
        "competitive_landscape_agent",
    )

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        *,
        manager: ConnectionManager | None = None,
        redis_client: Any | None = None,
        embedding_service_cls: type[EmbeddingService] = EmbeddingService,
        session_service_cls: type[SessionService] = SessionService,
    ) -> None:
        self.db = db
        self.manager = manager or get_connection_manager()
        self.redis_client = redis_client
        self.embedding_service_cls = embedding_service_cls
        self.session_service_cls = session_service_cls
        self._graph: Any | None = None

    async def run(
        self,
        *,
        session_id: str,
        user_id: str,
        query: str,
        business_context: str | None = None,
        timeout_seconds: int = 300,
    ) -> dict[str, Any]:
        session_service = self.session_service_cls(
            self.db,
            redis_client=self.redis_client,
            embedding_service_cls=self.embedding_service_cls,
        )
        session = await session_service.get(session_id, user_id)
        if session is None:
            raise ValueError("Session not found")

        session_context = await session_service.get_session_context(
            session_id=session_id,
            user_id=user_id,
            query=query,
        )

        await self.manager.broadcast(
            session_id,
            status_message(
                session_id,
                "orchestrator",
                "analyzing_query",
                metadata={"query": query},
            ),
        )

        try:
            result = await asyncio.wait_for(
                self._execute(
                    session_id=session_id,
                    user_id=user_id,
                    query=query,
                    business_context=business_context,
                    session_context=session_context,
                ),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError:
            logger.error("orchestrator_timeout", session_id=session_id, timeout_seconds=timeout_seconds)
            await self.manager.broadcast(
                session_id,
                error_message(session_id, "Query processing timed out", agent="orchestrator"),
            )
            raise
        except Exception as exc:
            logger.error("orchestrator_failed", session_id=session_id, error=str(exc))
            await self.manager.broadcast(
                session_id,
                error_message(session_id, f"Query processing failed: {exc}", agent="orchestrator"),
            )
            raise

        assistant_message = {
            "session_id": session_id,
            "user_id": user_id,
            "role": "assistant",
            "content": result["synthesis"],
            "artifacts": result["artifacts"],
            "agent_trace": result["trace"],
            "timestamp": datetime.now(UTC),
            "tokens_used": result["tokens_used"],
            "cost": result["cost"],
        }
        insert_result = await self.db.chat_history.insert_one(assistant_message)
        assistant_message["_id"] = insert_result.inserted_id

        await self.db.sessions.update_one(
            {"_id": session["_id"]},
            {
                "$set": {"updated_at": assistant_message["timestamp"]},
                "$inc": {"message_count": 1},
            },
        )
        await session_service.invalidate_context_cache(session_id)

        await self.manager.broadcast(
            session_id,
            final_message(
                session_id,
                result["synthesis"],
                agent="orchestrator",
                metadata={
                    "trace": result["trace"],
                    "tokens_used": result["tokens_used"],
                    "cost": result["cost"],
                    "artifacts": result["artifacts"],
                    "message_id": str(insert_result.inserted_id),
                },
            ),
        )

        logger.info(
            "orchestrator_completed",
            session_id=session_id,
            artifacts=len(result["artifacts"]),
        )
        return {
            "message_id": str(insert_result.inserted_id),
            **result,
        }

    async def _execute(
        self,
        *,
        session_id: str,
        user_id: str,
        query: str,
        business_context: str | None,
        session_context: dict[str, Any],
    ) -> dict[str, Any]:
        await self.manager.broadcast(
            session_id,
            status_message(session_id, "orchestrator", "loading_context"),
        )
        context_docs = session_context.get("business_context", {}).get("relevant_chunks", [])

        artifacts = self._build_context_artifacts(context_docs)
        for artifact in artifacts:
            await self.manager.broadcast(
                session_id,
                artifact_message(
                    session_id,
                    artifact["type"],
                    {
                        "title": artifact["title"],
                        "data": artifact["data"],
                    },
                    agent="retrieval",
                ),
            )

        graph_state = await self._run_graph(
            session_id=session_id,
            user_id=user_id,
            query=query,
            business_context=business_context,
            session_context=session_context,
            context_docs=context_docs,
        )

        synthesis = self._coerce_synthesis(
            graph_state.get("synthesis_result"),
            query=query,
            business_context=business_context,
            context_docs=context_docs,
        )

        trace = self._build_trace(graph_state, context_docs)
        extra_artifacts = [
            artifact
            for artifact in graph_state.get("artifacts", []) or []
            if isinstance(artifact, dict)
        ]

        return {
            "synthesis": synthesis,
            "artifacts": [*artifacts, *extra_artifacts],
            "trace": trace,
            "tokens_used": self._coerce_int(graph_state.get("tokens_used")),
            "cost": self._coerce_float(graph_state.get("cost_estimate")),
        }

    async def _run_graph(
        self,
        *,
        session_id: str,
        user_id: str,
        query: str,
        business_context: str | None,
        session_context: dict[str, Any],
        context_docs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        initial_state = {
            "user_query": query,
            "user_id": user_id,
            "session_id": session_id,
            "business_context": self._merge_business_context(
                business_context,
                session_context.get("formatted_context"),
                context_docs,
            ),
            "conversation_history": list(session_context.get("conversation_history", [])[-10:]),
            "planned_agents": [],
            "current_agent": None,
            "agent_outputs": {},
            "synthesis_result": None,
            "artifacts": [],
            "start_time": datetime.now(UTC).timestamp(),
            "trace_data": {
                "context_results": len(context_docs),
                "history_messages": len(session_context.get("conversation_history", [])),
                "recent_insights": len(session_context.get("recent_insights", [])),
                "agent_statuses": {},
            },
            "tokens_used": 0,
            "cost_estimate": 0.0,
        }

        graph = await self._get_graph()
        if graph is None:
            await self.manager.broadcast(
                session_id,
                status_message(
                    session_id,
                    "orchestrator",
                    "synthesizing",
                    metadata=self._status_metadata(initial_state),
                ),
            )
            return initial_state

        try:
            if hasattr(graph, "ainvoke"):
                result = await self._invoke_graph(graph, initial_state)
            elif hasattr(graph, "astream"):
                result = await self._stream_graph_updates(graph, initial_state)
            else:
                await self.manager.broadcast(
                    session_id,
                    status_message(
                        session_id,
                        "orchestrator",
                        "synthesizing",
                        metadata=self._status_metadata(initial_state),
                    ),
                )
                result = await asyncio.to_thread(graph.invoke, initial_state)
                if isinstance(result, dict):
                    await self._emit_graph_summary_statuses(result)
        except Exception as exc:
            logger.warning("orchestrator_graph_failed", session_id=session_id, error=str(exc))
            return initial_state

        return result if isinstance(result, dict) else initial_state

    async def _stream_graph_updates(
        self,
        graph: Any,
        initial_state: dict[str, Any],
    ) -> dict[str, Any]:
        session_id = initial_state["session_id"]
        final_state = dict(initial_state)
        synthesis_started = False

        await self.manager.broadcast(
            session_id,
            status_message(
                session_id,
                "orchestrator",
                "routing_agents",
                metadata=self._status_metadata(final_state),
            ),
        )

        try:
            stream = graph.astream(initial_state, stream_mode="values")
        except TypeError as exc:
            logger.warning("orchestrator_graph_stream_mode_unsupported", error=str(exc))
            return await self._invoke_graph(graph, initial_state)

        prev_state: dict[str, Any] = dict(initial_state)
        async for state in stream:
            if not isinstance(state, dict):
                continue

            # Each chunk IS the complete current state — no manual merging needed.
            final_state = state

            # Detect router completion (planned_agents appeared).
            if state.get("planned_agents") and not prev_state.get("planned_agents"):
                await self._broadcast_router_status(final_state)

            # Detect newly completed domain agents.
            prev_outputs: dict[str, Any] = dict(prev_state.get("agent_outputs") or {})
            curr_outputs: dict[str, Any] = dict(state.get("agent_outputs") or {})
            for agent_name in list(curr_outputs):
                if not isinstance(agent_name, str):
                    continue
                if agent_name not in prev_outputs and agent_name in self._EXECUTABLE_GRAPH_AGENTS:
                    await self._broadcast_agent_completion(final_state, agent_name)
                    if not synthesis_started:
                        await self.manager.broadcast(
                            session_id,
                            status_message(
                                session_id,
                                "synthesis",
                                "running",
                                metadata=self._status_metadata(final_state),
                            ),
                        )
                        synthesis_started = True

            # Detect synthesis completion (synthesis_result appeared).
            if state.get("synthesis_result") and not prev_state.get("synthesis_result"):
                if not synthesis_started:
                    await self.manager.broadcast(
                        session_id,
                        status_message(
                            session_id,
                            "synthesis",
                            "running",
                            metadata=self._status_metadata(final_state),
                        ),
                    )
                await self.manager.broadcast(
                    session_id,
                    status_message(
                        session_id,
                        "synthesis",
                        "completed",
                        metadata=self._status_metadata(final_state),
                    ),
                )
                synthesis_started = True

            prev_state = state

        if not synthesis_started:
            await self.manager.broadcast(
                session_id,
                status_message(
                    session_id,
                    "synthesis",
                    "completed",
                    metadata=self._status_metadata(final_state),
                ),
            )

        return final_state

    async def _invoke_graph(
        self,
        graph: Any,
        initial_state: dict[str, Any],
    ) -> dict[str, Any]:
        session_id = initial_state["session_id"]
        await self.manager.broadcast(
            session_id,
            status_message(
                session_id,
                "orchestrator",
                "synthesizing",
                metadata=self._status_metadata(initial_state),
            ),
        )

        if hasattr(graph, "ainvoke"):
            result = await graph.ainvoke(initial_state)
        else:
            result = await asyncio.to_thread(graph.invoke, initial_state)

        if isinstance(result, dict):
            await self._emit_graph_summary_statuses(result)
            return result

        return initial_state

    async def _get_graph(self) -> Any | None:
        if self._graph is not None:
            return self._graph

        repo_root = Path(__file__).resolve().parents[3]
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))

        try:
            from agents.orchestrator.graph import create_orchestrator_graph
        except Exception as exc:
            logger.warning("orchestrator_graph_unavailable", error=str(exc))
            return None

        try:
            self._graph = create_orchestrator_graph()
        except Exception as exc:
            logger.warning("orchestrator_graph_compile_failed", error=str(exc))
            return None

        return self._graph

    def _build_context_artifacts(self, context_docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not context_docs:
            return []

        items = [
            {
                "text": doc.get("text", ""),
                "source": doc.get("source"),
                "score": doc.get("score"),
                "created_at": doc.get("created_at"),
            }
            for doc in context_docs
        ]
        return [
            {
                "type": "context_snippets",
                "title": "Relevant session context",
                "data": {"items": items},
            }
        ]

    def _build_trace(self, graph_state: dict[str, Any], context_docs: list[dict[str, Any]]) -> dict[str, Any]:
        trace_data = graph_state.get("trace_data")
        if isinstance(trace_data, dict):
            trace = dict(trace_data)
        else:
            trace = {}

        trace.pop("agent_statuses", None)
        trace.setdefault("planned_agents", graph_state.get("planned_agents") or [])
        trace["agents"] = self._extract_agent_trace(graph_state)
        trace["duration_ms"] = self._compute_duration_ms(graph_state.get("start_time"))
        trace.setdefault("context_results", len(context_docs))
        trace.setdefault(
            "mode",
            "graph" if graph_state.get("synthesis_result") not in (None, {}, "") else "fallback",
        )
        return trace

    def _coerce_synthesis(
        self,
        synthesis_result: Any,
        *,
        query: str,
        business_context: str | None,
        context_docs: list[dict[str, Any]],
    ) -> str:
        if isinstance(synthesis_result, str) and synthesis_result.strip():
            return synthesis_result.strip()
        if isinstance(synthesis_result, dict) and synthesis_result:
            # Prefer the formatted markdown from the frontend_response sub-dict
            frontend = synthesis_result.get("frontend_response")
            if isinstance(frontend, dict):
                md = frontend.get("markdown")
                if isinstance(md, str) and md.strip():
                    return md.strip()
            # Fall back to executive_summary or summary key
            for key in ("executive_summary", "summary"):
                val = synthesis_result.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()
            return str(synthesis_result)

        lines = [f"Research request received: {query.strip()}"]
        if business_context:
            lines.append(f"Business context: {business_context.strip()}")
        if context_docs:
            lines.append("Relevant indexed context:")
            lines.extend(
                f"- {doc.get('text', '').strip()}".rstrip()
                for doc in context_docs
                if isinstance(doc.get("text"), str) and doc.get("text", "").strip()
            )
        else:
            lines.append("No indexed business context was available for this session.")
        lines.append("The chat orchestration pipeline is connected and returned a fallback synthesis.")
        return "\n".join(lines)

    @staticmethod
    def _summarize_context(context_docs: list[dict[str, Any]]) -> str | None:
        snippets = [doc.get("text", "").strip() for doc in context_docs if isinstance(doc.get("text"), str)]
        snippets = [snippet for snippet in snippets if snippet]
        if not snippets:
            return None
        return "\n".join(f"- {snippet}" for snippet in snippets[:3])

    def _merge_business_context(
        self,
        business_context: str | None,
        formatted_session_context: str | None,
        context_docs: list[dict[str, Any]],
    ) -> str | None:
        parts: list[str] = []

        if business_context:
            parts.append(f"User-provided business context:\n{business_context.strip()}")
        if formatted_session_context:
            parts.append(f"Session memory:\n{formatted_session_context.strip()}")

        merged_context = "\n\n".join(parts).strip()
        if merged_context:
            return merged_context

        return self._summarize_context(context_docs)

    async def _broadcast_router_status(self, graph_state: dict[str, Any]) -> None:
        session_id = graph_state["session_id"]
        planned_agents = graph_state.get("planned_agents") or []
        executable_agents = self._select_executable_agents(planned_agents)

        await self.manager.broadcast(
            session_id,
            status_message(
                session_id,
                "router",
                "completed",
                metadata={
                    "planned_agents": planned_agents,
                    "trace": self._status_metadata(graph_state)["trace"],
                },
            ),
        )

        for agent_name in executable_agents:
            self._update_agent_trace(graph_state, agent_name, "pending")
            await self.manager.broadcast(
                session_id,
                status_message(
                    session_id,
                    agent_name,
                    "pending",
                    metadata=self._status_metadata(graph_state),
                ),
            )

        if executable_agents:
            current_agent = executable_agents[0]
            graph_state["current_agent"] = current_agent
            self._update_agent_trace(graph_state, current_agent, "running")
            await self.manager.broadcast(
                session_id,
                status_message(
                    session_id,
                    current_agent,
                    "running",
                    metadata=self._status_metadata(graph_state),
                ),
            )

    async def _broadcast_agent_completion(
        self,
        graph_state: dict[str, Any],
        agent_name: str,
    ) -> None:
        output = (graph_state.get("agent_outputs") or {}).get(agent_name) or {}
        status = output.get("status")
        if status not in {"pending", "running", "completed", "failed"}:
            status = "completed"

        self._update_agent_trace(
            graph_state,
            agent_name,
            status,
            error=output.get("error"),
            result=output.get("result"),
        )
        graph_state["current_agent"] = agent_name
        await self.manager.broadcast(
            graph_state["session_id"],
            status_message(
                graph_state["session_id"],
                agent_name,
                status,
                metadata=self._status_metadata(graph_state),
            ),
        )

    async def _emit_graph_summary_statuses(self, graph_state: dict[str, Any]) -> None:
        session_id = graph_state["session_id"]
        planned_agents = graph_state.get("planned_agents") or []
        executable_agents = self._select_executable_agents(planned_agents)

        if planned_agents:
            await self.manager.broadcast(
                session_id,
                status_message(
                    session_id,
                    "router",
                    "completed",
                    metadata={
                        "planned_agents": planned_agents,
                        "trace": self._status_metadata(graph_state)["trace"],
                    },
                ),
            )

        for agent_name in executable_agents:
            self._update_agent_trace(graph_state, agent_name, "pending")
            await self.manager.broadcast(
                session_id,
                status_message(
                    session_id,
                    agent_name,
                    "pending",
                    metadata=self._status_metadata(graph_state),
                ),
            )
            self._update_agent_trace(graph_state, agent_name, "running")
            await self.manager.broadcast(
                session_id,
                status_message(
                    session_id,
                    agent_name,
                    "running",
                    metadata=self._status_metadata(graph_state),
                ),
            )
            await self._broadcast_agent_completion(graph_state, agent_name)

        await self.manager.broadcast(
            session_id,
            status_message(
                session_id,
                "synthesis",
                "running",
                metadata=self._status_metadata(graph_state),
            ),
        )
        await self.manager.broadcast(
            session_id,
            status_message(
                session_id,
                "synthesis",
                "completed",
                metadata=self._status_metadata(graph_state),
            ),
        )

    def _status_metadata(self, graph_state: dict[str, Any]) -> dict[str, Any]:
        return {
            "trace": self._build_live_trace(graph_state),
            "current_agent": graph_state.get("current_agent"),
        }

    def _build_live_trace(self, graph_state: dict[str, Any]) -> dict[str, Any]:
        trace_data = graph_state.get("trace_data")
        if isinstance(trace_data, dict):
            trace = dict(trace_data)
        else:
            trace = {}

        trace.pop("agent_statuses", None)
        trace["planned_agents"] = graph_state.get("planned_agents") or []
        trace["agents"] = self._extract_agent_trace(graph_state)
        trace["duration_ms"] = self._compute_duration_ms(graph_state.get("start_time"))
        return trace

    def _extract_agent_trace(self, graph_state: dict[str, Any]) -> list[dict[str, Any]]:
        trace_data = graph_state.get("trace_data")
        tracked_agents = {}
        if isinstance(trace_data, dict):
            tracked = trace_data.get("agent_statuses")
            if isinstance(tracked, dict):
                tracked_agents = tracked

        ordered_names: list[str] = []
        for agent_name in graph_state.get("planned_agents") or []:
            if agent_name in tracked_agents and agent_name not in ordered_names:
                ordered_names.append(agent_name)

        for agent_name in tracked_agents:
            if agent_name not in ordered_names:
                ordered_names.append(agent_name)

        agent_outputs = graph_state.get("agent_outputs") or {}
        for agent_name in agent_outputs:
            if agent_name not in ordered_names:
                ordered_names.append(agent_name)

        agents: list[dict[str, Any]] = []
        for agent_name in ordered_names:
            if agent_name in tracked_agents:
                tracked = tracked_agents[agent_name]
                agents.append(
                    {
                        "name": agent_name,
                        "status": tracked.get("status", "pending"),
                        "error": tracked.get("error"),
                        "result": tracked.get("result"),
                        "duration_ms": tracked.get("duration_ms"),
                    }
                )
                continue

            output = agent_outputs.get(agent_name)
            if not isinstance(output, dict):
                continue

            agents.append(
                {
                    "name": agent_name,
                    "status": output.get("status", "pending"),
                    "error": output.get("error"),
                    "result": self._summarize_agent_result(output.get("result")),
                    "duration_ms": None,
                }
            )

        return agents

    def _update_agent_trace(
        self,
        graph_state: dict[str, Any],
        agent_name: str,
        status: str,
        *,
        error: str | None = None,
        result: Any = None,
    ) -> None:
        trace_data = graph_state.setdefault("trace_data", {})
        tracked_agents = trace_data.setdefault("agent_statuses", {})
        tracked: dict[str, Any] = dict(tracked_agents.get(agent_name) or {})
        now = datetime.now(UTC).timestamp()

        tracked["name"] = agent_name
        tracked["status"] = status

        if status == "running":
            tracked.setdefault("started_at", now)
        if status in {"completed", "failed"}:
            tracked.setdefault("started_at", now)
            tracked["completed_at"] = now
            tracked["duration_ms"] = max(int((now - tracked["started_at"]) * 1000), 0)

        if error:
            tracked["error"] = error
        if result is not None:
            tracked["result"] = self._summarize_agent_result(result)

        tracked_agents[agent_name] = tracked

    def _summarize_agent_result(self, result: Any) -> dict[str, Any] | None:
        if not isinstance(result, dict):
            return None

        analysis = result.get("analysis")
        if isinstance(analysis, dict):
            summary = analysis.get("summary")
            confidence_score = analysis.get("confidence_score")
            payload = {
                key: value
                for key, value in {
                    "summary": summary,
                    "confidence_score": confidence_score,
                }.items()
                if value not in (None, "", [])
            }
            if payload:
                return payload

        summary = result.get("summary")
        if isinstance(summary, str) and summary.strip():
            return {"summary": summary.strip()}

        return None

    def _select_executable_agents(self, planned_agents: list[str]) -> list[str]:
        for agent_name in planned_agents:
            if agent_name in self._EXECUTABLE_GRAPH_AGENTS:
                return [agent_name]
        return []

    def _merge_state(
        self,
        current_state: dict[str, Any],
        update: dict[str, Any],
    ) -> dict[str, Any]:
        merged = dict(current_state)
        for key, value in update.items():
            existing = merged.get(key)
            if isinstance(existing, dict) and isinstance(value, dict):
                merged[key] = {**existing, **value}
            else:
                merged[key] = value
        return merged

    @staticmethod
    def _compute_duration_ms(start_time: Any) -> int | None:
        if start_time is None:
            return None
        try:
            return max(int((datetime.now(UTC).timestamp() - float(start_time)) * 1000), 0)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _coerce_int(value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _coerce_float(value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
