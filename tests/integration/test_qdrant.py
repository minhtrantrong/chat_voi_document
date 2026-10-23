"""Integration test Qdrant thật; tự skip nếu Qdrant không chạy."""

from __future__ import annotations

import pytest
from qdrant_client.models import Distance, VectorParams

from app.chunking import Chunk
from app.vector_store import (
    count_points,
    delete_document,
    ensure_collection,
    get_client,
    health,
    search_chunks,
    upsert_chunks,
)

pytestmark = pytest.mark.integration


def _chunk(index: int, page: int = 1) -> Chunk:
    return Chunk(page, index, f"text {index}", index * 10, index * 10 + 4)


def _vec(index: int, dim: int = 8) -> list[float]:
    vector = [0.0] * dim
    vector[index % dim] = 1.0
    return vector


def _skip_if_down() -> None:
    if not health():
        pytest.skip("Qdrant không chạy")


def test_ensure_collection_creates_and_is_idempotent(qdrant_settings):
    _skip_if_down()
    ensure_collection()
    ensure_collection()
    client = get_client()
    assert client.collection_exists(qdrant_settings.qdrant_collection)
    assert count_points() == 0


def test_dimension_mismatch_raises(qdrant_settings):
    _skip_if_down()
    client = get_client()
    client.create_collection(
        collection_name=qdrant_settings.qdrant_collection,
        vectors_config=VectorParams(size=4, distance=Distance.COSINE),
    )
    with pytest.raises(RuntimeError, match="vector size"):
        ensure_collection()


def test_upsert_idempotent_and_payload(qdrant_settings):
    _skip_if_down()
    chunks = [_chunk(0), _chunk(1, page=2)]
    vectors = [_vec(0), _vec(1)]
    upsert_chunks("doc-a", "a.pdf", chunks, vectors)
    upsert_chunks("doc-a", "a.pdf", chunks, vectors)
    assert count_points() == 2

    hits = search_chunks(_vec(0), limit=1, score_threshold=0.0)
    assert len(hits) == 1
    payload = hits[0].payload
    assert payload["doc_id"] == "doc-a"
    assert payload["file_name"] == "a.pdf"
    assert payload["chunk_index"] == 0
    assert payload["text"] == "text 0"
    assert payload["char_start"] == 0
    assert payload["char_end"] == 4


def test_search_top_k_and_threshold(qdrant_settings):
    _skip_if_down()
    chunks = [_chunk(index) for index in range(5)]
    vectors = [_vec(index) for index in range(5)]
    upsert_chunks("doc-a", "a.pdf", chunks, vectors)

    hits = search_chunks(_vec(0), limit=2, score_threshold=-1.0)
    assert len(hits) == 2
    assert hits[0].score >= hits[1].score

    only_exact = search_chunks(_vec(0), limit=10, score_threshold=0.99)
    assert len(only_exact) == 1
    assert only_exact[0].payload["chunk_index"] == 0


def test_delete_only_target_and_idempotent(qdrant_settings):
    _skip_if_down()
    upsert_chunks("doc-a", "a.pdf", [_chunk(0)], [_vec(0)])
    upsert_chunks("doc-b", "b.pdf", [_chunk(0)], [_vec(1)])
    assert count_points() == 2

    delete_document("doc-a")
    delete_document("doc-a")
    assert count_points() == 1

    remaining = search_chunks(_vec(1), limit=10, score_threshold=0.0)
    assert {hit.payload["doc_id"] for hit in remaining} == {"doc-b"}
