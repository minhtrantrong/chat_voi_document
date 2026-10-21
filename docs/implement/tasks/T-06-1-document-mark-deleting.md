# T-06-1 — Domain: chuyển tài liệu sang DELETING

| Thuộc tính | Giá trị |
|---|---|
| Story | US-06 — Xoá một tài liệu (P0) |
| Sprint | S2 (làm cùng T-01-3, vì T-01-5 cần) |
| Tầng | DOM |
| Ước lượng | 0.25d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-01-3 |
| Chặn | T-06-2, T-01-5 |

## Bối cảnh

DR-06: xoá có hiệu lực ngay với retrieval: `status=DELETING` + `deleted_at` trong cùng transaction; purge xong mới `DELETED`.

## Phạm vi

**Làm:** `Document.mark_deleting(now)` và test (nếu chưa làm ở T-01-3).

## Đặc tả

```python
def mark_deleting(self, now: datetime) -> None:
    if self.status not in (PROCESSING, READY, ERROR):
        raise InvalidTransition(self.status, DocumentStatus.DELETING)
    self.status = DocumentStatus.DELETING
    self.deleted_at = now
```

- Gọi lại trên tài liệu đã DELETING → `InvalidTransition` (service bắt và trả `NotFound`, vì với người dùng tài liệu đã không còn).

## Tiêu chí xong

- [ ] Từ PROCESSING/READY/ERROR → DELETING, `deleted_at` được gán.
- [ ] Từ DELETING/DELETED → lỗi.

## Test

`tests/unit/documents/test_domain.py::test_mark_deleting_*`.

## Tham chiếu

SADD §5.2.4 DR-06, §5.3.8
