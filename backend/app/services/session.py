from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import get_settings
from app.core.logger import get_logger
from app.services.embedding import EmbeddingService

try:
    import redis.asyncio as redis_asyncio
except ImportError:  # pragma: no cover - exercised when redis is not installed locally.
    redis_asyncio = None

logger = get_logger(__name__)
settings = get_settings()


@lru_cache
def _get_redis_client() -> Any | None:
    if redis_asyncio is None:
        return None

    return redis_asyncio.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )


class SessionService:
    CONTEXT_CACHE_TTL_SECONDS = 3600

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        *,
        redis_client: Any | None = None,
        embedding_service_cls: type[EmbeddingService] = EmbeddingService,
    ) -> None:
        self.db = db
        self.collection = db.sessions
        self.chat_history = db.chat_history
        self.business_context = getattr(db, "business_context", None)
        self.redis = redis_client if redis_client is not None else (None if settings.APP_ENV == "test" else _get_redis_client())
        self.embedding_service_cls = embedding_service_cls

    async def create(
        self,
        user_id: str,
        title: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        session = {
            "user_id": user_id,
            "title": title.strip(),
            "description": self._normalize_description(description),
            "created_at": now,
            "updated_at": now,
            "is_archived": False,
            "message_count": 0,
        }
        result = await self.collection.insert_one(session)
        session["_id"] = result.inserted_id
        logger.info("session_created", session_id=str(result.inserted_id), user_id=user_id)
        return session

    async def get(self, session_id: str, user_id: str) -> dict[str, Any] | None:
        object_id = self._to_object_id(session_id)
        if object_id is None:
            return None

        return await self.collection.find_one(
            {
                "_id": object_id,
                "user_id": user_id,
                "is_archived": False,
            }
        )

    async def get_with_history(
        self, session_id: str, user_id: str
    ) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
        session = await self.get(session_id, user_id)
        if session is None:
            return None, []

        messages = await self._fetch_history(
            session_id=session_id,
            user_id=user_id,
            max_history=None,
            sort_direction=1,
        )
        return session, messages

    async def get_session_context(
        self,
        session_id: str,
        user_id: str,
        *,
        query: str | None = None,
        max_history: int = 20,
        context_limit: int = 3,
    ) -> dict[str, Any]:
        session = await self.get(session_id, user_id)
        if session is None:
            raise ValueError("Session not found")

        cache_key = self._build_context_cache_key(
            session_id=session_id,
            user_id=user_id,
            query=query,
            max_history=max_history,
            context_limit=context_limit,
        )
        cached_context = await self._read_cached_context(cache_key)
        if cached_context is not None:
            return cached_context

        history_task = self._fetch_history(
            session_id=session_id,
            user_id=user_id,
            max_history=max_history,
            sort_direction=-1,
        )
        context_task = self._fetch_business_context_records(session_id=session_id, user_id=user_id)
        insights_task = self.get_recent_insights(session_id=session_id, user_id=user_id)
        relevant_context_task = self._search_business_context(
            query=query,
            session_id=session_id,
            context_limit=context_limit,
        )

        history, contexts, recent_insights, relevant_context = await asyncio.gather(
            history_task,
            context_task,
            insights_task,
            relevant_context_task,
        )

        session_context = {
            "session_id": session_id,
            "conversation_history": [self._serialize_message(message) for message in history],
            "recent_insights": recent_insights,
            "business_context": self._build_business_context(contexts, relevant_context),
        }
        session_context["formatted_context"] = self._format_for_agents(session_context)

        await self._write_cached_context(cache_key, session_context)
        return session_context

    async def list_user_sessions(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        filters = {
            "user_id": user_id,
            "is_archived": False,
        }
        sessions = (
            await self.collection.find(filters).sort("updated_at", -1).skip(skip).limit(limit).to_list(None)
        )
        total = await self.collection.count_documents(filters)
        return sessions, total

    async def update(
        self,
        session_id: str,
        user_id: str,
        title: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any] | None:
        session = await self.get(session_id, user_id)
        if session is None:
            return None

        update_data: dict[str, Any] = {
            "updated_at": datetime.now(UTC),
        }
        if title is not None:
            update_data["title"] = title.strip()
        if description is not None:
            update_data["description"] = self._normalize_description(description)

        await self.collection.update_one({"_id": session["_id"]}, {"$set": update_data})
        return {
            **session,
            **update_data,
        }

    async def delete(self, session_id: str, user_id: str) -> bool:
        session = await self.get(session_id, user_id)
        if session is None:
            return False

        result = await self.collection.update_one(
            {"_id": session["_id"]},
            {
                "$set": {
                    "is_archived": True,
                    "updated_at": datetime.now(UTC),
                }
            },
        )
        return result.modified_count > 0

    async def get_recent_insights(
        self,
        session_id: str,
        user_id: str,
        *,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        messages = await self._fetch_history(
            session_id=session_id,
            user_id=user_id,
            max_history=limit,
            sort_direction=-1,
            filters={"role": "assistant"},
        )
        messages.reverse()

        return [
            {
                "content": self._truncate_text(message.get("content", ""), limit=500),
                "timestamp": self._serialize_datetime(message.get("timestamp")),
                "artifacts": message.get("artifacts") or [],
            }
            for message in messages
        ]

    async def invalidate_context_cache(self, session_id: str) -> None:
        if self.redis is None:
            return

        try:
            cache_keys = await self._scan_cache_keys(f"session_context:{session_id}:*")
            if cache_keys:
                await self.redis.delete(*cache_keys)
        except Exception as exc:
            logger.warning("session_context_cache_invalidation_failed", session_id=session_id, error=str(exc))

    @staticmethod
    def _normalize_description(description: str | None) -> str | None:
        if description is None:
            return None

        cleaned = description.strip()
        return cleaned or None

    @staticmethod
    def _to_object_id(value: str) -> ObjectId | None:
        if not ObjectId.is_valid(value):
            return None
        return ObjectId(value)

    async def _fetch_history(
        self,
        *,
        session_id: str,
        user_id: str,
        max_history: int | None,
        sort_direction: int,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {
            "session_id": session_id,
            "user_id": user_id,
        }
        if filters:
            query.update(filters)

        cursor = self.chat_history.find(query).sort("timestamp", sort_direction)
        if max_history is not None and hasattr(cursor, "limit"):
            cursor = cursor.limit(max_history)

        documents = await cursor.to_list(None)
        if max_history is not None and not hasattr(cursor, "limit"):
            documents = documents[:max_history]

        if sort_direction < 0:
            documents.reverse()

        return documents

    async def _fetch_business_context_records(
        self,
        *,
        session_id: str,
        user_id: str,
    ) -> list[dict[str, Any]]:
        if self.business_context is None:
            return []

        return (
            await self.business_context.find(
                {
                    "session_id": session_id,
                    "user_id": user_id,
                }
            )
            .sort("created_at", -1)
            .to_list(None)
        )

    async def _search_business_context(
        self,
        *,
        query: str | None,
        session_id: str,
        context_limit: int,
    ) -> list[dict[str, Any]]:
        if query is None or not query.strip():
            return []

        try:
            service = self.embedding_service_cls(db=self.db)
            results = await service.search(
                query=query,
                session_id=session_id,
                limit=context_limit,
            )
        except Exception as exc:
            logger.warning("session_context_search_failed", session_id=session_id, error=str(exc))
            return []

        return [self._serialize_context_result(result) for result in results if isinstance(result, dict)]

    def _build_business_context(
        self,
        contexts: list[dict[str, Any]],
        relevant_context: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "documents": [
                context.get("source")
                for context in contexts
                if context.get("source_type") == "document" and context.get("source")
            ],
            "urls": [
                context.get("source")
                for context in contexts
                if context.get("source_type") == "url" and context.get("source")
            ],
            "text_snippets": [
                context.get("source")
                for context in contexts
                if context.get("source_type") == "text" and context.get("source")
            ],
            "total_items": len(contexts),
            "total_chunks": sum(int(context.get("chunk_count", 0)) for context in contexts),
            "relevant_chunks": relevant_context,
        }

    def _format_for_agents(self, session_context: dict[str, Any]) -> str | None:
        lines: list[str] = []

        history = session_context.get("conversation_history", [])
        if history:
            lines.append("Recent conversation history:")
            lines.extend(
                f"- {message.get('role', 'unknown')}: {self._truncate_text(message.get('content', ''), limit=300)}"
                for message in history
                if message.get("content")
            )

        recent_insights = session_context.get("recent_insights", [])
        if recent_insights:
            lines.append("Recent assistant insights:")
            lines.extend(
                f"- {self._truncate_text(insight.get('content', ''), limit=240)}"
                for insight in recent_insights
                if insight.get("content")
            )

        business_context = session_context.get("business_context", {})
        relevant_chunks = business_context.get("relevant_chunks", [])
        if relevant_chunks:
            lines.append("Relevant business context:")
            for chunk in relevant_chunks:
                source = chunk.get("source") or "unknown source"
                snippet = self._truncate_text(chunk.get("text", ""), limit=300)
                score = chunk.get("score")
                score_suffix = f" (score={score:.2f})" if isinstance(score, (int, float)) else ""
                lines.append(f"- [{source}] {snippet}{score_suffix}")
        elif business_context.get("total_items"):
            sources = [
                *business_context.get("documents", []),
                *business_context.get("urls", []),
                *business_context.get("text_snippets", []),
            ]
            if sources:
                lines.append("Available context sources:")
                lines.extend(f"- {source}" for source in sources[:10])

        return "\n".join(lines) if lines else None

    async def _read_cached_context(self, cache_key: str) -> dict[str, Any] | None:
        if self.redis is None:
            return None

        try:
            cached_value = await self.redis.get(cache_key)
        except Exception as exc:
            logger.warning("session_context_cache_read_failed", cache_key=cache_key, error=str(exc))
            return None

        if not cached_value:
            return None

        if isinstance(cached_value, bytes):
            cached_value = cached_value.decode("utf-8")

        try:
            return json.loads(cached_value)
        except json.JSONDecodeError:
            logger.warning("session_context_cache_decode_failed", cache_key=cache_key)
            return None

    async def _write_cached_context(self, cache_key: str, session_context: dict[str, Any]) -> None:
        if self.redis is None:
            return

        try:
            await self.redis.setex(
                cache_key,
                self.CONTEXT_CACHE_TTL_SECONDS,
                json.dumps(session_context),
            )
        except Exception as exc:
            logger.warning("session_context_cache_write_failed", cache_key=cache_key, error=str(exc))

    async def _scan_cache_keys(self, pattern: str) -> list[str]:
        scan_iter = getattr(self.redis, "scan_iter", None)
        if callable(scan_iter):
            return [
                key.decode("utf-8") if isinstance(key, bytes) else key
                async for key in scan_iter(match=pattern)
            ]

        keys_method = getattr(self.redis, "keys", None)
        if callable(keys_method):
            keys = await keys_method(pattern)
            return [key.decode("utf-8") if isinstance(key, bytes) else key for key in keys]

        return []

    @staticmethod
    def _build_context_cache_key(
        *,
        session_id: str,
        user_id: str,
        query: str | None,
        max_history: int,
        context_limit: int,
    ) -> str:
        normalized_query = (query or "").strip().lower()
        query_hash = hashlib.sha1(normalized_query.encode("utf-8")).hexdigest()[:12]
        return f"session_context:{session_id}:{user_id}:{max_history}:{context_limit}:{query_hash}"

    @classmethod
    def _serialize_message(cls, message: dict[str, Any]) -> dict[str, Any]:
        return {
            "role": message.get("role", "unknown"),
            "content": message.get("content", ""),
            "timestamp": cls._serialize_datetime(message.get("timestamp")),
        }

    @classmethod
    def _serialize_context_result(cls, result: dict[str, Any]) -> dict[str, Any]:
        return {
            "text": result.get("text", ""),
            "source": result.get("source"),
            "score": result.get("score"),
            "created_at": cls._serialize_datetime(result.get("created_at")),
            "source_type": result.get("source_type"),
            "metadata": dict(result.get("metadata") or {}),
        }

    @staticmethod
    def _serialize_datetime(value: Any) -> str | None:
        if value is None:
            return None
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)

    @staticmethod
    def _truncate_text(value: str, *, limit: int) -> str:
        if len(value) <= limit:
            return value
        return f"{value[: limit - 3].rstrip()}..."
