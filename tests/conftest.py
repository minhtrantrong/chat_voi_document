"""Fixture dùng chung cho test."""

from __future__ import annotations

import uuid
from pathlib import Path

import pymupdf
import pytest

from app.config import get_settings


@pytest.fixture
def settings(tmp_path, monkeypatch):
    """Settings cô lập: DB/PDF trong tmp, collection Qdrant riêng, dim nhỏ."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("QDRANT_COLLECTION", f"test_{uuid.uuid4().hex}")
    monkeypatch.setenv("EMBEDDING_DIM", "8")
    monkeypatch.setenv("EMBEDDING_BATCH_SIZE", "2")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("EMBEDDING_MODEL", "test-embed")
    monkeypatch.setenv("LLM_MODEL", "test-llm")
    get_settings.cache_clear()
    value = get_settings()
    yield value
    get_settings.cache_clear()


@pytest.fixture
def qdrant_settings(settings):
    """Settings + dọn collection sau test (dùng cho test cần Qdrant thật)."""
    yield settings
    try:
        from app.vector_store import get_client

        client = get_client()
        if client.collection_exists(settings.qdrant_collection):
            client.delete_collection(settings.qdrant_collection)
    except Exception:
        pass


@pytest.fixture
def make_pdf(tmp_path):
    """Tạo PDF thật; pages là list[str], None/'' tạo trang trắng."""

    def _make(
        name: str = "sample.pdf",
        pages: list[str | None] | None = None,
        *,
        encrypted: bool = False,
    ) -> Path:
        pages = pages or ["Hello world. This is a sample document page with enough text to index."]
        doc = pymupdf.open()
        for text in pages:
            page = doc.new_page()
            if text:
                page.insert_text((72, 72), text, fontsize=12)
        path = tmp_path / name
        if encrypted:
            doc.save(
                path,
                encryption=pymupdf.PDF_ENCRYPT_AES_256,
                owner_pw="owner",
                user_pw="user",
            )
        else:
            doc.save(path)
        doc.close()
        return path

    return _make
