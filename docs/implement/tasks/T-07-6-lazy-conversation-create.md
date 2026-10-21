# T-07-6 — Tạo hội thoại "lười" khi gửi câu hỏi đầu tiên

| Thuộc tính | Giá trị |
|---|---|
| Story | US-07 (P0); US-16 (không tạo hội thoại rỗng) |
| Sprint | S3 |
| Tầng | APP / INF |
| Ước lượng | 0.25d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | PLT-08, F-07 |
| Chặn | T-07-2 |

## Bối cảnh

Hội thoại chỉ được tạo khi có câu hỏi đầu tiên, để nút "Hội thoại mới" không sinh bản ghi rỗng trong lịch sử.

## Phạm vi

**Làm:** `ConversationRepository.get_or_create(tx, actor, conv_id, title)`, `touch`, `has_completed_answer` trong `app/conversation/`.

## Đặc tả

```text
get_or_create(tx, actor, conv_id, title):
  if conv_id is None:
      return insert(id=new_id(), user_id=actor.user_id, title=clean_title(title))
  conv = SELECT ... WHERE id=:id AND user_id=:uid AND archived=false
  if conv is None: raise NotFound(ERR_DOC_404)           # không lộ hội thoại người khác
  return conv

clean_title(q): một dòng, gộp khoảng trắng, tối đa 60 ký tự (cắt tại ranh giới từ + "…")
touch: UPDATE conversations SET updated_at = now() WHERE id=:id
has_completed_answer(conv_id): EXISTS answers a JOIN messages m ON a.question_message_id=m.id
                               WHERE m.conversation_id=:id AND a.outcome IN ('ANSWERED','NOT_FOUND')
```

- Tiêu đề chứa nội dung câu hỏi: được lưu trong DB (bảng nghiệp vụ), **không** được log.

## Tiêu chí xong

- [ ] Hỏi câu đầu tạo đúng 1 hội thoại; câu thứ hai dùng lại hội thoại đó.
- [ ] `conv_id` của người khác → `NotFound`.

## Test

`tests/integration/conversation/test_get_or_create.py`.

## Tham chiếu

US-07, US-16 · SADD §5.4.1
