from __future__ import annotations

import inspect

from app.rag import Source
from app.ui import (
    _as_dict,
    _source_order,
    dedupe_sources,
    md_escape,
    render_sources,
    source_to_dict,
    truncate_snippet,
)


def test_as_dict_from_dataclass():
    source = Source("S1", "d", "a.pdf", 2, 3, "text", 0.9)
    assert _as_dict(source)["label"] == "S1"
    assert _as_dict(source)["page"] == 2


def test_as_dict_from_dict():
    value = {"label": "S1", "file_name": "a.pdf"}
    assert _as_dict(value) is value


def test_as_dict_missing_fields_defaults():
    value = _as_dict(object())
    assert value["label"] == "?"
    assert value["file_name"] == "tài liệu"
    assert value["page"] == 0
    assert value["chunk_index"] == -1


def test_source_to_dict():
    source = Source("S1", "d", "a.pdf", 2, 3, "text", 0.9)
    value = source_to_dict(source)
    assert value == {
        "label": "S1",
        "doc_id": "d",
        "file_name": "a.pdf",
        "page": 2,
        "chunk_index": 3,
        "text": "text",
        "score": 0.9,
    }


def test_dedupe_same_chunk_keeps_first():
    first = {"file_name": "a.pdf", "page": 1, "chunk_index": 0, "label": "S1"}
    second = {**first, "label": "S2"}
    assert dedupe_sources([first, second]) == [first]


def test_source_order_by_label_then_score():
    assert _source_order({"label": "S10"}) > _source_order({"label": "S2"})
    assert _source_order({"score": 0.9}) < _source_order({"score": 0.5})
    assert _source_order({"label": "S1", "score": 0.1}) == (0.0, 1.0)


def test_truncate_snippet():
    assert truncate_snippet("abc", max_chars=3) == "abc"
    assert truncate_snippet("abcdef", max_chars=3) == "abc…"


def test_md_escape():
    assert md_escape("a*b") == "a\\*b"


def test_render_empty_noop():
    render_sources([])


def test_render_nonempty_does_not_raise():
    render_sources(
        [
            {
                "label": "S1",
                "file_name": "a.pdf",
                "page": 1,
                "chunk_index": 0,
                "text": "Nội dung",
                "score": 0.9,
            }
        ]
    )


def test_render_uses_plain_text_not_unsafe_html():
    source = inspect.getsource(render_sources)
    assert "unsafe_allow_html" not in source
