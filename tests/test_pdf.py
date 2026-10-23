from __future__ import annotations

import pytest

from app.pdf import (
    PdfError,
    _clean_text,
    extract_pages,
    inspect_pdf,
    validate_filename,
    validate_uploaded,
)

MAX_BYTES = 25 * 1024 * 1024


def test_validate_filename():
    validate_filename("a.pdf")
    validate_filename("A.PDF")
    with pytest.raises(PdfError) as exc:
        validate_filename("a.docx")
    assert exc.value.code == "PDF_NOT_PDF"


def test_inspect_valid_pdf(make_pdf):
    path = make_pdf()
    info = inspect_pdf(path, max_pages=10, max_bytes=MAX_BYTES)
    assert info.page_count == 1
    assert info.is_pdf is True
    assert info.needs_pass is False


def test_inspect_too_many_pages(make_pdf):
    path = make_pdf(pages=["Page one with enough text.", "Page two with enough text."])
    with pytest.raises(PdfError) as exc:
        inspect_pdf(path, max_pages=1, max_bytes=MAX_BYTES)
    assert exc.value.code == "PDF_TOO_MANY_PAGES"


def test_inspect_too_large(make_pdf):
    path = make_pdf()
    with pytest.raises(PdfError) as exc:
        inspect_pdf(path, max_pages=10, max_bytes=10)
    assert exc.value.code == "PDF_TOO_LARGE"


def test_inspect_not_pdf(tmp_path):
    path = tmp_path / "fake.pdf"
    path.write_bytes(b"hello")
    with pytest.raises(PdfError) as exc:
        inspect_pdf(path, max_pages=10, max_bytes=MAX_BYTES)
    assert exc.value.code == "PDF_NOT_PDF"


def test_inspect_corrupt(tmp_path):
    path = tmp_path / "corrupt.pdf"
    path.write_bytes(b"%PDF-1.7\nnot really a pdf")
    with pytest.raises(PdfError) as exc:
        inspect_pdf(path, max_pages=10, max_bytes=MAX_BYTES)
    assert exc.value.code == "PDF_CORRUPT"


def test_inspect_missing(tmp_path):
    with pytest.raises(PdfError) as exc:
        inspect_pdf(tmp_path / "missing.pdf", max_pages=10, max_bytes=MAX_BYTES)
    assert exc.value.code == "PDF_CORRUPT"


def test_inspect_empty_file(tmp_path):
    path = tmp_path / "empty.pdf"
    path.write_bytes(b"")
    with pytest.raises(PdfError) as exc:
        inspect_pdf(path, max_pages=10, max_bytes=MAX_BYTES)
    assert exc.value.code == "PDF_CORRUPT"


def test_validate_uploaded_uses_settings(settings, make_pdf):
    path = make_pdf("A.PDF")
    info = validate_uploaded(path, settings)
    assert info.page_count == 1


def test_clean_text_nfc_and_nul():
    text = "Ha\u0300 No\u0302\u0323i\x00"
    cleaned = _clean_text(text)
    assert cleaned == "Hà Nội"
    assert "\x00" not in cleaned


def test_inspect_encrypted(make_pdf):
    path = make_pdf(encrypted=True)
    with pytest.raises(PdfError) as exc:
        inspect_pdf(path, max_pages=10, max_bytes=MAX_BYTES)
    assert exc.value.code == "PDF_ENCRYPTED"


def test_extract_pages(make_pdf):
    path = make_pdf(
        pages=[
            "Page one. This text is long enough to keep.",
            "Page two. This text is also long enough.",
        ]
    )
    pages = extract_pages(path, min_text_chars_per_page=20)
    assert [page.page for page in pages] == [1, 2]
    assert "Page one" in pages[0].text


def test_extract_skips_short_pages(make_pdf):
    path = make_pdf(pages=["short", "This page has enough text to keep in the index."])
    pages = extract_pages(path, min_text_chars_per_page=20)
    assert len(pages) == 1
    assert pages[0].page == 2


def test_extract_no_text(make_pdf):
    path = make_pdf(pages=[None])
    with pytest.raises(PdfError) as exc:
        extract_pages(path, min_text_chars_per_page=20)
    assert exc.value.code == "PDF_NO_TEXT"


def test_extract_mixed_pdf_keeps_text_pages(make_pdf):
    path = make_pdf(pages=[None, "This page has enough text to keep in the index."])
    pages = extract_pages(path, min_text_chars_per_page=20)
    assert [page.page for page in pages] == [2]
