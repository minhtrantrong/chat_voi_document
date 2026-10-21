# T-01-5 — Xử lý trùng tên khi tải lên: Thay thế / Giữ cả hai

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01 (P0), US-02 (P1) — màn hình SCR-07 |
| Sprint | S2 |
| Tầng | APP |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-01-4, T-06-1 (`mark_deleting`) |
| Chặn | T-01-7 |

## Bối cảnh

Quyết định **C-12**: cùng tên nhưng khác nội dung với một tài liệu đang hoạt động của chính người dùng thì hỏi "Thay thế" hoặc "Giữ cả hai".

## Phạm vi

**Làm:** nhánh `on_conflict` trong `_upload_one`; hàm nội bộ dùng chung `_mark_deleting(tx, actor, doc)` (US-06 dùng lại).

## Đặc tả

- `KEEP_BOTH`: `existing = repo.names_like(tx, owner, stem)` (các tên dạng `stem.pdf`, `stem (n).pdf`), `file_name = next_copy_name(file_name, existing)`, sau đó đi tiếp bước 8 của T-01-4.
- `REPLACE`: trong **cùng transaction** với insert tài liệu mới:
  1. `old = repo.get_for_update(tx, same_name.id)`; nếu `old` đã bị xoá thì bỏ qua (coi như không trùng nữa).
  2. `_mark_deleting(tx, actor, old)`: `old.mark_deleting(now)`, lưu; huỷ job ingest đang QUEUED của `old`; `enqueue("document.purge", {"documentId": old.id}, priority=150, max_attempts=5)`; `audit.record(DOCUMENT_DELETE, metadata={"reason": "replaced"})` — **chú ý** khoá `reason` bị F-05 lọc, dùng `{"replaced_by": str(new_id)}`.
  3. Insert tài liệu mới như bình thường.
- Chỉ chủ sở hữu mới bị hỏi trùng tên (trùng tên với tài liệu SHARED của người khác thì **không** coi là trùng).
- Hội thoại cũ trích dẫn tài liệu bị thay thế sẽ hiện "Tài liệu đã bị xoá" (giống xoá thường; thông báo trước trong SCR-07).

## Tiêu chí xong

- [ ] `KEEP_BOTH` tạo tài liệu `ten (2).pdf`; tài liệu cũ giữ nguyên.
- [ ] `REPLACE`: tài liệu cũ `DELETING` + có job purge; tài liệu mới `PROCESSING`; cả hai thay đổi nằm trong một transaction (lỗi insert mới thì tài liệu cũ không bị xoá).
- [ ] Trùng tên với tài liệu của người khác: không hỏi.

## Test

`tests/integration/documents/test_upload_conflict.py`: keep both, replace, replace rollback, tên trùng với người khác.

## Tham chiếu

Implement_plan §14 C-12 · Blueprint SCR-07 · SADD §5.3.6
