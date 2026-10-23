from __future__ import annotations

import sqlite3

import pytest

from app.db import (
    DocumentStatus,
    clear_documents,
    count_ready_documents,
    create_document,
    delete_document,
    get_document,
    init_db,
    list_documents,
    mark_error,
    mark_ready,
)


def test_crud_and_status_transitions(settings, tmp_path):
    init_db()
    stored = settings.uploads_dir / "a.pdf"
    stored.write_bytes(b"%PDF-test")

    create_document("doc-1", "a.pdf", stored, 123)
    doc = get_document("doc-1")
    assert doc is not None
    assert doc.status == DocumentStatus.PROCESSING
    assert doc.page_count is None
    assert doc.stored_path == stored
    assert doc.error_code is None

    mark_ready("doc-1", 3)
    doc = get_document("doc-1")
    assert doc is not None
    assert doc.status == DocumentStatus.READY
    assert doc.page_count == 3
    assert doc.processed_at is not None

    mark_error("doc-1", "PDF_NO_TEXT")
    doc = get_document("doc-1")
    assert doc is not None
    assert doc.status == DocumentStatus.ERROR
    assert doc.error_code == "PDF_NO_TEXT"


def test_list_order_count_and_delete(settings):
    init_db()
    for index in range(3):
        create_document(
            f"doc-{index}",
            f"{index}.pdf",
            settings.uploads_dir / f"{index}.pdf",
            index,
        )
    mark_ready("doc-0", 1)
    mark_ready("doc-2", 2)

    docs = list_documents()
    assert {doc.id for doc in docs} == {"doc-0", "doc-1", "doc-2"}
    assert count_ready_documents() == 2

    delete_document("doc-1")
    delete_document("doc-1")  # idempotent
    assert get_document("doc-1") is None

    clear_documents()
    assert list_documents() == []


def test_get_missing_returns_none(settings):
    init_db()
    assert get_document("missing") is None


def test_init_db_is_idempotent(settings):
    init_db()
    init_db()
    assert list_documents() == []


def test_duplicate_id_raises(settings):
    init_db()
    stored = settings.uploads_dir / "a.pdf"
    create_document("doc-1", "a.pdf", stored, 1)
    with pytest.raises(sqlite3.IntegrityError):
        create_document("doc-1", "a.pdf", stored, 1)
