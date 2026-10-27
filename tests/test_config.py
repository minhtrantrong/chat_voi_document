from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings, require_api_key


def test_settings_creates_directories(settings):
    assert settings.embedding_dim == 8
    assert settings.db_path.parent == settings.data_dir
    assert settings.db_path.parent.exists()
    assert settings.uploads_dir.exists()
    assert settings.max_upload_bytes == settings.max_upload_mb * 1024 * 1024


def test_defaults_use_lm_studio_and_small_embedding(tmp_path, monkeypatch):
    for key in (
        "OPENAI_BASE_URL",
        "OPENAI_API_KEY",
        "LLM_MODEL",
        "EMBEDDING_MODEL",
        "EMBEDDING_DIM",
    ):
        monkeypatch.delenv(key, raising=False)
    value = Settings(data_dir=tmp_path / "data", _env_file=None)
    assert value.openai_base_url == "http://localhost:1234/v1"
    assert value.openai_api_key == "lm-studio"
    assert value.llm_model == "qwen/qwen3-1.7b"
    assert value.embedding_model == "text-embedding-nomic-embed-text-v1.5"
    assert value.embedding_dim == 768


def test_settings_rejects_bad_overlap(tmp_path):
    with pytest.raises(ValidationError):
        Settings(
            data_dir=tmp_path / "data",
            chunk_size_tokens=100,
            chunk_overlap_tokens=100,
        )


@pytest.mark.parametrize(
    "overrides",
    [
        {"embedding_dim": 0},
        {"max_upload_mb": 0},
        {"max_pages": 0},
        {"top_k": 0},
        {"max_chunks_per_doc": 0},
        {"score_threshold": 1.1},
        {"embedding_batch_size": 0},
    ],
)
def test_settings_rejects_invalid_values(tmp_path, overrides):
    with pytest.raises(ValidationError):
        Settings(data_dir=tmp_path / "data", **overrides)


def test_repr_hides_api_key(tmp_path):
    value = Settings(data_dir=tmp_path / "data", openai_api_key="sk-secret")
    assert "sk-secret" not in repr(value)


def test_require_api_key_rejects_empty(tmp_path):
    value = Settings(data_dir=tmp_path / "data", openai_api_key="")
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        require_api_key(value)


def test_require_api_key_accepts_value(tmp_path):
    value = Settings(data_dir=tmp_path / "data", openai_api_key="abc")
    require_api_key(value)


def test_get_settings_is_cached(settings):
    assert get_settings() is get_settings()
