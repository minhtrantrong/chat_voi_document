# T-01-3 — Domain Document: entity, trạng thái, chính sách upload

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01 (P0); dùng chung US-04, US-06 |
| Sprint | S2 |
| Tầng | DOM |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | F-01, F-02 |
| Chặn | T-01-4, T-04-6, T-06-1, T-02-1 |

## Bối cảnh

State machine Document ở SADD §5.3.8; quy tắc DR-01, DR-06. Domain không import framework (PLT-02).

## Phạm vi

**Làm:** `app/documents/domain.py`: `DocumentStatus`, `Visibility`, `Document`, `UploadPolicy`, `next_copy_name`, `InvalidTransition`. (Phần `mark_deleting` chi tiết thuộc T-06-1 nhưng có thể làm luôn ở đây.)

## Đặc tả

```python
class DocumentStatus(StrEnum):
    PROCESSING = "PROCESSING"; READY = "READY"; ERROR = "ERROR"; DELETING = "DELETING"; DELETED = "DELETED"

ALLOWED = {
    PROCESSING: {READY, ERROR, DELETING},
    READY: {DELETING},
    ERROR: {PROCESSING, DELETING},
    DELETING: {DELETING, DELETED},
    DELETED: set(),
}

@dataclass
class Document:
    id: UUID; owner_id: UUID; file_name: str; size_bytes: int; page_count: int | None
    storage_key: str; checksum: str; visibility: Visibility; status: DocumentStatus
    error_code: str | None; uploaded_at: datetime; ready_at: datetime | None
    deleted_at: datetime | None; version: int

    def transition(self, to: DocumentStatus) -> None   # không hợp lệ → raise InvalidTransition
    def mark_ready(self, page_count: int, now: datetime) -> None
    def mark_error(self, code: str) -> None
    def mark_retry(self) -> None                         # ERROR → PROCESSING, error_code=None, version += 1
    def mark_deleting(self, now: datetime) -> None       # → DELETING, deleted_at=now
    @property
    def is_active(self) -> bool: return self.deleted_at is None

class UploadPolicy:
    @staticmethod
    def check_name(name: str) -> DocErrorCode | None      # không kết thúc .pdf (không phân biệt hoa thường) → PDF_NOT_PDF
    @staticmethod
    def check_size(size: int, limits: Limits) -> tuple[DocErrorCode, dict] | None   # PDF_TOO_LARGE {limit_mb, actual_mb (1 chữ số thập phân)}
    @staticmethod
    def check_pages(pages: int, limits: Limits) -> tuple[DocErrorCode, dict] | None # PDF_TOO_MANY_PAGES {limit, actual}

def next_copy_name(name: str, existing: set[str]) -> str:
    """'hop-dong.pdf' → 'hop-dong (2).pdf', rồi (3)…; so sánh không phân biệt hoa thường."""
```

- `size == 0` → `PDF_NOT_PDF` (tệp rỗng không phải PDF).
- `file_name` được chuẩn hoá: Unicode NFC, bỏ ký tự điều khiển, bỏ đường dẫn (`PurePath(name).name`), tối đa 255 ký tự (giữ phần đuôi `.pdf`).

## Tiêu chí xong

- [ ] Mọi chuyển trạng thái hợp lệ/không hợp lệ có test.
- [ ] `next_copy_name` đúng khi đã tồn tại `(2)`, `(3)`; tên không có đuôi chuẩn.
- [ ] Mypy strict, không import framework.

## Test

`tests/unit/documents/test_domain.py`.

## Tham chiếu

SADD §5.2.4 (DR-01, DR-06), §5.3.8 · Implement_plan §14 C-12
