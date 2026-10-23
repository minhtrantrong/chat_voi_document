from __future__ import annotations

from pathlib import Path

import pytest
from qdrant_client.models import Distance, VectorParams
from streamlit.testing.v1 import AppTest

from app.db import (
    create_document,
    init_db,
    mark_error,
    mark_ready,
)
from app.vector_store import get_client, health

APP = Path(__file__).resolve().parents[1] / "app" / "main.py"


def _run(settings):
    init_db()
    app = AppTest.from_file(APP, default_timeout=30)
    app.run()
    return app


def _seed(settings, *, status: str = "READY"):
    init_db()
    stored = settings.uploads_dir / "a.pdf"
    stored.write_bytes(b"%PDF-1.7\n")
    create_document("doc-1", "a.pdf", stored, stored.stat().st_size)
    if status == "READY":
        mark_ready("doc-1", 1)
    elif status == "ERROR":
        mark_error("doc-1", "PDF_NO_TEXT")


def test_no_docs_chat_disabled(qdrant_settings):
    app = _run(qdrant_settings)
    assert not app.exception
    assert any(header.value == "Tài liệu" for header in app.header)
    assert len(app.file_uploader) == 1
    assert app.chat_input[0].disabled is True
    assert any("Tải PDF đầu tiên" in info.value for info in app.info)


def test_only_error_doc_chat_disabled(qdrant_settings):
    _seed(qdrant_settings, status="ERROR")
    app = AppTest.from_file(APP, default_timeout=30)
    app.run()
    assert not app.exception
    assert app.chat_input[0].disabled is True
    assert any("Chưa có tài liệu sẵn sàng" in warning.value for warning in app.warning)


def test_processing_doc_chat_disabled(qdrant_settings):
    _seed(qdrant_settings, status="PROCESSING")
    app = AppTest.from_file(APP, default_timeout=30)
    app.run()
    assert not app.exception
    assert app.chat_input[0].disabled is True
    assert any("Đang xử lý" in caption.value for caption in app.caption)


def test_ready_doc_chat_enabled(qdrant_settings):
    _seed(qdrant_settings, status="READY")
    app = AppTest.from_file(APP, default_timeout=30)
    app.run()
    assert not app.exception
    assert app.chat_input[0].disabled is False
    assert any("a\\.pdf" in item.value for item in app.markdown)


@pytest.mark.integration
def test_dimension_mismatch_banner(qdrant_settings):
    if not health():
        pytest.skip("Qdrant không chạy")
    client = get_client()
    client.create_collection(
        collection_name=qdrant_settings.qdrant_collection,
        vectors_config=VectorParams(size=4, distance=Distance.COSINE),
    )
    app = AppTest.from_file(APP, default_timeout=30)
    app.run()
    assert not app.exception
    assert any("vector size" in item.value for item in app.error)


def test_history_is_rendered(qdrant_settings):
    _seed(qdrant_settings, status="READY")
    app = AppTest.from_file(APP, default_timeout=30)
    app.run()
    app.session_state["messages"] = [
        {"role": "user", "content": "Xin chào"},
        {"role": "assistant", "content": "Chào bạn", "sources": []},
    ]
    app.run()
    assert not app.exception
    rendered = [item.value for item in app.markdown]
    assert "Xin chào" in rendered
    assert "Chào bạn" in rendered
