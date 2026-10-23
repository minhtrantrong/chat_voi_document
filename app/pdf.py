"""Đọc, kiểm tra và trích xuất văn bản từ PDF."""

from __future__ import annotations

import logging
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import pymupdf

logger = logging.getLogger(__name__)
PDF_MAGIC = b"%PDF-"


@dataclass(frozen=True)
class PdfInfo:
    page_count: int
    needs_pass: bool
    is_pdf: bool


@dataclass(frozen=True)
class PageText:
    page: int  # 1-based
    text: str


class PdfError(Exception):
    def __init__(self, code: str, message: str, *, detail: str | None = None):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(message)


def validate_filename(file_name: str) -> None:
    if not file_name.lower().endswith(".pdf"):
        raise PdfError("PDF_NOT_PDF", "Chỉ chấp nhận tệp PDF.")


def inspect_pdf(path: Path, *, max_pages: int, max_bytes: int) -> PdfInfo:
    if not path.exists():
        raise PdfError("PDF_CORRUPT", "Không tìm thấy tệp PDF.")
    size = path.stat().st_size
    if size == 0:
        raise PdfError("PDF_CORRUPT", "Tệp PDF rỗng.")
    if size > max_bytes:
        raise PdfError(
            "PDF_TOO_LARGE",
            f"Tệp vượt quá {max_bytes // (1024 * 1024)} MB.",
            detail=f"size={size}",
        )

    with path.open("rb") as fh:
        if fh.read(5) != PDF_MAGIC:
            raise PdfError("PDF_NOT_PDF", "Tệp không phải PDF hợp lệ.")

    try:
        doc = pymupdf.open(path)
    except Exception as exc:
        raise PdfError("PDF_CORRUPT", "Không mở được tệp PDF.", detail=str(exc)) from exc

    try:
        page_count = doc.page_count
        if doc.needs_pass:
            raise PdfError("PDF_ENCRYPTED", "PDF đang được bảo vệ bằng mật khẩu.")
        if page_count == 0:
            raise PdfError("PDF_CORRUPT", "PDF không có trang nào.")
        if page_count > max_pages:
            raise PdfError(
                "PDF_TOO_MANY_PAGES",
                f"PDF có {page_count} trang, vượt giới hạn {max_pages} trang.",
            )
        return PdfInfo(page_count=page_count, needs_pass=False, is_pdf=True)
    finally:
        doc.close()


def _clean_text(raw: str) -> str:
    text = raw.replace("\x00", "")
    text = unicodedata.normalize("NFC", text)
    return text.strip()


def extract_pages(
    path: Path,
    *,
    min_text_chars_per_page: int = 20,
) -> list[PageText]:
    try:
        doc = pymupdf.open(path)
    except Exception as exc:
        raise PdfError("PDF_CORRUPT", "Không mở được tệp PDF.", detail=str(exc)) from exc

    pages: list[PageText] = []
    skipped = 0
    try:
        page_count = doc.page_count
        for index in range(page_count):
            page = doc.load_page(index)
            try:
                raw = page.get_text("text", sort=True)
            except Exception:
                skipped += 1
                continue
            text = _clean_text(raw)
            if len(text) < min_text_chars_per_page:
                skipped += 1
                continue
            pages.append(PageText(page=index + 1, text=text))
    finally:
        doc.close()

    logger.debug(
        "extract_pages total=%s kept=%s skipped=%s",
        page_count,
        len(pages),
        skipped,
    )
    if not pages:
        raise PdfError(
            "PDF_NO_TEXT",
            "PDF không có văn bản để tìm kiếm (có thể là PDF scan). Ứng dụng chưa hỗ trợ OCR.",
            detail=f"pages={page_count}, skipped={skipped}",
        )
    return pages


def validate_uploaded(path: Path, settings) -> PdfInfo:
    return inspect_pdf(
        path,
        max_pages=settings.max_pages,
        max_bytes=settings.max_upload_bytes,
    )
