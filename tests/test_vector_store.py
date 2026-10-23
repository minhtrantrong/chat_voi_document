from __future__ import annotations

from types import SimpleNamespace

import pytest
from qdrant_client.models import Distance, VectorParams

from app.chunking import Chunk
from app.vector_store import (
    VectorStoreError,
    _vector_size,
    count_points,
    delete_document,
    ensure_collection,
    health,
    search_chunks,
    upsert_chunks,
)


class BrokenClient:
    def get_collections(self):
        raise RuntimeError("down")


def _chunk(index: int, page: int = 1) -> Chunk:
    return Chunk(
        page=page,
        chunk_index=index,
        text=f"text {index}",
        char_start=index * 10,
        char_end=index * 10 + 4,
    )


def test_health_false_when_client_fails():
    assert health(client=BrokenClient()) is False


def test_vector_size_from_vectors_params():
    info = SimpleNamespace(
        config=SimpleNamespace(
            params=SimpleNamespace(vectors=VectorParams(size=8, distance=Distance.COSINE))
        )
    )
    assert _vector_size(info) == 8


def test_vector_size_from_named_vectors_dict():
    info = SimpleNamespace(
        config=SimpleNamespace(
            params=SimpleNamespace(
                vectors={"text": VectorParams(size=12, distance=Distance.COSINE)}
            )
        )
    )
    assert _vector_size(info) == 12


def test_search_error_is_wrapped(settings):
    class BrokenQuery:
        def query_points(self, **_kwargs):
            raise RuntimeError("down")

    with pytest.raises(VectorStoreError) as exc:
        search_chunks([0.1] * 8, limit=1, score_threshold=0.0, client=BrokenQuery())
    assert exc.value.code == "QDRANT_UNAVAILABLE"


def test_ensure_collection_connection_error_is_wrapped(settings):
    class BrokenEnsure:
        def collection_exists(self, _name):
            raise RuntimeError("down")

    with pytest.raises(VectorStoreError):
        ensure_collection(client=BrokenEnsure())


def test_upsert_empty_is_noop():
    upsert_chunks("d", "a.pdf", [], [])


def test_upsert_count_mismatch(settings):
    with pytest.raises(ValueError):
        upsert_chunks("d", "a.pdf", [_chunk(0)], [])


def test_upsert_wrong_dimension(settings):
    with pytest.raises(ValueError):
        upsert_chunks("d", "a.pdf", [_chunk(0)], [[0.1] * 4])


@pytest.mark.integration
def test_upsert_search_filter_delete(qdrant_settings):
    if not health():
        pytest.skip("Qdrant không chạy")
    ensure_collection()
    ensure_collection()  # idempotent

    chunks = [_chunk(0), _chunk(1, page=2)]
    vectors = [[1.0] * 8, [0.5] * 8]
    upsert_chunks("doc-1", "a.pdf", chunks, vectors, batch_size=1)
    upsert_chunks("doc-2", "b.pdf", [_chunk(0)], [[0.7] * 8])

    assert count_points() == 3

    hits = search_chunks([1.0] * 8, limit=10, score_threshold=0.0)
    assert len(hits) == 3
    assert all(hit.payload["doc_id"] in {"doc-1", "doc-2"} for hit in hits)

    filtered = search_chunks(
        [1.0] * 8,
        limit=10,
        score_threshold=0.0,
        doc_ids=["doc-1"],
    )
    assert len(filtered) == 2
    assert {hit.payload["doc_id"] for hit in filtered} == {"doc-1"}

    delete_document("doc-1")
    assert count_points() == 1
    remaining = search_chunks([1.0] * 8, limit=10, score_threshold=0.0)
    assert {hit.payload["doc_id"] for hit in remaining} == {"doc-2"}

    delete_document("doc-2")
    assert count_points() == 0
