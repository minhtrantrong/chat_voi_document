# T-04-3 — Adapter Embedding, cache theo nội dung và bản giả cho test

| Thuộc tính | Giá trị |
|---|---|
| Story | US-04 (P0); dùng ở US-07/US-09 (embed câu hỏi) |
| Sprint | S2 |
| Tầng | INF |
| Ước lượng | 1d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | PLT-05, T-22-2, Redis client |
| Chặn | T-04-4, T-09-1 |

## Bối cảnh

ADR-009: provider qua port. SADD §5.3.3: embedding cache theo `sha256(model + text)` để không embed lại khi retry; §5.7.6: timeout 5/30 s, retry 3, breaker 60 s.

## Phạm vi

**Làm:** `EmbeddingPort`, `OpenAICompatibleEmbedding` (httpx), `CachedEmbedding` (decorator), `FakeEmbedding`, factory (T-22-2).

## Đặc tả

```python
class EmbeddingPort(Protocol):
    model: str
    dim: int
    def embed(self, texts: list[str], *, timeout_s: float = 30) -> list[list[float]]: ...
```

`OpenAICompatibleEmbedding`:
- `POST {base_url}/embeddings` body `{"model": m, "input": texts}`; header `Authorization: Bearer`.
- Chia lô theo `EMBEDDING_BATCH_SIZE` (64).
- Retry 3 lần với backoff 0.5/1/2 s cho 429/5xx/timeout; 4xx khác → không retry.
- Kiểm tra `len(vector) == dim`; sai → `RetryableJobError(EMBED_FAILED)` không, đây là lỗi cấu hình → `PermanentJobError(EMBED_FAILED, "dim_mismatch")` và log error.
- Lỗi cuối cùng → ném `EmbeddingUnavailable` (service chuyển thành `RetryableJobError(EMBED_FAILED)` trong ingest, hoặc `Unavailable` trong QA).
- Metric `cvd_llm_requests_total{provider, model}` (dùng chung nhóm LLM, `kind="embedding"` qua label `model`).

`CachedEmbedding(inner, redis, ttl_days=30)`:
- Khoá `emb:{sha256(model + "\n" + text)}`, giá trị `array("f", vec).tobytes()`.
- `MGET` cho cả lô; chỉ gọi `inner.embed` cho phần thiếu; `SET` pipeline với `EX`.
- Redis lỗi → bỏ qua cache (log warn), vẫn gọi provider.

`FakeEmbedding(dim=1536)`: vector tất định từ hash của text (chuẩn hoá L2), cộng thêm thành phần theo **từ khoá chung** để hai câu có từ giống nhau có cosine cao — đủ để test retrieval có ý nghĩa.

## Tiêu chí xong

- [ ] Contract test (respx) với response mẫu: đúng thứ tự vector, đúng lô.
- [ ] Gọi `embed` hai lần cùng text → lần hai không gọi HTTP (cache hit).
- [ ] 503 ba lần → ném lỗi sau ~3.5 s; breaker mở sau 5 lần lỗi liên tiếp.

## Test

`tests/contract/test_embedding_adapter.py` (respx); `tests/integration/test_embedding_cache.py` (Redis); `tests/unit/test_fake_embedding.py`.

## Tham chiếu

ADR-009 · SADD §5.3.3, §5.7.3, §5.7.6 · T-22-2
