from __future__ import annotations

import pytest

from app.rag import select_hits
from app.vector_store import SearchHit


def _hit(hit_id: str, doc_id: str | None, chunk: int, score: float) -> SearchHit:
    payload = {"chunk_index": chunk, "text": "x"}
    if doc_id is not None:
        payload["doc_id"] = doc_id
    return SearchHit(hit_id, score, payload)


def test_cap_per_doc():
    hits = [_hit(str(i), "A", i, 1.0 - i / 100) for i in range(6)]
    selected = select_hits(hits, top_k=8, max_per_doc=2)
    assert len(selected) == 2
    assert [hit.id for hit in selected] == ["0", "1"]


def test_top_k_limit():
    hits = [_hit(str(i), f"D{i}", 0, 1.0 - i / 100) for i in range(5)]
    assert len(select_hits(hits, top_k=3, max_per_doc=4)) == 3


def test_dedupe_point_id_and_doc_chunk():
    hits = [
        _hit("same", "A", 0, 0.9),
        _hit("same", "A", 0, 0.8),
        _hit("other", "A", 0, 0.7),
    ]
    assert len(select_hits(hits, top_k=10, max_per_doc=10)) == 1


def test_skip_missing_doc_id_and_bad_index():
    hits = [
        _hit("1", None, 0, 0.9),
        SearchHit("2", 0.8, {"doc_id": "A", "chunk_index": "bad"}),
        _hit("3", "A", -1, 0.7),
        _hit("4", "A", 0, 0.6),
    ]
    assert [hit.id for hit in select_hits(hits, top_k=10, max_per_doc=10)] == ["4"]


def test_invalid_params_raise():
    with pytest.raises(ValueError):
        select_hits([], top_k=0, max_per_doc=1)
    with pytest.raises(ValueError):
        select_hits([], top_k=1, max_per_doc=0)


def test_multiple_docs_selected():
    hits = [
        _hit("a1", "A", 0, 0.99),
        _hit("a2", "A", 1, 0.98),
        _hit("b1", "B", 0, 0.90),
        _hit("c1", "C", 0, 0.80),
    ]
    selected = select_hits(hits, top_k=3, max_per_doc=1)
    assert {hit.payload["doc_id"] for hit in selected} == {"A", "B", "C"}


def test_single_doc_returns_at_most_cap():
    hits = [_hit(str(i), "A", i, 1.0) for i in range(5)]
    assert len(select_hits(hits, top_k=10, max_per_doc=2)) == 2
