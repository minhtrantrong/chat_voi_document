# F-05 — AuditService: ghi nhật ký kiểm toán trong cùng transaction

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng dùng chung (Implement_plan §15) |
| Sprint | S1 |
| Tầng | APP / INF |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | PLT-08, F-07 |
| Chặn | T-01-4, T-06-2, T-13-5, T-24-3, T-13d-4 |

## Bối cảnh

STRIDE Repudiation (SADD §5.8.1): ai xoá gì, khi nào phải truy được; `audit_log` chỉ INSERT. ADMIN đọc/xoá tài liệu không sở hữu **bắt buộc** có audit (§5.8.3).

## Phạm vi

**Làm:** `AuditService.record(...)` ghi qua transaction đang mở; danh mục `action` chuẩn; hàm đọc cho trang admin (`list(filter, cursor)`).

## Đặc tả

```python
class AuditAction(StrEnum):
    DOCUMENT_UPLOAD = "document.upload"; DOCUMENT_DELETE = "document.delete"
    DOCUMENT_RETRY = "document.retry"; DOCUMENT_VIEW_OTHER = "document.view_other"
    ANSWER_CANCEL = "answer.cancel"; CONFIG_UPDATE = "config.update"
    JOB_RETRY = "job.retry"; AUTH_LOGIN = "auth.login"; AUTH_DENIED = "auth.denied"

class AuditService:
    def record(self, tx: UnitOfWork, actor: Actor | None, action: AuditAction,
               entity_type: str, entity_id: str | UUID | None,
               metadata: Mapping[str, Any] | None = None, ip_hash: str | None = None) -> None: ...
    def list(self, actor: Actor, *, action: str | None, since: datetime | None,
             cursor: str | None, limit: int = 50) -> Page[AuditEntryDTO]: ...   # chỉ ADMIN/PM
```

- `record` **không** tự commit; nếu transaction nghiệp vụ rollback thì audit cũng rollback (đúng ý nghĩa: hành động không xảy ra).
- `metadata` chỉ chứa ID, cờ, giá trị cấu hình cũ/mới; **cấm** nội dung câu hỏi, tên tệp đầy đủ, quote. Hàm kiểm tra khoá cấm giống F-12 và loại bỏ nếu có.
- `list`: END_USER gọi thì `Forbidden`.

## Tiêu chí xong

- [ ] Ghi audit trong transaction bị rollback thì không có dòng nào.
- [ ] Metadata có khoá cấm thì khoá đó bị loại và có log warn.
- [ ] END_USER gọi `list` thì `Forbidden`.

## Test

`tests/integration/admin/test_audit.py`: commit/rollback; lọc khoá cấm; phân quyền `list`.

## Tham chiếu

SADD §5.4.2 (Audit), §5.8.1, §5.8.3, §5.8.6
