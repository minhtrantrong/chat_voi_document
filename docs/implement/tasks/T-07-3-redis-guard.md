# T-07-3 — RedisGuard: ping, rate limit theo người dùng, idempotency

| Thuộc tính | Giá trị |
|---|---|
| Story | US-07 (P0); US-24 (rate limit) |
| Sprint | S3 |
| Tầng | INF |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | Redis client (PLT-04/PLT-05) |
| Chặn | T-07-2 |

## Bối cảnh

SADD §5.3.4: `QaService.ask` kiểm tra Redis trước khi tạo job; rate limit bằng `INCR` + TTL; `Idempotency-Key` lưu ngắn hạn để tránh double-submit do rerun Streamlit, khoá theo `(user_id, conversation_id, key)`.

## Phạm vi

**Làm:** port `AskGuardPort` (`app/qa/ports.py`) và cài đặt `app/infrastructure/redis/ask_guard.py`.

## Đặc tả

```python
class AskGuardPort(Protocol):
    def ping(self) -> bool: ...
    def rate_limit(self, user_id: UUID, per_hour: int) -> tuple[bool, int]: ...   # (ok, retry_after_s)
    def idempotency_get(self, user_id: UUID, conv_id: UUID | None, key: str) -> UUID | None: ...
    def idempotency_set(self, user_id: UUID, conv_id: UUID, key: str, answer_id: UUID) -> None: ...
```

| Thao tác | Lệnh Redis |
|---|---|
| `ping` | `PING` với `socket_timeout=1` |
| `rate_limit` | khoá `rl:ask:{user_id}:{yyyymmddHH theo UTC}`; pipeline `INCR` + `EXPIRE 3600 NX`; `count > per_hour` → `(False, giây còn lại tới đầu giờ sau)` |
| `idempotency_get/set` | khoá `idem:{user_id}:{conv_id or "new"}:{key}`; `SET … NX EX 60` giá trị `answer_id` |

- Lần gửi đầu khi `conversation_id=None` thì key dùng `"new"`; sau khi tạo hội thoại, `idempotency_set` lưu thêm với `conv_id` thật (hai khoá) để lần submit thứ hai (có thể đã có conv id) vẫn khớp.
- Lỗi Redis trong `rate_limit` / `idempotency_*` (sau khi `ping` thành công): log warn và **cho qua** (không chặn người dùng vì lỗi tạm thời); `ping` là chốt chặn chính.
- Bucket theo giờ đồng hồ (fixed window) là đủ cho MVP; ghi chú trong code.

## Tiêu chí xong

- [ ] 30 lần trong cùng giờ OK, lần 31 bị chặn với `retry_after` hợp lý.
- [ ] Idempotency hết hạn sau 60 s.

## Test

`tests/integration/redis/test_ask_guard.py` (Redis testcontainer).

## Tham chiếu

SADD §5.3.4 (Kiểm tra trước khi tạo job), §10.2 `RATE_LIMIT_ASKS_PER_HOUR`
