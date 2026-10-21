# T-16-2 — Test: hội thoại mới không mang ngữ cảnh cũ

| Thuộc tính | Giá trị |
|---|---|
| Story | US-16 (P1) — AC-16.1 |
| Sprint | S4 |
| Tầng | TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | T-16-1, T-14-1, T-08-3 (FakeLLM ghi `last_messages`) |
| Chặn | — |

## Bối cảnh

AC-16.1: câu hỏi tham chiếu hội thoại cũ không được trả lời bằng ngữ cảnh cũ.

## Phạm vi

**Làm:** test integration kiểm tra **prompt** gửi cho LLM.

## Đặc tả

| Test | Bước | Khẳng định |
|---|---|---|
| `test_new_conversation_has_no_prior_context` | Hội thoại 1: hỏi "Hợp đồng ký với bên nào?" → hoàn tất. Tạo hội thoại mới (conversation_id=None). Hỏi "Còn hạn chót của nó?" | `FakeLLM.last_messages` user message có mục lịch sử là `(không có)`; không chứa "Hợp đồng ký với bên nào"; `is_followup=False` trong payload job |
| `test_same_conversation_has_context` | Như trên nhưng hỏi tiếp trong hội thoại 1 | Prompt chứa câu hỏi trước; `is_followup=True` |

## Tiêu chí xong

- [ ] 2 test xanh.

## Tham chiếu

US-16 AC-16.1 · T-14-1
