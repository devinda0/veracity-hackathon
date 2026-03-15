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

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        *,
        manager: ConnectionManager | None = None,
        embedding_service_cls: type[EmbeddingService] = EmbeddingService,
    ) -> None:
        self.db = db
        self.manager = manager or get_connection_manager()
        self.embedding_service_cls = embedding_service_cls
        self._graph: Any | None = None

    async def run(
        self,
        *,
        session_id: str,
        user_id: str,
        query: str,
        business_context: str | None = None,
        timeout_seconds: int = 30,
    ) -> dict[str, Any]:
        session, history = await SessionService(self.db).get_with_history(session_id, user_id)
        if session is None:
            raise ValueError("Session not found")

        await self.manager.broadcast(
            session_id,
            status_message(session_id, "orchestrator", "analyzing_query"),
        )

        try:
            result = await asyncio.wait_for(
                self._execute(
                    session_id=session_id,
                    user_id=user_id,
                    query=query,
                    business_context=business_context,
                    history=history,
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
        history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        await self.manager.broadcast(
            session_id,
            status_message(session_id, "orchestrator", "loading_context"),
        )
        context_docs = await self._load_context(query=query, session_id=session_id)

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

        await self.manager.broadcast(
            session_id,
            status_message(session_id, "orchestrator", "synthesizing"),
        )

        graph_state = await self._run_graph(
            session_id=session_id,
            user_id=user_id,
            query=query,
            business_context=business_context,
            history=history,
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

    async def _load_context(self, *, query: str, session_id: str) -> list[dict[str, Any]]:
        try:
            service = self.embedding_service_cls(db=self.db)
            results = await service.search(query=query, session_id=session_id, limit=3)
            return [result for result in results if isinstance(result, dict)]
        except Exception as exc:
            logger.warning("orchestrator_context_unavailable", session_id=session_id, error=str(exc))
            return []

    async def _run_graph(
        self,
        *,
        session_id: str,
        user_id: str,
        query: str,
        business_context: str | None,
        history: list[dict[str, Any]],
        context_docs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        initial_state = {
            "user_query": query,
            "user_id": user_id,
            "session_id": session_id,
            "business_context": business_context or self._summarize_context(context_docs),
            "conversation_history": [
                {
                    "role": message.get("role", "assistant"),
                    "content": message.get("content", ""),
                    "timestamp": message.get("timestamp").isoformat()
                    if hasattr(message.get("timestamp"), "isoformat")
                    else message.get("timestamp"),
                }
                for message in history[-10:]
            ],
            "planned_agents": [],
            "current_agent": None,
            "agent_outputs": {},
            "synthesis_result": None,
            "artifacts": [],
            "start_time": datetime.now(UTC).timestamp(),
            "trace_data": {"context_results": len(context_docs)},
            "tokens_used": 0,
            "cost_estimate": 0.0,
        }

        graph = await self._get_graph()
        if graph is None:
            return initial_state

        try:
            if hasattr(graph, "ainvoke"):
                result = await graph.ainvoke(initial_state)
            else:
                result = await asyncio.to_thread(graph.invoke, initial_state)
        except Exception as exc:
            logger.warning("orchestrator_graph_failed", session_id=session_id, error=str(exc))
            return initial_state

        return result if isinstance(result, dict) else initial_state

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

        trace.setdefault("planned_agents", graph_state.get("planned_agents") or [])
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
            if isinstance(synthesis_result.get("summary"), str) and synthesis_result["summary"].strip():
                return synthesis_result["summary"].strip()
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
