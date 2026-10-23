from __future__ import annotations

import pytest

from app import ingest as module
from app.db import DocumentStatus, list_documents
from app.embeddings import EmbeddingError
from app.ingest import IngestError, ingest_many, ingest_pdf
from app.pdf import PdfError
from app.vector_store import VectorStoreError


def _fake_embeddings(texts):
    return [[0.1] * 8 for _ in texts]


def test_ingest_success(settings, make_pdf, monkeypatch):
    path = make_pdf(pages=["This is a valid document with enough text to be chunked and indexed."])
    calls = {}
    monkeypatch.setattr(module, "embed_texts", _fake_embeddings)
    monkeypatch.setattr(module, "ensure_collection", lambda: None)

    def fake_upsert(doc_id, file_name, chunks, vectors):
        calls.update(doc_id=doc_id, file_name=file_name, chunks=chunks, vectors=vectors)

    monkeypatch.setattr(module, "upsert_chunks", fake_upsert)

    with path.open("rb") as file_obj:
        document = ingest_pdf(
            "sample.pdf",
            file_obj,
            size_bytes=path.stat().st_size,
        )

    assert document.status == DocumentStatus.READY
    assert document.page_count == 1
    assert document.error_code is None
    assert document.stored_path.exists()
    assert calls["file_name"] == "sample.pdf"
    assert calls["chunks"]
    assert len(calls["vectors"]) == len(calls["chunks"])
    assert len(list_documents()) == 1


def test_ingest_no_text_marks_error(settings, make_pdf, monkeypatch):
    path = make_pdf(pages=[None])
    monkeypatch.setattr(module, "embed_texts", _fake_embeddings)
    monkeypatch.setattr(module, "ensure_collection", lambda: None)
    monkeypatch.setattr(module, "upsert_chunks", lambda *_a, **_kw: None)

    with path.open("rb") as file_obj, pytest.raises(PdfError) as exc:
        ingest_pdf("scan.pdf", file_obj, size_bytes=path.stat().st_size)

    assert exc.value.code == "PDF_NO_TEXT"
    documents = list_documents()
    assert len(documents) == 1
    assert documents[0].status == DocumentStatus.ERROR
    assert documents[0].error_code == "PDF_NO_TEXT"


def test_ingest_encrypted_marks_error(settings, make_pdf):
    path = make_pdf(encrypted=True)
    with path.open("rb") as file_obj, pytest.raises(PdfError) as exc:
        ingest_pdf("encrypted.pdf", file_obj, size_bytes=path.stat().st_size)
    assert exc.value.code == "PDF_ENCRYPTED"
    assert list_documents()[0].error_code == "PDF_ENCRYPTED"


def test_ingest_wrong_extension_creates_no_document(settings, tmp_path):
    path = tmp_path / "fake.docx"
    path.write_bytes(b"not a pdf")
    with path.open("rb") as file_obj, pytest.raises(PdfError) as exc:
        ingest_pdf("fake.docx", file_obj, size_bytes=path.stat().st_size)
    assert exc.value.code == "PDF_NOT_PDF"
    assert list_documents() == []


def test_ingest_too_large_creates_no_document(settings, tmp_path):
    path = tmp_path / "big.pdf"
    path.write_bytes(b"%PDF-1.7\n")
    with path.open("rb") as file_obj, pytest.raises(PdfError) as exc:
        ingest_pdf(
            "big.pdf",
            file_obj,
            size_bytes=settings.max_upload_bytes + 1,
        )
    assert exc.value.code == "PDF_TOO_LARGE"
    assert list_documents() == []


