from collections.abc import Sequence
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    CollectionInfo,
    Distance,
    FieldCondition,
    Filter,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class QdrantClient:
    _instance: AsyncQdrantClient | None = None

    EMBEDDING_DIM = 768
    DISTANCE = Distance.COSINE
    COLLECTIONS: dict[str, str] = {
        "business_context": "Business context documents and metadata",
        "research_cache": "Research results from external sources",
    }
    PAYLOAD_INDEXES: dict[str, PayloadSchemaType] = {
        "session_id": PayloadSchemaType.KEYWORD,
        "source_type": PayloadSchemaType.KEYWORD,
        "created_at": PayloadSchemaType.INTEGER,
    }

    @classmethod
    async def connect(cls, url: str | None = None) -> AsyncQdrantClient:
        if cls._instance is None:
            settings = get_settings()
            client = AsyncQdrantClient(url=url or settings.QDRANT_URL, timeout=30.0)

            try:
                await client.get_collections()
            except Exception as exc:
                logger.error("qdrant_connection_failed", error=str(exc))
                await client.close()
                raise

            cls._instance = client
            logger.info("qdrant_connected", url=url or settings.QDRANT_URL)

        return cls._instance

    @classmethod
    async def disconnect(cls) -> None:
        if cls._instance is not None:
            await cls._instance.close()
            logger.info("qdrant_disconnected")

        cls._instance = None

    @classmethod
    async def get_client(cls) -> AsyncQdrantClient:
        return cls._instance or await cls.connect()


async def init_qdrant_collections(client: AsyncQdrantClient) -> None:
    for collection_name in QdrantClient.COLLECTIONS:
        try:
            if await client.collection_exists(collection_name):
                collection_info = await client.get_collection(collection_name)
                _validate_collection_config(collection_name, collection_info)
                logger.info("qdrant_collection_exists", collection=collection_name)
            else:
                await client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=QdrantClient.EMBEDDING_DIM,
                        distance=QdrantClient.DISTANCE,
                    ),
                )
                logger.info("qdrant_collection_created", collection=collection_name)

            for field_name, field_schema in QdrantClient.PAYLOAD_INDEXES.items():
                await client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field_name,
                    field_schema=field_schema,
                )

            logger.info("qdrant_payload_indexes_ready", collection=collection_name)
        except Exception as exc:
            logger.error(
                "qdrant_collection_init_failed",
                collection=collection_name,
                error=str(exc),
            )
            raise


def _validate_collection_config(collection_name: str, collection_info: CollectionInfo) -> None:
    vectors = collection_info.config.params.vectors
    vector_params = vectors if isinstance(vectors, VectorParams) else None

    if vector_params is None:
        raise RuntimeError(
            f"Collection '{collection_name}' uses unsupported vector configuration: {vectors!r}"
        )

    if vector_params.size != QdrantClient.EMBEDDING_DIM:
        raise RuntimeError(
            f"Collection '{collection_name}' has size {vector_params.size}, "
            f"expected {QdrantClient.EMBEDDING_DIM}"
        )

    if vector_params.distance != QdrantClient.DISTANCE:
        raise RuntimeError(
            f"Collection '{collection_name}' uses distance {vector_params.distance}, "
            f"expected {QdrantClient.DISTANCE}"
        )


async def qdrant_upsert_batch(
    client: AsyncQdrantClient,
    collection_name: str,
    points: Sequence[PointStruct],
    batch_size: int = 100,
) -> None:
    for start in range(0, len(points), batch_size):
        batch = list(points[start : start + batch_size])
        try:
            await client.upsert(collection_name=collection_name, points=batch, wait=True)
        except Exception as exc:
            logger.error(
                "qdrant_upsert_failed",
                collection=collection_name,
                batch_start=start,
                batch_size=len(batch),
                error=str(exc),
            )
            raise


async def qdrant_search(
    client: AsyncQdrantClient,
    collection_name: str,
    vector: Sequence[float],
    limit: int = 10,
    filter_conditions: Sequence[FieldCondition] | None = None,
) -> list[Any]:
    query_filter = Filter(must=list(filter_conditions)) if filter_conditions else None

    try:
        response = await client.query_points(
            collection_name=collection_name,
            query=list(vector),
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
        )
    except Exception as exc:
        logger.error("qdrant_search_failed", collection=collection_name, error=str(exc))
        raise

    return response.points
