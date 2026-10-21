# T-08-3 — Adapter LLM streaming (openai-compatible) và FakeLLM

| Thuộc tính | Giá trị |
|---|---|
| Story | US-08 (P0); nền cho US-13 |
| Sprint | S3 |
| Tầng | INF |
| Ước lượng | 1.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | PLT-05, T-22-2 |
| Chặn | T-13-3, PLT-15 (tiêm lỗi) |

## Bối cảnh

ADR-009 provider qua port. SADD §5.7.6: LLM connect 5 s, first token 10 s, total 60 s; retry 1 lần **chỉ khi chưa nhận token**; breaker 60 s. Worker phải đóng được stream khi người dùng bấm Dừng.

## Phạm vi

**Làm:** `LLMPort`, `OpenAICompatibleLLM` (httpx SSE, chat completions `stream=true`), `FakeLLM` (kịch bản + tiêm lỗi), factory.

## Đặc tả

```python
@dataclass(frozen=True)
class TokenEvent:
    text: str

@dataclass(frozen=True)
class Usage:
    prompt_tokens: int; completion_tokens: int

class LLMStream(Protocol):
    def __iter__(self) -> Iterator[TokenEvent]: ...
    def close(self) -> None: ...                    # đóng HTTP response ngay
    @property
    def usage(self) -> Usage | None: ...            # có sau khi stream kết thúc

class LLMPort(Protocol):
    provider: str; model: str
    def stream_chat(self, messages: list[ChatMessage], *, max_tokens: int, temperature: float) -> LLMStream: ...

class LLMTimeout(Exception): ...                    # → ERR_LLM_TIMEOUT
class LLMUnavailable(Exception): ...                # 5xx, lỗi mạng, breaker mở → ERR_LLM_UNAVAILABLE
```

`OpenAICompatibleLLM`:
- `POST {base}/chat/completions` với `{"model", "messages", "stream": true, "max_tokens", "temperature", "stream_options": {"include_usage": true}}`.
- `httpx.Client(timeout=httpx.Timeout(connect=5, read=10, write=10, pool=5))`; đo **tổng** 60 s bằng deadline riêng; hết deadline → `close()` + `LLMTimeout`.
- Token đầu không đến trong 10 s → `LLMTimeout` (read timeout của chunk đầu).
- Retry: lỗi trước khi nhận token đầu (connect error, 5xx, 429) → thử lại 1 lần sau 1 s; đã có token thì **không** retry.
- Breaker dùng chung `app/shared/breaker.py`.
- Metric `cvd_llm_requests_total`, `cvd_llm_tokens_total{kind=prompt|completion}`, `cvd_llm_errors_total{reason}`.
- Không log `messages`.

`FakeLLM` (`app/infrastructure/llm/fake.py`):
- Kịch bản từ env `LLM_FAKE_SCRIPT` hoặc tham số: `echo_sources` (mặc định: trả lời bằng câu đầu tiên của nguồn S1 kèm `[S1]`), `not_found`, `no_markers`, `fixed:<text>`.
- Tốc độ: `LLM_FAKE_TOKEN_MS` (mặc định 30 ms/token).
- Tiêm lỗi `LLM_FAULT` (PLT-15): `timeout_first_token`, `http_503`, `drop_midstream`, `slow_stream:<ms>`.
- Ghi lại `last_messages` để test kiểm tra prompt (T-16-2).

## Tiêu chí xong

- [ ] Contract test respx với stream SSE ghi sẵn: nhận đúng chuỗi token và usage.
- [ ] `close()` giữa stream đóng kết nối (respx xác nhận stream không bị đọc tiếp).
- [ ] 503 trước token đầu → retry 1 lần; 503 lần hai → `LLMUnavailable`.
- [ ] Không có token trong 10 s → `LLMTimeout`.

## Test

`tests/contract/test_llm_adapter.py`; `tests/unit/test_fake_llm.py`.

## Tham chiếu

ADR-009 · SADD §5.7.3, §5.7.6, §5.8.5 · PLT-15
