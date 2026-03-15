from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import FieldCondition, MatchValue, PointStruct, Range

from app.core.config import get_settings
from app.core.logger import get_logger
from app.db.qdrant import QdrantClient, qdrant_search, qdrant_upsert_batch

try:
    from openai import AsyncOpenAI
except ImportError:  # pragma: no cover - exercised only when dependency is missing locally.
    AsyncOpenAI = None

logger = get_logger(__name__)
settings = get_settings()


class EmbeddingService:
    """Embed text, cache vectors in MongoDB, and index/search Qdrant."""

    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIM = 1536
    EMBEDDING_BATCH_SIZE = 100
    CACHE_COLLECTION = "embedding_cache"

    def __init__(
        self,
        db: AsyncIOMotorDatabase | None = None,
        *,
        openai_client: Any | None = None,
        qdrant_client: AsyncQdrantClient | None = None,
    ) -> None:
        self.db = db
        self._qdrant_client = qdrant_client
        self.openai_client = openai_client or self._build_openai_client()

    def _build_openai_client(self) -> Any:
        if AsyncOpenAI is None:
            raise RuntimeError("The 'openai' package is required to use EmbeddingService")
        return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        if any(not text.strip() for text in texts):
            raise ValueError("Cannot embed empty text")

        ordered_keys = [self._cache_key(text) for text in texts]
        cached_vectors: dict[str, list[float]] = {}
        missing_entries: list[tuple[str, str]] = []

        for cache_key, text in zip(ordered_keys, texts, strict=False):
            if cache_key in cached_vectors or any(existing_key == cache_key for existing_key, _ in missing_entries):
                continue

            cached_vector = await self._get_cached_embedding(cache_key)
            if cached_vector is not None:
                cached_vectors[cache_key] = cached_vector
            else:
                missing_entries.append((cache_key, text))

        for start in range(0, len(missing_entries), self.EMBEDDING_BATCH_SIZE):
            batch = missing_entries[start : start + self.EMBEDDING_BATCH_SIZE]
            batch_texts = [text for _, text in batch]
            response = await self.openai_client.embeddings.create(
                model=self.EMBEDDING_MODEL,
                input=batch_texts,
            )

            for (cache_key, text), embedding_obj in zip(batch, response.data, strict=True):
                vector = list(embedding_obj.embedding)
                cached_vectors[cache_key] = vector
                await self._store_cached_embedding(cache_key, text, vector)

            logger.info("embeddings_generated", batch_size=len(batch_texts), model=self.EMBEDDING_MODEL)

        return [cached_vectors[cache_key] for cache_key in ordered_keys]

    async def embed_chunks(
        self,
        chunks: Sequence[str],
        session_id: str,
        source: str,
        *,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
    ) -> list[PointStruct]:
        if not session_id.strip():
            raise ValueError("session_id is required")
        if not source.strip():
            raise ValueError("source is required")

        chunk_list = [chunk for chunk in chunks if chunk.strip()]
        if not chunk_list:
            return []

        payload_metadata = dict(metadata or {})
        source_type = str(payload_metadata.pop("source_type", self._infer_source_type(source)))
        created_at_ts = int((created_at or datetime.now(UTC)).timestamp())
        embeddings = await self.embed_texts(chunk_list)

        points: list[PointStruct] = []
        for index, (chunk, embedding) in enumerate(zip(chunk_list, embeddings, strict=True)):
            point_id = hashlib.sha1(
                json.dumps(
                    {
                        "session_id": session_id,
                        "source": source,
                        "chunk_index": index,
                        "text_hash": self._text_hash(chunk),
                    },
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "session_id": session_id,
                        "source": source,
                        "source_type": source_type,
                        "chunk_index": index,
                        "text": chunk,
                        "created_at": created_at_ts,
                        "metadata": payload_metadata,
                    },
                )
            )

        logger.info("chunks_embedded", chunk_count=len(points), session_id=session_id, source=source)
        return points

    async def index_chunks(
        self,
        chunks: Sequence[str],
        session_id: str,
        source: str,
        *,
        collection: str = "business_context",
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
    ) -> int:
        points = await self.embed_chunks(
            chunks,
            session_id,
            source,
            metadata=metadata,
            created_at=created_at,
        )
        if not points:
            return 0

        client = await self._get_qdrant_client()
        await qdrant_upsert_batch(client, collection, points)
        logger.info("chunks_indexed", collection=collection, chunk_count=len(points), session_id=session_id)
        return len(points)

    async def search(
        self,
        query: str,
        session_id: str,
        *,
        limit: int = 5,
        collection: str = "business_context",
        source: str | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> list[dict[str, Any]]:
        if not query.strip():
            raise ValueError("query is required")
        if not session_id.strip():
            raise ValueError("session_id is required")
        if created_after and created_before and created_after > created_before:
            raise ValueError("created_after must be earlier than created_before")

        query_vector = (await self.embed_texts([query]))[0]
        filter_conditions = [FieldCondition(key="session_id", match=MatchValue(value=session_id))]

        if source:
            filter_conditions.append(FieldCondition(key="source", match=MatchValue(value=source)))

        date_range = self._build_date_range(created_after, created_before)
        if date_range is not None:
            filter_conditions.append(FieldCondition(key="created_at", range=date_range))

        client = await self._get_qdrant_client()
        results = await qdrant_search(
            client,
            collection,
            vector=query_vector,
            limit=limit,
            filter_conditions=filter_conditions,
        )

        formatted_results = [self._format_search_result(result) for result in results]
        logger.info("semantic_search_completed", session_id=session_id, result_count=len(formatted_results))
        return formatted_results

    async def _get_qdrant_client(self) -> AsyncQdrantClient:
        return self._qdrant_client or await QdrantClient.get_client()

    async def _get_cached_embedding(self, cache_key: str) -> list[float] | None:
        if self.db is None:
            return None

        document = await self._cache_collection().find_one({"cache_key": cache_key})
        embedding = document.get("embedding") if document else None
        if embedding is None:
            return None

        logger.info("embedding_cache_hit", cache_key=cache_key)
        return list(embedding)

    async def _store_cached_embedding(self, cache_key: str, text: str, embedding: list[float]) -> None:
        if self.db is None:
            return

        now = datetime.now(UTC)
        await self._cache_collection().update_one(
            {"cache_key": cache_key},
            {
                "$set": {
                    "model": self.EMBEDDING_MODEL,
                    "text_hash": self._text_hash(text),
                    "embedding": embedding,
                    "updated_at": now,
                },
                "$setOnInsert": {
                    "created_at": now,
                },
            },
            upsert=True,
        )

    def _cache_key(self, text: str) -> str:
        return f"{self.EMBEDDING_MODEL}:{self._text_hash(text)}"

    def _cache_collection(self) -> Any:
        return self.db[self.CACHE_COLLECTION] if hasattr(self.db, "__getitem__") else getattr(self.db, self.CACHE_COLLECTION)

    @staticmethod
    def _text_hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _infer_source_type(source: str) -> str:
        prefix, _, _ = source.partition(":")
        return prefix if prefix else "unknown"

    @staticmethod
    def _build_date_range(created_after: datetime | None, created_before: datetime | None) -> Range | None:
        if created_after is None and created_before is None:
            return None
        return Range(
            gte=int(created_after.timestamp()) if created_after else None,
            lte=int(created_before.timestamp()) if created_before else None,
        )

    @staticmethod
    def _format_search_result(result: Any) -> dict[str, Any]:
        payload = dict(getattr(result, "payload", {}) or {})
        created_at = payload.get("created_at")
        created_at_iso = (
            datetime.fromtimestamp(created_at, tz=UTC).isoformat()
            if isinstance(created_at, (int, float))
            else None
        )

        return {
            "text": payload.get("text"),
            "source": payload.get("source"),
            "source_type": payload.get("source_type"),
            "score": getattr(result, "score", None),
            "chunk_index": payload.get("chunk_index"),
            "created_at": created_at_iso,
            "metadata": dict(payload.get("metadata", {})),
        }
