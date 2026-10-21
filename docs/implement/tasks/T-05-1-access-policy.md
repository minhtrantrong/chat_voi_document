# T-05-1 — AccessPolicy cho tài liệu

| Thuộc tính | Giá trị |
|---|---|
| Story | US-05 — Xem danh sách tài liệu được phép hỏi (P0) — AC-05.2; dùng chung US-06, US-13d, US-21 |
| Sprint | S2 |
| Tầng | DOM |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | F-01, T-01-3 |
| Chặn | T-05-2, T-04-6, T-06-2, T-13d-2, T-13c-2 |

## Bối cảnh

SADD §5.8.3 bảng phân quyền; quyết định **C-10** (mặc định PRIVATE), **C-11** (ADMIN thấy danh sách như người thường, truy cập tài liệu người khác có audit).

## Phạm vi

**Làm:** `app/documents/domain.py::AccessPolicy` (hàm thuần, không I/O).

## Đặc tả

```python
class AccessPolicy:
    @staticmethod
    def can_view(actor: Actor, doc: Document) -> bool:
        if not doc.is_active: return False
        return doc.owner_id == actor.user_id or doc.visibility is Visibility.SHARED or actor.is_admin

    @staticmethod
    def can_delete(actor: Actor, doc: Document) -> bool:
        return doc.is_active and (doc.owner_id == actor.user_id or actor.is_admin)

    @staticmethod
    def needs_admin_audit(actor: Actor, doc: Document) -> bool:
        return actor.is_admin and doc.owner_id != actor.user_id and doc.visibility is Visibility.PRIVATE

    @staticmethod
    def list_filter(actor: Actor) -> ListFilter:
        """Danh sách chính: của mình + SHARED (kể cả ADMIN, C-11)."""
        return ListFilter(owner_id=actor.user_id, include_shared=True)
```

- PM có quyền tài liệu như END_USER (SADD §5.8.3).
- Mọi service đọc/xoá/render tài liệu **phải** gọi `can_view` trước, và trả `NotFound` (không phải `Forbidden`) khi không xem được, để không lộ sự tồn tại.
- Khi `needs_admin_audit` → service ghi `AuditAction.DOCUMENT_VIEW_OTHER`.

## Tiêu chí xong

- [ ] Bảng chân trị đầy đủ: 3 role × (của mình / private người khác / shared người khác / đã xoá) cho `can_view`, `can_delete`.

## Test

`tests/unit/documents/test_access_policy.py` (parametrize).

## Tham chiếu

SADD §5.8.3 · US-05 AC-05.2 · Implement_plan §14 C-10, C-11
