# S-04 — SQLite schema và CRUD tài liệu

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01, US-04, US-05, US-06 |
| Phase | P0 |
| Tầng | INFRA |
| Ước lượng | 0,5d |
| Phụ thuộc | S-01 |
| Chặn | S-11, S-12, S-19 |
| Owner gợi ý | Backend |

## 1. Mục tiêu

Có lớp lưu metadata tài liệu bằng SQLite: tạo DB, insert khi upload, cập nhật trạng thái `PROCESSING → READY/ERROR`, list và xoá. Không cần ORM; dùng `sqlite3` chuẩn để giảm dependency.

## 2. Phạm vi

**Làm:**

- `app/db.py`: schema, connection, CRUD.
- `Document` dataclass + `DocumentStatus` enum.
- `init_db()` idempotent.
- Index/FTS không cần.
- WAL mode để đọc/ghi đơn giản.

**Không làm:**

- Không lưu chat history (dùng `st.session_state`).
- Không migration phức tạp; schema v1 dùng `CREATE TABLE IF NOT EXISTS`.
- Không multi-user/owner.

## 3. File chính

```text
app/db.py
tests/test_db.py
```

## 4. Đặc tả

### 4.1 Schema

```sql
CREATE TABLE IF NOT EXISTS documents (
    id            TEXT PRIMARY KEY,
    file_name     TEXT NOT NULL,
    stored_path   TEXT NOT NULL,
    size_bytes    INTEGER NOT NULL,
    page_count    INTEGER,
    status        TEXT NOT NULL CHECK (status IN ('PROCESSING', 'READY', 'ERROR')),
    error_code    TEXT,
    created_at    TEXT NOT NULL,
    processed_at  TEXT
);

CREATE INDEX IF NOT EXISTS idx_documents_created_at
    ON documents(created_at DESC);
```

### 4.2 DTO

```python
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

class DocumentStatus(StrEnum):
    PROCESSING = "PROCESSING"
    READY = "READY"
    ERROR = "ERROR"

@dataclass(frozen=True)
class Document:
    id: str
    file_name: str
    stored_path: Path
    size_bytes: int
    page_count: int | None
    status: DocumentStatus
    error_code: str | None
    created_at: str
    processed_at: str | None
```

### 4.3 Hàm công khai

```python
def init_db() -> None: ...
def create_document(doc_id: str, file_name: str, stored_path: Path, size_bytes: int) -> None: ...
def mark_ready(doc_id: str, page_count: int) -> None: ...
def mark_error(doc_id: str, error_code: str) -> None: ...
def get_document(doc_id: str) -> Document | None: ...
def list_documents() -> list[Document]: ...
def delete_document(doc_id: str) -> None: ...
def count_ready_documents() -> int: ...
```

### 4.4 Connection pattern

```python
from contextlib import contextmanager
import sqlite3
from app.config import get_settings

@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    db_path = get_settings().db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

**Quy ước:**

- `created_at` / `processed_at`: `datetime.now(timezone.utc).isoformat(timespec="seconds")`.
- `stored_path` lưu **tuyệt đối** hoặc tương đối từ repo? Chọn tuyệt đối (`str(path.resolve())`) để tránh phụ thuộc cwd; khi đọc trả `Path`.
- `create_document` set `status='PROCESSING'`, `page_count=NULL`, `error_code=NULL`, `processed_at=NULL`.
- `mark_ready` set `status='READY'`, `page_count`, `error_code=NULL`, `processed_at=now`.
- `mark_error` set `status='ERROR'`, `error_code`, `processed_at=now`; giữ `page_count` nếu đã có.
- `delete_document` xoá row; không raise nếu không tồn tại (idempotent).
- `list_documents` order `created_at DESC, id DESC`.

### 4.5 Map row → Document

```python
def _row_to_document(row: sqlite3.Row) -> Document:
    return Document(
        id=row["id"],
        file_name=row["file_name"],
        stored_path=Path(row["stored_path"]),
        size_bytes=row["size_bytes"],
        page_count=row["page_count"],
        status=DocumentStatus(row["status"]),
        error_code=row["error_code"],
        created_at=row["created_at"],
        processed_at=row["processed_at"],
    )
```

### 4.6 Ví dụ dùng

```python
init_db()
create_document(doc_id, "hop-dong.pdf", path, size)
try:
    ...
    mark_ready(doc_id, page_count=32)
except PdfError as e:
    mark_error(doc_id, e.code)
```

## 5. Trường hợp biên

- `init_db()` gọi nhiều lần → không lỗi, không mất dữ liệu.
- `doc_id` trùng → `sqlite3.IntegrityError`; caller phải dùng uuid mới.
- DB bị lock do tiến trình khác → timeout 10s, lỗi rõ.
- `stored_path` không tồn tại → vẫn lưu metadata; kiểm tra file ở tầng ingest.
- `status` ngoài enum → CHECK constraint chặn.
- Xoá document không tồn tại → không lỗi.
- Thư mục `data/` bị xoá khi app đang chạy → connection mới tạo lại; nếu file DB bị xoá, dữ liệu mất (chấp nhận).

## 6. Tiêu chí xong

- [ ] `init_db()` tạo bảng + index, idempotent.
- [ ] CRUD đủ 7 hàm trên.
- [ ] Insert → `PROCESSING`; mark_ready → `READY` + page_count; mark_error → `ERROR` + code.
- [ ] `list_documents()` mới nhất trước.
- [ ] `delete_document()` idempotent.
- [ ] Không dùng `datetime.utcnow()` (deprecated); dùng timezone-aware UTC.
- [ ] Test dùng `tmp_path` + monkeypatch `DATA_DIR`, không đụng DB thật.

## 7. Test

`tests/test_db.py`:

- `test_init_idempotent`.
- `test_create_and_get`.
- `test_mark_ready`.
- `test_mark_error`.
- `test_list_order`.
- `test_delete_idempotent`.
- `test_duplicate_id_raises`.
- `test_count_ready_documents`.

## 8. Tham chiếu

- Kế hoạch §5.1, §7.5.
- S-11, S-12, S-19.
