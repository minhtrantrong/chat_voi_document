from __future__ import annotations

from app.db import Document, DocumentStatus
from app.rag import Source
from app.ui import (
    dedupe_sources,
    empty_state_message,
    format_bytes,
    has_ready_documents,
    ingest_stage_text,
    source_to_dict,
    status_text,
)


def _doc(status: DocumentStatus, doc_id: str = "d") -> Document:
    return Document(
        id=doc_id,
        file_name="a.pdf",
        stored_path="a.pdf",
        size_bytes=10,
        page_count=1,
        status=status,
        error_code=None,
        created_at="now",
        processed_at=None,
    )


def test_format_bytes():
    assert format_bytes(0) == "0 B"
    assert format_bytes(1024) == "1 KB"
    assert format_bytes(1024**2) == "1.0 MB"


def test_has_ready_documents():
    assert has_ready_documents([_doc(DocumentStatus.READY)]) is True
    assert has_ready_documents([_doc(DocumentStatus.ERROR)]) is False


def test_empty_state_messages():
    assert empty_state_message([])[0] == "info"
    assert empty_state_message([_doc(DocumentStatus.PROCESSING)])[0] == "info"
    assert empty_state_message([_doc(DocumentStatus.ERROR)])[0] == "warning"
    assert empty_state_message([_doc(DocumentStatus.READY)]) is None


def test_status_text():
    assert "Sẵn sàng" in status_text(_doc(DocumentStatus.READY))
    assert "Lỗi" in status_text(_doc(DocumentStatus.ERROR))


def test_source_to_dict_and_dedupe():
    source = Source("S1", "d", "a.pdf", 1, 2, "text", 0.9)
    item = source_to_dict(source)
    assert item["label"] == "S1"
    assert item["page"] == 1
    assert dedupe_sources([item, item, {**item, "label": "S2"}]) == [item]


def test_ingest_stage_text_processing_has_percent() -> None:
    text = ingest_stage_text("a.pdf", "extracting", 15)
    assert "⏳" in text and "Đang đọc văn bản" in text and "(15%)" in text


def test_ingest_stage_text_pending_and_done_have_no_percent() -> None:
    assert "%" not in ingest_stage_text("a.pdf", "pending", 0)
    done = ingest_stage_text("a.pdf", "done", 100)
    assert "✅" in done and "%" not in done


def test_ingest_stage_text_unknown_stage_falls_back() -> None:
    assert "Đang xử lý" in ingest_stage_text("a.pdf", "xyz")
