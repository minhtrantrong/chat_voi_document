# T-18-1 — Bảng `document_suggestions` (P2)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-18 — Được gợi ý tối đa 3 câu hỏi (P2) |
| Sprint | S4 — chỉ khi còn dung lượng; cờ `FEATURE_SUGGESTIONS` mặc định tắt |
| Tầng | DB |
| Ước lượng | 0.25d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | PLT-08 |
| Chặn | T-18-2 |

## Bối cảnh

Gợi ý câu hỏi được sinh một lần khi tài liệu READY rồi lưu lại, để không gọi LLM mỗi lần mở trang. SADD chưa có bảng này (bổ sung khi review SADD, PLT-20).

## Phạm vi

**Làm:** migration mới.

## Đặc tả

```sql
CREATE TABLE document_suggestions (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  ord         int NOT NULL,
  question    text NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (document_id, ord)
);
```

- `ON DELETE CASCADE` không đủ vì tài liệu chỉ bị xoá mềm (không bao giờ `DELETE` khỏi `documents`). Vì vậy: (1) thêm `DELETE FROM document_suggestions WHERE document_id=:id` vào transaction DB của purge (T-06-3); (2) mọi truy vấn đọc gợi ý lọc `documents.deleted_at IS NULL` để gợi ý biến mất ngay khi xoá mềm.

## Tiêu chí xong

- [ ] Migration có `downgrade`; handler purge (T-06-3) có thêm dòng xoá gợi ý (chỉ khi bảng tồn tại, tức tính năng được làm).

## Tham chiếu

US-18 · BR-021
