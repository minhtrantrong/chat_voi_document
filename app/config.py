"""Cấu hình ứng dụng đọc từ biến môi trường / `.env`."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "document_chunks"
    qdrant_timeout: int = 10

    # LLM / Embedding (mặc định: LM Studio local, OpenAI-compatible)
    openai_base_url: str = "http://localhost:1234/v1"
    openai_api_key: str = Field(default="lm-studio", repr=False)
    llm_model: str = "qwen/qwen3-1.7b"
    llm_temperature: float = 0.1
    embedding_model: str = "text-embedding-nomic-embed-text-v1.5"
    embedding_dim: int = 768
    embedding_batch_size: int = 64

    # Upload / PDF / chunking
    max_upload_mb: int = 25
    max_pages: int = 400
    min_text_chars_per_page: int = 20
    chunk_size_tokens: int = 700
    chunk_overlap_tokens: int = 100

    # Retrieval / chat
    top_k: int = 8
    score_threshold: float = 0.25
    max_chunks_per_doc: int = 4
    max_context_chars: int = 24_000
    max_history_messages: int = 6
    max_question_chars: int = 2_000

    # Storage
    data_dir: Path = Path("./data")

    @model_validator(mode="after")
    def _validate(self) -> Settings:
        if self.embedding_dim <= 0:
            raise ValueError("EMBEDDING_DIM phải > 0")
        if self.max_upload_mb <= 0:
            raise ValueError("MAX_UPLOAD_MB phải > 0")
        if self.max_pages <= 0:
            raise ValueError("MAX_PAGES phải > 0")
        if self.top_k <= 0:
            raise ValueError("TOP_K phải > 0")
        if self.max_chunks_per_doc <= 0:
            raise ValueError("MAX_CHUNKS_PER_DOC phải > 0")
        if not 0 <= self.score_threshold <= 1:
            raise ValueError("SCORE_THRESHOLD phải trong [0, 1]")
        if self.chunk_overlap_tokens >= self.chunk_size_tokens:
            raise ValueError("CHUNK_OVERLAP_TOKENS phải nhỏ hơn CHUNK_SIZE_TOKENS")
        if self.embedding_batch_size <= 0:
            raise ValueError("EMBEDDING_BATCH_SIZE phải > 0")

        self.data_dir = self.data_dir.expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        return self

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def db_path(self) -> Path:
        return self.data_dir / "app.db"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def require_api_key(settings: Settings) -> None:
    if not settings.openai_api_key.strip():
        raise RuntimeError(
            "Thiếu OPENAI_API_KEY. Với LM Studio/Ollama, dùng giá trị giả (vd. `lm-studio`); "
            "với OpenAI, sao chép `.env.example` thành `.env` và điền key."
        )
