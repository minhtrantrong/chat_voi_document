# T-15-1 — ConversationService: danh sách và nội dung hội thoại

| Thuộc tính | Giá trị |
|---|---|
| Story | US-15 — Xem lại các hội thoại cũ (P1) — AC-15.1 |
| Sprint | S4 (`get` bản tối thiểu cần ở S3 để render hội thoại hiện tại) |
| Tầng | APP / INF |
| Ước lượng | 1d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-07-6, T-06-4, T-13-4 |
| Chặn | T-15-2, T-10-5 (danh sách tin nhắn), T-23-3 |

## Bối cảnh

AC-15.1: đăng xuất rồi đăng nhập vẫn thấy hội thoại trong thời hạn OQ-012; không thấy hội thoại của người khác. SADD §5.8.3: kể cả ADMIN không xem hội thoại người khác.

## Phạm vi

**Làm:** `list(actor, cursor, limit=30) -> Page[ConversationSummaryDTO]`, `get(actor, conv_id) -> ConversationDTO`.

## Đặc tả

```python
@dataclass(frozen=True)
class ConversationSummaryDTO:
    id: UUID; title: str; updated_at: datetime

@dataclass(frozen=True)
class ConversationDTO:
    id: UUID; title: str; answers: list[AnswerDTO]      # theo thứ tự thời gian; mỗi AnswerDTO chứa question
    active_answer_id: UUID | None                       # answer cuối nếu còn PENDING (để UI nối lại stream)
```

```sql
-- list
SELECT id, title, updated_at FROM conversations
WHERE user_id = :uid AND archived = false
  AND (:cursor_ts IS NULL OR (updated_at, id) < (:cursor_ts, :cursor_id))
ORDER BY updated_at DESC, id DESC LIMIT :limit_plus_one;
```

`get`: kiểm tra `user_id = actor.user_id` (không thì `NotFound`); tải bằng 3 truy vấn:
1. answers + message câu hỏi + state của message trả lời, `WHERE mq.conversation_id = :id ORDER BY mq.created_at`.
2. segments của các answer đó (`answer_id = ANY(:ids)`).
3. citations qua `citations.for_segments` (T-06-4) + `my_feedback` (`feedback WHERE answer_id = ANY(:ids) AND user_id = :uid`).

Giới hạn: hội thoại > 200 lượt chỉ tải 200 lượt gần nhất (ghi chú; MVP hiếm gặp).

## Tiêu chí xong

- [ ] `get` một hội thoại 20 lượt dùng đúng 4 truy vấn (đếm bằng event listener SQLAlchemy).
- [ ] Hội thoại của người khác (kể cả với ADMIN) → `NotFound`.

## Test

`tests/integration/conversation/test_conversation_service.py`; dòng `conversations.get` trong authz matrix.

## Tham chiếu

US-15 · SADD §5.4.3, §5.8.3
