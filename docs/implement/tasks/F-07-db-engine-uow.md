# F-07 — Engine DB, Unit of Work và repository base

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng dùng chung (Implement_plan §15; Phần I §4 S1, mục 1.2) |
| Sprint | S1 |
| Tầng | INF (+ port ở `app/shared/uow.py`) |
| Ước lượng | 1.5d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | PLT-05, PLT-08 |
| Chặn | Mọi repository, F-04, F-05, F-06, F-08 |

## Bối cảnh

SADD §4.4 (Repository + Unit of Work), §5.3.1 (pool, không connection toàn cục), §5.3.9 (transaction ngắn). Service chỉ thấy **port** (Protocol), không import SQLAlchemy (import-linter, PLT-02).

## Phạm vi

**Làm:**
- `app/shared/uow.py`: Protocol `UnitOfWork`, `UnitOfWorkFactory`.
- `app/infrastructure/db/engine.py`: tạo engine + pool.
- `app/infrastructure/db/uow.py`: `SqlUnitOfWork`.
- `app/infrastructure/db/tables.py`: SQLAlchemy Core `Table` khớp schema PLT-08 (Core hoặc ORM typed đều được; **khuyến nghị Core** để kiểm soát SQL rõ ràng).
- Fixture pytest `db_engine`, `uow_factory` (testcontainers) ở `tests/integration/conftest.py`.

## Đặc tả

```python
# app/shared/uow.py
class UnitOfWork(Protocol):
    def execute(self, stmt: Any, params: Mapping[str, Any] | None = None) -> Any: ...
    def scalar(self, stmt: Any, params: Mapping[str, Any] | None = None) -> Any: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def after_commit(self, fn: Callable[[], None]) -> None: ...   # chạy sau khi commit thành công; bỏ qua nếu rollback
    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(self, *exc: object) -> None: ...   # exc → rollback, không exc → commit

UnitOfWorkFactory = Callable[[], UnitOfWork]
```

```python
# app/infrastructure/db/engine.py
def create_db_engine(s: Settings) -> Engine:
    return create_engine(str(s.database_url), pool_size=s.db_pool_size, max_overflow=5,
                         pool_pre_ping=True, pool_recycle=1800,
                         connect_args={"connect_timeout": 5,
                                       "options": f"-c statement_timeout={s.db_statement_timeout_ms}"})
```

- `SqlUnitOfWork` mở `engine.connect()` + `begin()` khi `__enter__`; repository nhận `uow` làm tham số (không giữ connection riêng).
- `after_commit`: callback (gửi Redis, telemetry ngoài transaction) chạy theo thứ tự đăng ký sau khi commit; exception trong callback chỉ log warn, không ảnh hưởng dữ liệu đã commit. Dùng ở T-13-8, T-13-3.
- Repository interface đặt ở `app/<module>/repository.py` (Protocol); bản cài đặt ở `app/infrastructure/db/repositories/<module>.py`.
- Tổng connection: `web(15+5) + worker-answer(15+5) + worker-ingest(15+5) + ops` < `max_connections` (Postgres mặc định 100) — ghi vào `docs/ops` khi PLT-20.
- Hàm tiện ích: `advisory_xact_lock(uow, key: str) -> bool` dùng `pg_try_advisory_xact_lock(hashtext(:k))` (dùng ở T-04-4, T-06-3).

## Tiêu chí xong

- [ ] Exception trong `with uow:` thì rollback; không exception thì commit.
- [ ] Query chạy quá `statement_timeout` bị huỷ và ném lỗi.
- [ ] Mypy strict xanh với `app/shared/uow.py`; core không import `sqlalchemy` (lint-imports xanh).

## Test

`tests/integration/db/test_uow.py`: commit/rollback; `statement_timeout` (`SELECT pg_sleep(…)` với timeout nhỏ); `advisory_xact_lock` hai connection tranh nhau.

## Tham chiếu

SADD §4.4, §5.3.1, §5.3.9, §5.7.6
