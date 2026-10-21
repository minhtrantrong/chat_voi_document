# F-01 — Shared kernel: Actor, Role, Page, UUIDv7, Clock

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng dùng chung (Implement_plan §15) |
| Sprint | S0 |
| Tầng | DOM |
| Ước lượng | 0.5d |
| Owner gợi ý | Tech Lead |
| Phụ thuộc | PLT-01 |
| Chặn | Gần như mọi task APP/DOM |

## Bối cảnh

Mọi use case nhận `Actor` (SADD §5.7.2) và trả DTO. ID dùng UUIDv7 (§5.4.2), thời gian qua `Clock` có thể thay khi test (§5.5.2).

## Phạm vi

**Làm:** `app/shared/types.py`, `app/shared/ids.py`, `app/shared/clock.py`.

## Đặc tả

```python
# app/shared/types.py
class Role(StrEnum):
    END_USER = "END_USER"; PM = "PM"; ADMIN = "ADMIN"

@dataclass(frozen=True, slots=True)
class Actor:
    user_id: UUID
    role: Role
    session_id: str
    @property
    def is_admin(self) -> bool: return self.role is Role.ADMIN

SYSTEM_SESSION = "system"
def system_actor(user_id: UUID) -> Actor:            # worker hành động thay mặt chủ hội thoại
    return Actor(user_id=user_id, role=Role.END_USER, session_id=SYSTEM_SESSION)

T = TypeVar("T")
@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    items: list[T]
    next_cursor: str | None

def encode_cursor(ts: datetime, id_: UUID) -> str      # base64url("<iso8601>|<uuid>")
def decode_cursor(cursor: str) -> tuple[datetime, UUID] # cursor hỏng → raise Invalid(ERR_DOC_422) (F-02)
```

```python
# app/shared/ids.py
def new_id() -> UUID:   # UUIDv7 qua uuid_utils.uuid7(), trả về uuid.UUID chuẩn
```

```python
# app/shared/clock.py
VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
class Clock(Protocol):
    def now(self) -> datetime: ...            # luôn aware UTC
class SystemClock:
    def now(self) -> datetime: return datetime.now(UTC)
class FrozenClock:                            # cho test
    def __init__(self, at: datetime) -> None: ...
    def advance(self, **kw: float) -> None: ...
def to_vn(dt: datetime) -> datetime: return dt.astimezone(VN_TZ)
def today_vn(clock: Clock) -> date: return to_vn(clock.now()).date()
```

Quy tắc: không module nào khác gọi `datetime.now()` hoặc `uuid.uuid4()`; ruff rule `DTZ` (PLT-02) hỗ trợ bắt lỗi.

## Tiêu chí xong

- [ ] Mypy strict xanh.
- [ ] `new_id()` sinh ID tăng dần theo thời gian (so sánh 1.000 ID liên tiếp).
- [ ] Cursor round-trip đúng; cursor rác bị từ chối bằng `Invalid`.

## Test

`tests/unit/shared/test_types.py`, `test_ids.py`, `test_clock.py`.

## Tham chiếu

SADD §1.3 (Actor), §5.4.2, §5.5.2, §5.7.2
