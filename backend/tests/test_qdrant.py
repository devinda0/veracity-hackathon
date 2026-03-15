from types import SimpleNamespace

import pytest
from qdrant_client.models import (
    CollectionConfig,
    CollectionInfo,
    CollectionParams,
    Distance,
    FieldCondition,
    Filter,
    HnswConfig,
    MatchValue,
    OptimizersConfig,
    PayloadSchemaType,
    PointStruct,
    ScoredPoint,
    VectorParams,
)

from app.db.qdrant import QdrantClient, init_qdrant_collections, qdrant_search, qdrant_upsert_batch


class FakeQdrantClient:
    def __init__(
        self,
        existing: set[str] | None = None,
        collection_infos: dict[str, CollectionInfo] | None = None,
    ) -> None:
        self.existing = existing or set()
        self.collection_infos = collection_infos or {}
        self.created_collections: list[tuple[str, VectorParams]] = []
        self.payload_indexes: list[tuple[str, str, PayloadSchemaType]] = []
        self.upserts: list[tuple[str, list[PointStruct], bool]] = []
        self.query_calls: list[dict[str, object]] = []

    async def collection_exists(self, collection_name: str) -> bool:
        return collection_name in self.existing

    async def get_collection(self, collection_name: str) -> CollectionInfo:
        return self.collection_infos[collection_name]

    async def create_collection(self, collection_name: str, vectors_config: VectorParams) -> None:
        self.created_collections.append((collection_name, vectors_config))

    async def create_payload_index(
        self,
        collection_name: str,
        field_name: str,
        field_schema: PayloadSchemaType,
    ) -> None:
        self.payload_indexes.append((collection_name, field_name, field_schema))

    async def upsert(self, collection_name: str, points: list[PointStruct], wait: bool = True) -> None:
        self.upserts.append((collection_name, points, wait))

    async def query_points(
        self,
        collection_name: str,
        query: list[float],
        limit: int,
        query_filter: Filter | None,
        with_payload: bool,
    ) -> SimpleNamespace:
        self.query_calls.append(
            {
                "collection_name": collection_name,
                "query": query,
                "limit": limit,
                "query_filter": query_filter,
                "with_payload": with_payload,
            }
        )
        return SimpleNamespace(
            points=[
                ScoredPoint(
                    id=1,
                    version=1,
                    score=0.9,
                    payload={"session_id": "sess-1"},
                    vector=None,
                    shard_key=None,
                    order_value=None,
                )
            ]
        )


def make_collection_info(size: int = 1536, distance: Distance = Distance.COSINE) -> CollectionInfo:
    return CollectionInfo(
        status="green",
        optimizer_status="ok",
        warnings=None,
        indexed_vectors_count=0,
        points_count=0,
        segments_count=1,
        payload_schema={},
        update_queue=None,
        config=CollectionConfig(
            params=CollectionParams(
                vectors=VectorParams(size=size, distance=distance),
                shard_number=None,
                sharding_method=None,
                replication_factor=None,
                write_consistency_factor=None,
                read_fan_out_factor=None,
                read_fan_out_delay_ms=None,
                on_disk_payload=None,
                sparse_vectors=None,
            ),
            hnsw_config=HnswConfig(
                m=16,
                ef_construct=100,
                full_scan_threshold=10_000,
            ),
            optimizer_config=OptimizersConfig(
                deleted_threshold=0.2,
                vacuum_min_vector_number=1_000,
                default_segment_number=2,
                flush_interval_sec=5,
            ),
            wal_config=None,
            quantization_config=None,
            strict_mode_config=None,
            metadata=None,
        ),
    )


@pytest.mark.anyio
async def test_init_qdrant_creates_missing_collections_and_indexes() -> None:
    client = FakeQdrantClient()

    await init_qdrant_collections(client)

    assert [name for name, _ in client.created_collections] == list(QdrantClient.COLLECTIONS)
    for _, vectors_config in client.created_collections:
        assert vectors_config.size == QdrantClient.EMBEDDING_DIM
        assert vectors_config.distance == QdrantClient.DISTANCE

    assert client.payload_indexes == [
        ("business_context", "session_id", PayloadSchemaType.KEYWORD),
        ("business_context", "source", PayloadSchemaType.KEYWORD),
        ("business_context", "source_type", PayloadSchemaType.KEYWORD),
        ("business_context", "created_at", PayloadSchemaType.INTEGER),
        ("research_cache", "session_id", PayloadSchemaType.KEYWORD),
        ("research_cache", "source", PayloadSchemaType.KEYWORD),
        ("research_cache", "source_type", PayloadSchemaType.KEYWORD),
        ("research_cache", "created_at", PayloadSchemaType.INTEGER),
    ]


@pytest.mark.anyio
async def test_init_qdrant_raises_on_collection_config_conflict() -> None:
    client = FakeQdrantClient(
        existing={"business_context"},
        collection_infos={"business_context": make_collection_info(size=512)},
    )

    with pytest.raises(RuntimeError, match="expected 1536"):
        await init_qdrant_collections(client)


@pytest.mark.anyio
async def test_qdrant_upsert_batch_chunks_points() -> None:
    client = FakeQdrantClient()
    points = [
        PointStruct(id=index, vector=[0.1, 0.2, 0.3], payload={"session_id": f"s-{index}"})
        for index in range(205)
    ]

    await qdrant_upsert_batch(client, "business_context", points, batch_size=100)

    assert len(client.upserts) == 3
    assert [len(batch) for _, batch, _ in client.upserts] == [100, 100, 5]
    assert all(wait is True for _, _, wait in client.upserts)


@pytest.mark.anyio
async def test_qdrant_search_builds_filter_and_returns_points() -> None:
    client = FakeQdrantClient()
    filters = [FieldCondition(key="session_id", match=MatchValue(value="sess-1"))]

    results = await qdrant_search(
        client,
        "business_context",
        vector=[0.25, 0.5, 0.75],
        limit=5,
        filter_conditions=filters,
    )

    assert len(results) == 1
    assert client.query_calls == [
        {
            "collection_name": "business_context",
            "query": [0.25, 0.5, 0.75],
            "limit": 5,
            "query_filter": Filter(must=filters),
            "with_payload": True,
        }
    ]
