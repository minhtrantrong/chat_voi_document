from __future__ import annotations

import pytest

from app import ingest as ingest_module
from app.db import DocumentStatus, get_document
from app.db import delete_document as delete_document_row
from app.ingest import ingest_pdf
from app.vector_store import (
    count_points,
    delete_document,
    health,
    search_chunks,
)


@pytest.mark.integration
def test_full_ingest_to_qdrant_and_delete(qdrant_settings, make_pdf, monkeypatch):
    if not health():
        pytest.skip("Qdrant không chạy")

    path = make_pdf(
        pages=[
            "Hợp đồng số 123. Giá trị 1.200.000.000 VND. "
            "Hạn chót nộp hồ sơ là 30/11/2026. Bảo hành 24 tháng."
        ]
    )
    monkeypatch.setattr(
        ingest_module,
        "embed_texts",
        lambda texts: [[1.0] * 8 for _ in texts],
    )

    with path.open("rb") as file_obj:
        document = ingest_pdf(
            "hop-dong.pdf",
            file_obj,
            size_bytes=path.stat().st_size,
        )

    assert document.status == DocumentStatus.READY
    assert document.page_count == 1
    assert count_points() >= 1

    hits = search_chunks([1.0] * 8, limit=10, score_threshold=0.0)
    assert hits
    assert all(hit.payload["doc_id"] == document.id for hit in hits)
    assert any("1.200.000.000" in hit.payload["text"] for hit in hits)

    stored_path = document.stored_path
    delete_document(document.id)
    delete_document_row(document.id)
    stored_path.unlink(missing_ok=True)
    assert count_points() == 0
    assert get_document(document.id) is None
    assert not stored_path.exists()