def test_ingest_embedding_error_marks_error_and_cleans_points(settings, make_pdf, monkeypatch):
    path = make_pdf()
    cleaned = []
    monkeypatch.setattr(
        module,
        "embed_texts",
        lambda _texts: (_ for _ in ()).throw(EmbeddingError("embedding down")),
    )
    monkeypatch.setattr(module, "ensure_collection", lambda: None)
    monkeypatch.setattr(
        module,
        "delete_vector_document",
        lambda doc_id: cleaned.append(doc_id),
    )

    with path.open("rb") as file_obj, pytest.raises(EmbeddingError):
        ingest_pdf("sample.pdf", file_obj, size_bytes=path.stat().st_size)

    assert cleaned
    document = list_documents()[0]
    assert document.status == DocumentStatus.ERROR
    assert document.error_code == "EMBEDDING_FAILED"


def test_ingest_upsert_error_marks_error_and_cleans_points(settings, make_pdf, monkeypatch):
    path = make_pdf()
    cleaned = []
    monkeypatch.setattr(module, "embed_texts", _fake_embeddings)
    monkeypatch.setattr(module, "ensure_collection", lambda: None)
    monkeypatch.setattr(
        module,
        "upsert_chunks",
        lambda *_a, **_kw: (_ for _ in ()).throw(RuntimeError("qdrant down")),
    )
    monkeypatch.setattr(
        module,
        "delete_vector_document",
        lambda doc_id: cleaned.append(doc_id),
    )

    with path.open("rb") as file_obj, pytest.raises(IngestError):
        ingest_pdf("sample.pdf", file_obj, size_bytes=path.stat().st_size)

    assert cleaned
    document = list_documents()[0]
    assert document.status == DocumentStatus.ERROR
    assert document.error_code == "INGEST_FAILED"


def test_progress_called_in_order(settings, make_pdf, monkeypatch):
    path = make_pdf()
    stages = []
    monkeypatch.setattr(module, "embed_texts", _fake_embeddings)
    monkeypatch.setattr(module, "ensure_collection", lambda: None)
    monkeypatch.setattr(module, "upsert_chunks", lambda *_a, **_kw: None)

    with path.open("rb") as file_obj:
        document = ingest_pdf(
            "sample.pdf",
            file_obj,
            progress=lambda stage, percent: stages.append((stage, percent)),
        )

    assert stages[0] == ("validating", 0)
    assert stages[-1] == ("done", 100)
    assert [percent for _stage, percent in stages] == sorted(percent for _stage, percent in stages)
    assert document.stored_path.name == f"{document.id}.pdf"


def test_create_document_failure_removes_saved_file(settings, make_pdf, monkeypatch):
    path = make_pdf()
    monkeypatch.setattr(
        module,
        "create_document",
        lambda *_a, **_kw: (_ for _ in ()).throw(RuntimeError("db down")),
    )
    with path.open("rb") as file_obj, pytest.raises(RuntimeError):
        ingest_pdf("sample.pdf", file_obj, size_bytes=path.stat().st_size)
    assert list(settings.uploads_dir.glob("*.pdf")) == []


def test_qdrant_failure_marks_error(settings, make_pdf, monkeypatch):
    path = make_pdf()
    monkeypatch.setattr(module, "embed_texts", _fake_embeddings)
    monkeypatch.setattr(
        module,
        "ensure_collection",
        lambda: (_ for _ in ()).throw(VectorStoreError("down")),
    )
    with path.open("rb") as file_obj, pytest.raises(IngestError) as exc:
        ingest_pdf("sample.pdf", file_obj, size_bytes=path.stat().st_size)
    assert exc.value.code == "QDRANT_UNAVAILABLE"
    assert list_documents()[0].error_code == "QDRANT_UNAVAILABLE"


def test_ingest_many_continues_after_failure(settings, monkeypatch):
    class FakeDocument:
        status = DocumentStatus.READY

    def fake_ingest(file_name, _file_obj, **_kwargs):
        if file_name == "bad.pdf":
            raise RuntimeError("bad")
        return FakeDocument()

    monkeypatch.setattr(module, "ingest_pdf", fake_ingest)
    results = ingest_many(
        [
            ("good.pdf", object(), 1),
            ("bad.pdf", object(), 1),
            ("good2.pdf", object(), 1),
        ]
    )
    assert [result.ok for result in results] == [True, False, True]
    assert results[1].error is not None
