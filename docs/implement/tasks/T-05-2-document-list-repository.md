# T-05-2 — Truy vấn danh sách tài liệu theo quyền, phân trang keyset

| Thuộc tính | Giá trị |
|---|---|
| Story | US-05 (P0) — AC-05.1, AC-05.2 |
| Sprint | S2 |
| Tầng | INF / APP |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-05-1, F-01 (cursor), F-07 |
| Chặn | T-05-3, T-04-7 |

## Bối cảnh

AC-05.1: thấy **100%** tài liệu trong quyền, mỗi dòng có tên tệp, ngày tải lên, trạng thái. Quy mô ≤ 1.000 tài liệu.

## Phạm vi

**Làm:** `DocumentRepository.list_visible`, `DocumentService.list(actor, cursor, limit) -> Page[DocumentDTO]`, `DocumentService.get(actor, doc_id)`.

## Đặc tả

```sql
SELECT id, owner_id, file_name, page_count, status, error_code, uploaded_at, visibility, version
FROM documents
WHERE deleted_at IS NULL
  AND (owner_id = :uid OR visibility = 'SHARED')
  AND (:cursor_ts IS NULL OR (uploaded_at, id) < (:cursor_ts, :cursor_id))
ORDER BY uploaded_at DESC, id DESC
LIMIT :limit_plus_one;
```

- `limit` mặc định 50, tối đa 200; lấy `limit + 1` dòng để biết có trang sau; `next_cursor = encode_cursor(last.uploaded_at, last.id)`.
- `DocumentDTO` tính `is_owner`, `can_delete`, `can_retry`, `selectable = status == READY` theo `AccessPolicy`.
- `get(actor, doc_id)`: `can_view` sai → `NotFound(ERR_DOC_404)`; `needs_admin_audit` → audit.
- Không cache kết quả list (dữ liệu phân quyền; SADD §4.5).

## Tiêu chí xong

- [ ] Seed 120 tài liệu (của A, SHARED của B, private của B, đã xoá): duyệt hết trang với `limit=50` được đúng số tài liệu A được thấy, không trùng, không thiếu (AC-05.1).
- [ ] Private của B không xuất hiện (AC-05.2).
- [ ] `EXPLAIN` dùng index `ix_documents_owner_status` hoặc seq scan nhỏ (ghi lại trong PR).

## Test

`tests/integration/documents/test_list.py`; dòng `documents.list` trong authz matrix (T-21-8).

## Tham chiếu

US-05 · SADD §5.4.3, §5.8.3
