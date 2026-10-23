from __future__ import annotations

import logging

from app.embeddings import EmbeddingError
from app.errors import ERROR_MESSAGES, error_code, error_message, log_error
from app.ingest import IngestError
from app.llm import LLMError
from app.pdf import PdfError
from app.vector_store import VectorStoreError


class CodedError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def test_every_code_has_message():
    for code in ERROR_MESSAGES:
        assert error_message(CodedError(code))


def test_unknown_code_falls_back_to_internal():
    assert error_code(CodedError("WAT")) == "INTERNAL"
    assert error_message(CodedError("WAT")) == ERROR_MESSAGES["INTERNAL"]


def test_file_name_prefix():
    message = error_message(EmbeddingError("x"), "a.pdf")
    assert message.startswith("a.pdf: ")


def test_pdf_error_uses_friendly_message_not_detail():
    exc = PdfError(
        "PDF_TOO_LARGE",
        "Tệp vượt quá 25 MB.",
        detail="/home/private/secret.pdf",
    )
    message = error_message(exc, "a.pdf")
    assert "25 MB" in message
    assert "/home/private" not in message


def test_ingest_llm_and_qdrant_codes():
    assert "tài liệu" in error_message(IngestError("x"))
    assert "Trợ lý" in error_message(LLMError("x"))
    assert "vector" in error_message(VectorStoreError("x"))


def test_no_raw_exception_text():
    message = error_message(ValueError("raw secret text"))
    assert "raw secret" not in message
    assert message == ERROR_MESSAGES["INTERNAL"]


def test_log_does_not_include_detail(caplog):
    caplog.set_level(logging.WARNING)
    exc = PdfError("PDF_NO_TEXT", "PDF không có text.", detail="/secret/path")
    log_error(exc, context="unit")
    assert "context=unit" in caplog.text
    assert "PDF_NO_TEXT" in caplog.text
    assert "/secret/path" not in caplog.text
