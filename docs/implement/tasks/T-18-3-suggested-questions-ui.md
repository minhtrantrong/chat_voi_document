# T-18-3 — Chip gợi ý câu hỏi ở SCR-03 (P2)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-18 (P2) |
| Sprint | S4 — chỉ khi còn dung lượng |
| Tầng | APP / UI |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-18-2, T-07-4, T-07-5 |
| Chặn | T-18-4 |

## Bối cảnh

Thiết kế SCR-03: chip gợi ý trong trạng thái "có tài liệu, chưa hội thoại".

## Phạm vi

**Làm:** `DocumentService.suggestions(actor, scope_ids, limit=3)`, component `suggested_questions` trong EmptyState của cột Hội thoại.

## Đặc tả

```sql
SELECT s.question FROM document_suggestions s
JOIN documents d ON d.id = s.document_id
WHERE d.status = 'READY' AND d.deleted_at IS NULL
  AND (d.owner_id = :uid OR d.visibility = 'SHARED')
  AND (cardinality(:scope::uuid[]) = 0 OR d.id = ANY(:scope))
ORDER BY d.ready_at DESC, s.ord
LIMIT 3;
```

UI: chỉ hiển thị khi hội thoại trống và cờ bật; mỗi gợi ý là `st.button(q, key=f"sugg:{hash(q)}")`; bấm → gọi luồng gửi như T-07-5 với `question=q`.

## Tiêu chí xong

- [ ] Hội thoại trống hiển thị ≤ 3 chip; bấm chip gửi câu hỏi và bắt đầu stream.

## Test

`tests/unit/ui/test_suggested_questions.py` (AppTest).

## Tham chiếu

US-18 · Blueprint SCR-03, §3.1 (SuggestedQuestions)
