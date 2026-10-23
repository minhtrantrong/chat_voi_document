# S-03 — Config và Settings

| Thuộc tính | Giá trị |
|---|---|
| Story | Nền tảng |
| Phase | P0 |
| Tầng | APP |
| Ước lượng | 0,25d |
| Phụ thuộc | S-01 |
| Chặn | S-05, S-06, S-09, S-16 |
| Owner gợi ý | Backend |

## 1. Mục tiêu

Tập trung toàn bộ cấu hình vào một `Settings` có type, đọc từ `.env`, validate sớm và tạo thư mục dữ liệu. Không hard-code URL, model, key, giới hạn trong code.

## 2. Phạm vi

**Làm:**

- `app/config.py` dùng `pydantic-settings`.
- Các trường ở bảng §4.1.
- Validate: `embedding_dim > 0`, `max_upload_mb > 0`, `max_pages > 0`, `top_k > 0`, `0 <= score_threshold <= 1`.
- Tạo `DATA_DIR` và `DATA_DIR/uploads` nếu chưa có.
- `get_settings()` cache bằng `functools.lru_cache`.
- Không log `openai_api_key`.

**Không làm:**

- Chưa cấu hình Qdrant collection (S-05).
- Chưa đọc config từ DB/UI.

## 3. File chính

```text
app/config.py
.env.example
```

## 4. Đặc tả

```python
from functools import lru_cache
from pathlib import Path
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "document_chunks"

    # LLM / Embedding (mặc định: Ollama local)
    openai_base_url: str = "http://localhost:11434/v1"
    openai_api_key: str = Field(default="ollama", repr=False)
    llm_model: str = "llama3.1"
    embedding_model: str = "nomic-embed-text"
    embedding_dim: int = 768

    # Upload / chunk
    max_upload_mb: int = 25
    max_pages: int = 400
    min_text_chars_per_page: int = 20
    chunk_size_tokens: int = 700
    chunk_overlap_tokens: int = 100
    embedding_batch_size: int = 64

    # Retrieval
    top_k: int = 8
    score_threshold: float = 0.25
    max_chunks_per_doc: int = 4
    max_context_chars: int = 24_000

    # Storage
    data_dir: Path = Path("./data")

    @model_validator(mode="after")
    def _validate(self) -> "Settings":
        if self.embedding_dim <= 0:
            raise ValueError("EMBEDDING_DIM phải > 0")
        if self.max_upload_mb <= 0:
            raise ValueError("MAX_UPLOAD_MB phải > 0")
        if self.max_pages <= 0:
            raise ValueError("MAX_PAGES phải > 0")
        if self.top_k <= 0:
            raise ValueError("TOP_K phải > 0")
        if not 0 <= self.score_threshold <= 1:
            raise ValueError("SCORE_THRESHOLD phải trong [0, 1]")
        if self.chunk_overlap_tokens >= self.chunk_size_tokens:
            raise ValueError("CHUNK_OVERLAP_TOKENS phải nhỏ hơn CHUNK_SIZE_TOKENS")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "uploads").mkdir(parents=True, exist_ok=True)
        return self

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def db_path(self) -> Path:
        return self.data_dir / "app.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### 4.1 Bảng biến môi trường

| Biến | Mặc định | Ghi chú |
|---|---|---|
| `QDRANT_URL` | `http://localhost:6333` | |
| `QDRANT_API_KEY` | rỗng | Qdrant local không cần |
| `QDRANT_COLLECTION` | `document_chunks` | |
| `OPENAI_BASE_URL` | `http://localhost:11434/v1` | Ollama mặc định; đổi sang OpenAI/vLLM nếu cần |
| `OPENAI_API_KEY` | `ollama` | Ollama không cần key thật; OpenAI dùng key thật; không log |
| `LLM_MODEL` | `llama3.1` | |
| `EMBEDDING_MODEL` | `nomic-embed-text` | |
| `EMBEDDING_DIM` | `768` | phải khớp model |
| `MAX_UPLOAD_MB` | `25` | |
| `MAX_PAGES` | `400` | |
| `MIN_TEXT_CHARS_PER_PAGE` | `20` | dùng phát hiện scan |
| `CHUNK_SIZE_TOKENS` | `700` | |
| `CHUNK_OVERLAP_TOKENS` | `100` | |
| `EMBEDDING_BATCH_SIZE` | `64` | |
| `TOP_K` | `8` | |
| `SCORE_THRESHOLD` | `0.25` | |
| `MAX_CHUNKS_PER_DOC` | `4` | |
| `MAX_CONTEXT_CHARS` | `24000` | |
| `DATA_DIR` | `./data` | |

### 4.2 Kiểm tra API key

Không cần fail-fast lúc import (để test dễ). Tạo helper:

```python
def require_api_key(s: Settings) -> None:
    if not s.openai_api_key.strip():
        raise RuntimeError(
            "Thiếu OPENAI_API_KEY. Với Ollama, dùng giá trị giả `ollama`; "
            "với OpenAI, sao chép .env.example thành .env và điền key."
        )
```

Gọi helper này trong `embeddings.py` và `rag.py` trước khi gọi API. UI hiển thị thông báo thân thiện.

## 5. Trường hợp biên

- `.env` không tồn tại → dùng default Ollama (`OPENAI_API_KEY=ollama`); nếu dùng OpenAI mà key rỗng thì báo khi gọi AI.
- Biến môi trường sai kiểu (`MAX_UPLOAD_MB=abc`) → pydantic báo lỗi rõ.
- `DATA_DIR` là file → `mkdir` lỗi; thông báo rõ.
- `EMBEDDING_DIM` đổi nhưng Qdrant collection cũ → S-05 báo mismatch.
- Key chứa khoảng trắng/newline → strip khi đọc? Ghi chú: dùng `.strip()` trong adapter.

## 6. Tiêu chí xong

- [ ] `get_settings()` trả `Settings` với default đúng.
- [ ] `.env` override được default.
- [ ] Tạo `data/uploads` tự động.
- [ ] Validate bắt được dim/top_k/overlap/score sai.
- [ ] `repr(settings)` không chứa API key.
- [ ] `require_api_key` báo lỗi tiếng Việt rõ ràng.

## 7. Test

`tests/test_config.py`:

- `test_defaults`.
- `test_env_override` (monkeypatch env, clear cache).
- `test_invalid_dim_raises`.
- `test_overlap_must_be_smaller`.
- `test_score_threshold_range`.
- `test_require_api_key_raises`.
- `test_data_dirs_created` (tmp_path).

## 8. Tham chiếu

- Kế hoạch §3.3, §5.1.
- S-05, S-09, S-16.
