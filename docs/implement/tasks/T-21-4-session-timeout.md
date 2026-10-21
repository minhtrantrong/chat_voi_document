# T-21-4 — Thời hạn phiên: idle 8 giờ, tối đa 12 giờ

| Thuộc tính | Giá trị |
|---|---|
| Story | US-21 (P0) — AC-21.2 |
| Sprint | S1 |
| Tầng | APP / INF |
| Ước lượng | 1d (gồm spike xác nhận claim `iat`) |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | T-21-3, Redis client (PLT-04) |
| Chặn | T-21-6 |

## Bối cảnh

SADD §5.8.2 yêu cầu idle timeout 8 h và absolute 12 h. Cookie đăng nhập của Streamlit có thời hạn dài hơn nhiều, nên ứng dụng phải tự áp thời hạn.

## Phạm vi

**Làm:** `SessionPolicy` (domain) + `SessionTracker` (Redis) + hàm `check_session_timeout(actor)` gọi trong `auth_guard` (T-21-2).

**Không làm:** giao diện SCR-10 và giữ nháp (T-21-6).

## Đặc tả

**Spike (0.25d, làm trước):** đăng nhập với IdP thật/staging, in danh sách khoá của `st.user` (chỉ tên khoá, không giá trị) để xác nhận có `iat`. Ghi kết quả vào PR.

```python
# app/identity/domain.py
@dataclass(frozen=True)
class SessionPolicy:
    idle: timedelta = timedelta(hours=8)
    absolute: timedelta = timedelta(hours=12)
    def is_expired(self, login_at: datetime, last_seen: datetime | None, now: datetime) -> bool:
        return now - login_at > self.absolute or (last_seen is not None and now - last_seen > self.idle)
```

Redis (`app/infrastructure/redis/session_tracker.py`), khoá theo `h = hash_id(sub)` và `iat`:

| Khoá | Giá trị | TTL |
|---|---|---|
| `sess:{h}:{iat}:login_at` | epoch giây | 12 h |
| `sess:{h}:{iat}:last_seen` | epoch giây | 8 h (gia hạn mỗi lần tương tác) |

```text
check_session_timeout(claims):
  login_at = claims.iat  (nếu không có iat: GET login_at; chưa có thì SET NX = now)
  last_seen = GET last_seen
  if policy.is_expired(login_at, last_seen, now): đặt K.AUTH_EXPIRED = True; render_session_expired(); st.stop()  # T-21-6
  SET last_seen = now EX 8h
```

- "Tương tác" = mỗi lần script chạy do người dùng (không tính rerun do fragment `run_every`). Trong fragment, **không** gọi `check_session_timeout`.
- Redis lỗi: **fail open có kiểm soát** — cho phép tiếp tục nhưng log warn `session_tracker_unavailable`. Lý do: cookie OIDC vẫn hợp lệ; chặn toàn bộ người dùng khi Redis lỗi là quá khắt khe. Ghi rõ quyết định này trong PR để Security xác nhận.

## Tiêu chí xong

- [ ] Kết quả spike được ghi lại.
- [ ] FrozenClock: không tương tác 8 h 1 phút thì hết phiên; tương tác đều đặn 12 h 1 phút thì vẫn hết phiên.
- [ ] Fragment poll không làm gia hạn `last_seen`.

## Test

`tests/unit/identity/test_session_policy.py`; `tests/integration/identity/test_session_tracker.py` (Redis testcontainer, FrozenClock).

## Tham chiếu

SADD §5.8.2 · US-21 AC-21.2 · NIST SP 800-63B
