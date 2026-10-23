from __future__ import annotations

import pytest

from app import rag as module
from app.rag import (
    NOT_FOUND,
    PreparedAnswer,
    Source,
    answer_question,
    build_context,
    finalize_answer,
    prepare_answer,
    select_hits,
    stream_answer,
)
from app.vector_store import SearchHit


def _hit(
    hit_id: str,
    *,
    doc_id: str = "doc-1",
    chunk_index: int = 0,
    score: float = 0.9,
    text: str = "Nội dung quan trọng.",
    page: int = 1,
    file_name: str = "a.pdf",
) -> SearchHit:
    return SearchHit(
        id=hit_id,
        score=score,
        payload={
            "doc_id": doc_id,
            "chunk_index": chunk_index,
            "text": text,
            "page": page,
            "file_name": file_name,
        },
    )


def test_build_context_labels_sources_and_dedupes():
    hits = [
        _hit("1", doc_id="d1", chunk_index=0, text="Alpha"),
        _hit("1", doc_id="d1", chunk_index=0, text="Alpha"),
        _hit("2", doc_id="d2", chunk_index=1, text="Beta", page=2, file_name="b.pdf"),
    ]
    context, sources = build_context(hits, max_chars=10_000)
    assert "[S1]" in context and "[S2]" in context
    assert [source.label for source in sources] == ["S1", "S2"]
    assert sources[0].file_name == "a.pdf"
    assert sources[1].page == 2


def test_build_context_skips_invalid_payload():
    hits = [
        SearchHit("1", 0.9, {"chunk_index": 0, "text": "no doc"}),
        SearchHit("2", 0.9, {"doc_id": "d", "chunk_index": -1, "text": "bad index"}),
        SearchHit("3", 0.9, {"doc_id": "d", "chunk_index": 0, "text": "   "}),
    ]
    context, sources = build_context(hits)
    assert context == ""
    assert sources == []


def test_build_context_respects_budget():
    hits = [_hit("1", text="x" * 1000)]
    context, sources = build_context(hits, max_chars=100)
    assert len(context) <= 102
    assert len(sources) == 1
    assert len(sources[0].text) < 1000


def test_select_hits_per_document_limit_and_order():
    hits = [
        _hit("1", doc_id="d1", chunk_index=0, score=0.99),
        _hit("2", doc_id="d1", chunk_index=1, score=0.98),
        _hit("3", doc_id="d2", chunk_index=0, score=0.97),
        _hit("4", doc_id="d2", chunk_index=1, score=0.96),
    ]
    selected = select_hits(hits, top_k=2, max_per_doc=1)
    assert [hit.id for hit in selected] == ["1", "3"]


def test_select_hits_dedupes_chunk():
    hits = [
        _hit("a", doc_id="d1", chunk_index=0, score=0.9),
        _hit("b", doc_id="d1", chunk_index=0, score=0.8),
    ]
    selected = select_hits(hits, top_k=10, max_per_doc=10)
    assert len(selected) == 1


def test_select_hits_invalid_args():
    with pytest.raises(ValueError):
        select_hits([], top_k=0, max_per_doc=1)
    with pytest.raises(ValueError):
        select_hits([], top_k=1, max_per_doc=0)


def test_prepare_answer_not_found(settings, monkeypatch):
    called = {"stream": False}
    monkeypatch.setattr(module, "embed_query", lambda _question: [0.1] * 8)
    monkeypatch.setattr(module, "search_chunks", lambda *_a, **_kw: [])
    monkeypatch.setattr(
        module,
        "stream_chat",
        lambda *_a, **_kw: called.__setitem__("stream", True) or iter(["x"]),
    )
    prepared = prepare_answer("Câu hỏi?", [])
    assert prepared.not_found is True
    assert prepared.messages == []
    assert prepared.sources == []
    assert called["stream"] is False


def test_prepare_answer_forwards_selected_doc_ids(settings, monkeypatch):
    captured = {}
    monkeypatch.setattr(module, "embed_query", lambda _question: [0.1] * 8)

    def fake_search(_vector, **kwargs):
        captured.update(kwargs)
        return [_hit("1")]

    monkeypatch.setattr(module, "search_chunks", fake_search)
    prepare_answer("Câu hỏi?", [], selected_doc_ids=["doc-1"])
    assert captured["doc_ids"] == ["doc-1"]


def test_prepare_answer_rejects_empty_question(settings):
    with pytest.raises(ValueError):
        prepare_answer("   ", [])


def test_prepare_answer_builds_prompt(settings, monkeypatch):
    monkeypatch.setattr(module, "embed_query", lambda _question: [0.1] * 8)
    monkeypatch.setattr(module, "search_chunks", lambda *_a, **_kw: [_hit("1")])
    history = [
        {"role": "user", "content": "trước"},
        {"role": "assistant", "content": "đáp", "sources": []},
    ]
    prepared = prepare_answer("Câu hỏi?", history)
    assert prepared.not_found is False
    assert prepared.sources
    assert prepared.messages[0]["role"] == "system"
    assert "Nội dung quan trọng" in prepared.messages[0]["content"]
    assert "Câu hỏi?" in prepared.messages[0]["content"]
    assert prepared.messages[1:] == [
        {"role": "user", "content": "trước"},
        {"role": "assistant", "content": "đáp"},
    ]


def test_stream_answer_not_found():
    assert "".join(stream_answer(PreparedAnswer(not_found=True))) == NOT_FOUND


def test_history_is_trimmed_to_setting(settings, monkeypatch):
    monkeypatch.setattr(module, "embed_query", lambda _question: [0.1] * 8)
    monkeypatch.setattr(module, "search_chunks", lambda *_a, **_kw: [_hit("1")])
    history = [
        {"role": "user" if index % 2 == 0 else "assistant", "content": str(index)}
        for index in range(20)
    ]
    prepared = prepare_answer("Câu hỏi?", history)
    assert len(prepared.messages) == 1 + settings.max_history_messages
    assert prepared.messages[-1]["content"] == "19"


def test_finalize_answer_marker_and_empty():
    source = Source("S1", "d", "a.pdf", 1, 0, "text", 0.9)
    assert finalize_answer("KHONG_TIM_THAY", [source]) == (NOT_FOUND, [], True)
    assert finalize_answer("   ", [source]) == (NOT_FOUND, [], True)
    assert finalize_answer("Câu trả lời [S1]", [source]) == (
        "Câu trả lời [S1]",
        [source],
        False,
    )


def test_answer_question_with_monkeypatched_prepare(monkeypatch):
    source = Source("S1", "d", "a.pdf", 1, 0, "text", 0.9)
    monkeypatch.setattr(
        module,
        "prepare_answer",
        lambda *_a, **_kw: PreparedAnswer(
            messages=[{"role": "system", "content": "x"}],
            sources=[source],
        ),
    )
    monkeypatch.setattr(module, "stream_answer", lambda _prepared: iter(["Trả lời"]))
    assert answer_question("q", []) == ("Trả lời", [source], False)
