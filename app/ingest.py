"""Pipeline ingest PDF: lưu file → extract → chunk → embed → Qdrant."""

from __future__ import annotations

import contextlib
import shutil
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import BinaryIO

from app.chunking import chunk_pages
from app.config import get_settings
from app.db import (
    Document,
    create_document,
    get_document,
    init_db,
    mark_error,
    mark_ready,
)
from app.embeddings import EmbeddingError, embed_texts
from app.pdf import (
    PdfError,
    extract_pages,
    inspect_pdf,
    validate_filename,
)
from app.vector_store import (
    VectorStoreError,
    ensure_collection,
    upsert_chunks,
)
from app.vector_store import (
    delete_document as delete_vector_document,
)

ProgressFn = Callable[[str, int], None]


class IngestError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str = "INGEST_FAILED",
        detail: str | None = None,
    ):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(message)


@dataclass(frozen=True)
class IngestResult:
    file_name: str
    ok: bool
    document: Document | None = None
    error: Exception | None = None


def _progress(progress: ProgressFn | None, stage: str, percent: int) -> None:
    if progress is not None:
        progress(stage, percent)


def _cleanup_points(doc_id: str) -> None:
    with contextlib.suppress(Exception):
        delete_vector_document(doc_id)


def ingest_pdf(
    file_name: str,
    file_obj: BinaryIO,
    *,
    size_bytes: int | None = None,
    progress: ProgressFn | None = None,
) -> Document:
    settings = get_settings()
    init_db()
    _progress(progress, "validating", 0)
    validate_filename(file_name)
    if size_bytes is not None and size_bytes > settings.max_upload_bytes:
        raise PdfError(
            "PDF_TOO_LARGE",
            f"Tệp vượt quá {settings.max_upload_mb} MB.",
        )

    doc_id = uuid.uuid4().hex
    stored_path = (settings.uploads_dir / f"{doc_id}.pdf").resolve()
    _progress(progress, "saving", 5)
    try:
        with stored_path.open("wb") as output:
            shutil.copyfileobj(file_obj, output, length=1024 * 1024)
    except Exception as exc:
        stored_path.unlink(missing_ok=True)
        raise IngestError(
            "Không lưu được tệp tải lên.",
            detail=str(exc),
        ) from exc

    try:
        create_document(
            doc_id,
            file_name,
            stored_path,
            stored_path.stat().st_size,
        )
    except Exception:
        stored_path.unlink(missing_ok=True)
        raise

    try:
        info = inspect_pdf(
            stored_path,
            max_pages=settings.max_pages,
            max_bytes=settings.max_upload_bytes,
        )
        _progress(progress, "extracting", 15)
        pages = extract_pages(
            stored_path,
            min_text_chars_per_page=settings.min_text_chars_per_page,
        )

        _progress(progress, "chunking", 30)
        chunks = chunk_pages(
            pages,
            size_tokens=settings.chunk_size_tokens,
            overlap_tokens=settings.chunk_overlap_tokens,
        )
        if not chunks:
            raise PdfError("PDF_NO_TEXT", "Không tạo được đoạn văn bản nào.")

        _progress(progress, "embedding", 40)
        vectors = embed_texts([chunk.text for chunk in chunks])

        _progress(progress, "indexing", 80)
        ensure_collection()
        upsert_chunks(doc_id, file_name, chunks, vectors)

        mark_ready(doc_id, page_count=info.page_count)
        _progress(progress, "done", 100)
        document = get_document(doc_id)
        if document is None:
            raise IngestError("Không tìm thấy tài liệu sau khi xử lý.")
        return document

    except PdfError as exc:
        mark_error(doc_id, exc.code)
        raise
    except EmbeddingError as exc:
        mark_error(doc_id, exc.code)
        _cleanup_points(doc_id)
        raise
    except VectorStoreError as exc:
        mark_error(doc_id, exc.code)
        _cleanup_points(doc_id)
        raise IngestError("Không ghi được dữ liệu vector.", code=exc.code) from exc
    except Exception as exc:
        mark_error(doc_id, "INGEST_FAILED")
        _cleanup_points(doc_id)
        raise IngestError(
            "Không xử lý được tài liệu.",
            detail=str(exc),
        ) from exc


def ingest_many(
    files: list[tuple[str, BinaryIO, int | None]],
    *,
    progress_factory: Callable[[str], ProgressFn] | None = None,
) -> list[IngestResult]:
    results: list[IngestResult] = []
    for file_name, file_obj, size_bytes in files:
        progress = progress_factory(file_name) if progress_factory else None
        try:
            document = ingest_pdf(
                file_name,
                file_obj,
                size_bytes=size_bytes,
                progress=progress,
            )
            results.append(IngestResult(file_name, True, document=document))
        except Exception as exc:
            results.append(IngestResult(file_name, False, error=exc))
    return results
