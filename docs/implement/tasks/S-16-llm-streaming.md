# S-16 — Gọi LLM streaming qua API OpenAI-compatible

| Thuộc tính | Giá trị |
|---|---|
| Story | US-07, US-08, US-09 |
| Phase | P2 |
| Tầng | APP |
| Ước lượng | 0,5d |
| Phụ thuộc | S-03 |
| Chặn | S-17, S-18 |
| Owner gợi ý | Backend |

## 1. Mục tiêu

Adapter gọi chat completion ở chế độ streaming, trả từng token qua generator, có retry an toàn trước khi token đầu tiên được phát ra và lỗi được map thành `LLMError`. Hỗ trợ OpenAI, Ollama, vLLM qua `OPENAI_BASE_URL`.

## 2. Phạm vi

**Làm:**

- `app/llm.py`: `stream_chat(messages) -> Iterator[str]`.
- `LLMError`.
- Retry 2 lần cho lỗi kết nối/timeout/rate limit **trước khi** yield token đầu.
- Không retry nếu đã phát token (tránh lặp câu trả lời).
- Kiểm tra API key bằng `require_api_key`.
- Temperature thấp (`0.1`).

**Không làm:**

- Không build prompt (S-17).
- Không parse citations (S-20).
- Không hỗ trợ tool calling/function calling.
- Không lưu lịch sử.

## 3. File chính

```text
app/llm.py
tests/test_llm.py
```

## 4. Đặc tả

### 4.1 Lỗi

```python
class LLMError(Exception):
    def __init__(self, message: str, *, code: str = "LLM_FAILED"):
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
        max_retries=0,
    )
```

### 4.3 Stream

```python
import time
from collections.abc import Iterator
from openai import APIConnectionError, APITimeoutError, RateLimitError


def stream_chat(
    messages: list[dict[str, str]],
    *,
    client: OpenAI | None = None,
) -> Iterator[str]:
    s = get_settings()
    client = client or _client()
    emitted = False

    for attempt in range(2):
        try:
            stream = client.chat.completions.create(
                model=s.llm_model,
                messages=messages,
                temperature=0.1,
                stream=True,
            )
            got_any = False
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                text = getattr(delta, "content", None)
                if text:
                    got_any = True
                    emitted = True
                    yield text
            if not got_any:
                raise LLMError("Mô hình không trả về nội dung.")
            return
        except LLMError:
            raise
        except (APIConnectionError, APITimeoutError, RateLimitError) as exc:
            if emitted or attempt == 1:
                raise LLMError("Trợ lý tạm thời không phản hồi. Thử lại sau.") from exc
            time.sleep(2**attempt)
        except Exception as exc:
            raise LLMError(f"Lỗi gọi mô hình: {type(exc).__name__}") from exc

    raise LLMError("Trợ lý tạm thời không phản hồi. Thử lại sau.")
```

### 4.4 Định dạng `messages`

```python
[
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "..."},
]
```

Không gửi field lạ; OpenAI-compatible server có thể từ chối.

## 5. Trường hợp biên

- API key thiếu → `RuntimeError` từ `require_api_key`; S-18 map thành `CONFIG_MISSING` hoặc `LLM_FAILED`.
- Model trả chunk `choices=[]` (một số server) → bỏ qua.
- `delta.content=None` → bỏ qua.
- Stream rỗng hoàn toàn → `LLMError`.
- Lỗi giữa stream sau khi đã phát token → `LLMError`; UI hiển thị lỗi, không retry (tránh lặp).
- Rate limit trước token → retry 1 lần; nếu vẫn lỗi → `LLMError`.
- Timeout 60s → retry nếu chưa phát token.
- Ollama trả `content` từng token; vLLM tương tự.
- `messages` rỗng → gửi đi; server có thể lỗi; caller phải đảm bảo có system/user.
- Câu trả lời rất dài → không giới hạn trong adapter; UI tự xử lý.
- Hủy giữa chừng (đóng tab) → generator bị đóng; không cần cleanup đặc biệt.

## 6. Tiêu chí xong

- [ ] Stream trả đúng thứ tự token.
- [ ] Không retry sau khi đã phát token.
- [ ] Retry trước token cho lỗi tạm thời.
- [ ] Lỗi map `LLMError`, không lộ stack trace.
- [ ] Không log prompt/câu trả lời.
- [ ] Test bằng fake client, không gọi mạng.

## 7. Test

`tests/test_llm.py` dùng fake client:

```python
class FakeCompletions:
    def create(self, **kwargs):
        return iter([
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="Xin "))]),
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="chào"))]),
        ])

class FakeClient:
    def __init__(self): self.chat = SimpleNamespace(completions=FakeCompletions())
```

- `test_stream_tokens`.
- `test_skip_empty_choices`.
- `test_empty_stream_raises`.
- `test_retry_before_first_token`.
- `test_no_retry_after_first_token` (fake raise sau 1 token, assert chỉ nhận 1 token rồi lỗi).
- `test_rate_limit_exhausted`.
- `test_non_retryable_error_wrapped`.

## 8. Tham chiếu

- Kế hoạch §3.3, §7.4.
- S-03, S-17, S-18.
