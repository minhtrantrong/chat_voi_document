# T-06-4 — Trạng thái "đã xoá" của citation tính tại lúc đọc

| Thuộc tính | Giá trị |
|---|---|
| Story | US-06 (P0); US-23 — "tài liệu biến mất khỏi UI ≤ 1 s"; US-13d — AC-13d.2 |
| Sprint | S4 (cột tính động có thể làm ngay ở T-13-4 trong S3) |
| Tầng | INF |
| Ước lượng | 0.25d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-13-4 |
| Chặn | T-10-4 (hiển thị chip đã xoá ngay sau xoá) |

## Bối cảnh

`citations.deleted` chỉ được purge đặt (bất đồng bộ). Để chip đổi sang "Tài liệu đã bị xoá" ngay khi người dùng xoá, giá trị hiển thị phải tính từ `documents.deleted_at`.

## Phạm vi

**Làm:** mọi truy vấn đọc citation cho UI (`answers.get_full`, `conversations.get`) dùng biểu thức chung.

## Đặc tả

```sql
SELECT ci.id, ci.segment_id, ci.document_id, ci.doc_name_snapshot, ci.page, ci.anchor, ci.quote,
       (ci.deleted OR d.deleted_at IS NOT NULL) AS deleted
FROM citations ci
JOIN documents d ON d.id = ci.document_id
WHERE ci.segment_id = ANY(:segment_ids);
```

- Đặt biểu thức trong một hàm repository duy nhất `citations.for_segments(tx, segment_ids)` để không chỗ nào quên.
- Tên hiển thị dùng `doc_name_snapshot` (không join lấy tên hiện tại) — DR-04.

## Tiêu chí xong

- [ ] Xoá tài liệu rồi `get_answer` ngay (purge chưa chạy) → citation `deleted=True`.

## Test

`tests/integration/qa/test_citation_deleted_flag.py`.

## Tham chiếu

SADD §5.2.4 DR-04, §5.3.6 · US-23 · CN-10
