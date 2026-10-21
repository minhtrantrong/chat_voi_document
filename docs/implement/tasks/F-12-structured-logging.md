# F-12 — Structured logging JSON và lọc dữ liệu nhạy cảm

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng dùng chung (Implement_plan §15) |
| Sprint | S0 |
| Tầng | INF (shared) |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | PLT-01, PLT-05 |
| Chặn | PLT-09, T-22-4 |

## Bối cảnh

SADD §5.9.3: log JSON có `ts, level, service, env, corr_id, user_id_hash, route, event, duration_ms, error_code`; **không** log câu hỏi, câu trả lời, chunk, tên tệp đầy đủ.

## Phạm vi

**Làm:** `app/shared/logging.py` gồm `configure_logging(service: str)`, contextvar `corr_id`, processor lọc khoá cấm, hàm `hash_id`.

## Đặc tả

```python
corr_id_var: ContextVar[str | None] = ContextVar("corr_id", default=None)
FORBIDDEN_KEYS = frozenset({"question", "answer", "text", "content", "chunk", "chunk_text",
                            "file_name", "quote", "reason", "prompt", "history", "draft"})

def configure_logging(service: str, level: str = "INFO") -> None:
    # structlog: merge_contextvars → add service/env → redact_forbidden → TimeStamper(iso, utc) → JSONRenderer
def redact_forbidden(_, __, event_dict):   # thay giá trị khoá cấm bằng f"<redacted len={len(str(v))}>"
def hash_id(value: str | UUID) -> str:     # sha256(value + LOG_HASH_SALT)[:16], dùng cho user_id_hash
```

- Logging chuẩn của thư viện (`logging`) được route qua structlog để log của SQLAlchemy/httpx cũng là JSON; đặt `sqlalchemy.engine` ở mức WARNING (không in tham số SQL).
- httpx/openai client: tắt log request body.
- Gọi `configure_logging("web" | "worker-answer" | "worker-ingest" | "ops")` ở mỗi entrypoint.

## Tiêu chí xong

- [ ] `log.info("x", question="bí mật")` cho ra JSON có `"question": "<redacted len=6>"`.
- [ ] Mỗi dòng log có `service`, `env`, `ts`; có `corr_id` khi contextvar được gán.
- [ ] Log SQLAlchemy không chứa giá trị tham số.

## Test

`tests/unit/shared/test_logging.py` dùng `capsys`/`structlog.testing.capture_logs`.

## Tham chiếu

SADD §5.8.6 (Logs), §5.9.3 · NFR-SEC-02
