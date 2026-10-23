# S-09 — Embedding batch qua API OpenAI-compatible

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01, US-08, US-09 |
| Phase | P1 |
| Tầng | APP |
| Ước lượng | 0,5d |
| Phụ thuộc | S-03 |
| Chặn | S-10, S-11, S-15 |
| Owner gợi ý | Backend |

## 1. Mục tiêu

Chuyển text thành vector bằng API tương thích OpenAI, theo batch, có retry cho lỗi tạm thời và kiểm tra chiều vector khớp `EMBEDDING_DIM`. Hỗ trợ cả OpenAI, Ollama, vLLM qua `OPENAI_BASE_URL`.

## 2. Phạm vi

**Làm:**

- `app/embeddings.py`: `embed_texts`, `embed_query`.
- Batch theo `EMBEDDING_BATCH_SIZE`.
- Retry 3 lần với exponential backoff cho lỗi kết nối/timeout/rate limit.
- Validate dimension.
- `EmbeddingError` với code `EMBEDDING_FAILED`.
- Inject client optional để test.

**Không làm:**

- Cache vector.
- Local embedding model (chỉ gọi API).
- Token counting/truncate tự động; caller đảm bảo chunk vừa model.

## 3. File chính

```text
app/embeddings.py
tests/test_embeddings.py
```

## 4. Đặc tả

### 4.1 Lỗi

```python
class EmbeddingError(Exception):
    def __init__(self, message: str, *, code: str = "EMBEDDING_FAILED"):
        self.code = code
        self.message = message
        super().__init__(message)
```

### 4.2 Client

```python
from openai import OpenAI
from app.config import get_settings, require_api_key

def _client() -> OpenAI:
    s = get_settings()
    require_api_key(s)
    return OpenAI(
        api_key=s.openai_api_key.strip(),
        base_url=s.openai_base_url.rstrip("/"),
        timeout=60.0,
        max_retries=0,   # tự retry để kiểm soát
    )
```

### 4.3 Embed texts

```python
import time
from openai import APIConnectionError, APITimeoutError, RateLimitError

def embed_texts(
    texts: list[str],
    *,
    client: OpenAI | None = None,
) -> list[list[float]]:
    if not texts:
        return []
    s = get_settings()
    client = client or _client()
    out: list[list[float]] = []

    for i in range(0, len(texts), s.embedding_batch_size):
        batch = texts[i : i + s.embedding_batch_size]
        if any(not t.strip() for t in batch):
            raise EmbeddingError("Không thể embedding text rỗng.")

        resp = None
        for attempt in range(3):
            try:
                resp = client.embeddings.create(
                    model=s.embedding_model,
                    input=batch,
                )
                break
            except (APIConnectionError, APITimeoutError, RateLimitError) as exc:
                if attempt == 2:
                    raise EmbeddingError(
                        "Dịch vụ embedding tạm thời không phản hồi. Thử lại sau."
                    ) from exc
                time.sleep(2**attempt)
            except Exception as exc:
                raise EmbeddingError(f"Lỗi embedding: {type(exc).__name__}") from exc

        if resp is None:
            raise EmbeddingError("Không nhận được phản hồi embedding.")
        items = sorted(resp.data, key=lambda d: d.index)
        vectors = [item.embedding for item in items]
        for vec in vectors:
            if len(vec) != s.embedding_dim:
                raise EmbeddingError(
                    f"Vector có {len(vec)} chiều, cấu hình EMBEDDING_DIM={s.embedding_dim}. "
                    "Kiểm tra lại EMBEDDING_MODEL và EMBEDDING_DIM."
                )
        out.extend(vectors)

    return out
```

### 4.4 Embed query

```python
def embed_query(text: str, *, client: OpenAI | None = None) -> list[float]:
    if not text.strip():
        raise EmbeddingError("Câu hỏi rỗng.")
    return embed_texts([text], client=client)[0]
```

## 5. Trường hợp biên

- `texts=[]` → `[]`, không gọi API.
- Text rỗng/toàn khoảng trắng trong batch → `EmbeddingError` trước khi gọi API.
- API key thiếu → `RuntimeError` từ `require_api_key`; UI map thành "Chưa cấu hình API key".
- Model trả ít/many vector hơn input → phát hiện bằng `len(vectors) != len(batch)`; thêm check:
  ```python
  if len(vectors) != len(batch):
      raise EmbeddingError("Số vector trả về không khớp số input.")
  ```
- Vector sai chiều → lỗi hướng dẫn đổi `EMBEDDING_DIM` hoặc model.
- Rate limit → retry 3 lần; nếu vẫn lỗi → thông báo.
- Timeout → retry.
- Lỗi 400 (model sai) → raise ngay, không retry vô ích.
- Ollama không hỗ trợ batch lớn → giảm `EMBEDDING_BATCH_SIZE` trong `.env`.
- `base_url` có dấu `/` cuối → strip.

## 6. Tiêu chí xong

- [ ] Batch đúng kích thước, giữ thứ tự vector.
- [ ] Retry chỉ cho lỗi tạm thời; lỗi cấu hình raise ngay.
- [ ] Validate dimension và số lượng vector.
- [ ] Không log text/vector; chỉ log batch size, model, thời gian.
- [ ] Test không gọi mạng thật.

## 7. Test

`tests/test_embeddings.py` dùng fake client:

```python
class FakeEmbeddings:
    def create(self, *, model, input):
        return SimpleNamespace(data=[
            SimpleNamespace(index=i, embedding=[0.1] * dim)
            for i, _ in enumerate(input)
        ])
```

- `test_empty_returns_empty`.
- `test_single_text`.
- `test_batch_order_preserved`.
- `test_dimension_mismatch_raises`.
- `test_count_mismatch_raises`.
- `test_blank_text_raises`.
- `test_retry_then_success` (fake raise 2 lần rồi OK; monkeypatch `time.sleep`).
- `test_rate_limit_exhausted_raises`.
- `test_embed_query_empty_raises`.

## 8. Tham chiếu

- Kế hoạch §3.3, §7.3.
- S-10, S-11, S-15.
