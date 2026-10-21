# T-14-1 — Lấy lịch sử gần nhất để đưa vào prompt

| Thuộc tính | Giá trị |
|---|---|
| Story | US-14 — Hỏi tiếp mà không nhắc lại bối cảnh (P1) — AC-14.1 |
| Sprint | S4 (bản đơn giản cần sẵn ở S3 để `handle_answer` có `history`) |
| Tầng | APP / INF |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-07-6, T-04-2 (Tokenizer) |
| Chặn | T-14-2, T-13-3 (`load_for_generation`) |

## Bối cảnh

SADD §10.3 prompt có mục "LỊCH SỬ GẦN NHẤT"; giới hạn lịch sử để kiểm soát chi phí (§5.9.6). `HISTORY_TURNS` mặc định 3 (F-04).

## Phạm vi

**Làm:** `ConversationService.recent_turns(conv_id, before_message_id, n) -> list[Turn]` (gọi từ worker, không qua Actor vì đã kiểm tra quyền khi `ask`).

## Đặc tả

```python
@dataclass(frozen=True)
class Turn:
    question: str; answer: str          # answer = text các segment nối "\n", không marker, không citation
```

```sql
SELECT mq.content AS question, ma.content AS answer
FROM answers a
JOIN messages mq ON mq.id = a.question_message_id
JOIN messages ma ON ma.id = a.assistant_message_id
WHERE mq.conversation_id = :conv_id
  AND mq.created_at < (SELECT created_at FROM messages WHERE id = :current_question_message_id)
  AND a.outcome IN ('ANSWERED', 'NOT_FOUND')
ORDER BY mq.created_at DESC
LIMIT :n;
```

- Đảo lại theo thứ tự thời gian tăng dần trước khi trả.
- Cắt tổng ≤ 1.500 token: bỏ lượt cũ nhất trước; nếu một lượt vẫn quá dài, cắt `answer` còn 300 token.
- `n = 0` → danh sách rỗng (tắt ngữ cảnh hội thoại).
- Answer ABORTED/ERROR không đưa vào lịch sử (nội dung có thể dở dang).

## Tiêu chí xong

- [ ] Hội thoại 5 lượt → trả đúng 3 lượt gần nhất trước câu hiện tại, theo thứ tự thời gian.
- [ ] Không bao giờ lấy lượt của hội thoại khác.

## Test

`tests/integration/conversation/test_recent_turns.py`.

## Tham chiếu

US-14 · SADD §5.9.6, §10.3
