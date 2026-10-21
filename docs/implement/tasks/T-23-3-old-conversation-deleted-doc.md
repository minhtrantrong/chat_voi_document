# T-23-3 — Hội thoại cũ sau khi xoá tài liệu

| Thuộc tính | Giá trị |
|---|---|
| Story | US-23 (P0); PRD 4.2 "Xoá tài liệu khi đang được trích dẫn trong hội thoại cũ" |
| Sprint | S4 |
| Tầng | TEST |
| Ước lượng | 0.25d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | T-06-4, T-10-4, T-15-1 |
| Chặn | — |

## Bối cảnh

PRD 4.2: hội thoại cũ giữ nguyên văn câu trả lời nhưng chip trích dẫn hiển thị "Tài liệu đã bị xoá" và không mở được (BRU-006).

## Phạm vi

**Làm:** AppTest + test service.

## Đặc tả

| Test | Khẳng định |
|---|---|
| `test_old_answer_text_unchanged_after_delete` | `conversations.get` sau khi xoá: text segment giống hệt trước khi xoá |
| `test_deleted_chip_disabled_in_history` | AppTest render hội thoại cũ: chip có nhãn "Tài liệu đã bị xoá", `disabled=True` |
| `test_render_page_deleted_not_found` | `documents.render_page(actor, deleted_doc, 1)` → `NotFound` |

## Tiêu chí xong

- [ ] 3 test xanh.

## Tham chiếu

US-23 · PRD 4.2 · SADD DR-04
