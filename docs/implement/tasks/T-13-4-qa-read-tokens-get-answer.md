# T-13-4 — `QaService.read_tokens` và `get_answer`

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13 (P0); US-10 (UI đọc citation sau khi xong) |
| Sprint | S3 |
| Tầng | APP |
| Ước lượng | 0.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-13-2, T-07-1 (biểu thức `deleted` tính động viết luôn trong task này theo đặc tả T-06-4; T-06-4 ở S4 chỉ rà soát mọi nơi đọc citation dùng chung hàm) |
| Chặn | T-13-6, T-13-7 |

## Bối cảnh

Fragment UI gọi `read_tokens` mỗi 0.4 s. Kiểm tra quyền mỗi lần bằng DB sẽ tốn; SADD cho phép kiểm tra quyền **một lần** cho mỗi answer trong phiên.

## Phạm vi

**Làm:** hai method của `QaService` và repository `answers.get_full`.

## Đặc tả

```python
def read_tokens(self, actor: Actor, answer_id: UUID, last_id: str) -> TokenBatch:
    self._ensure_owner_cached(actor, answer_id)       # cache trong process: dict[(session_id, answer_id)] = True, TTL 1 h, tối đa 10.000 mục
    return self._stream.read(answer_id, last_id)

def get_answer(self, actor: Actor, answer_id: UUID) -> AnswerDTO:
    with self._uow() as tx:
        a = self._answers.get_full(tx, answer_id)      # answer + question + segments + citations + my_feedback
        if a is None or a.conversation_user_id != actor.user_id: raise NotFound(ERR_DOC_404)
    return a
```

`get_full` dùng ≤ 3 truy vấn:

```sql
SELECT a.*, mq.content AS question, ma.state AS message_state, c.user_id AS conversation_user_id, c.id AS conversation_id
FROM answers a JOIN messages mq ON mq.id = a.question_message_id
JOIN messages ma ON ma.id = a.assistant_message_id
JOIN conversations c ON c.id = mq.conversation_id WHERE a.id = :id;

SELECT s.id, s.ord, s.text, s.cited FROM answer_segments s WHERE s.answer_id = :id ORDER BY s.ord;

SELECT ci.*, (ci.deleted OR d.deleted_at IS NOT NULL) AS deleted_effective
FROM citations ci JOIN answer_segments s ON s.id = ci.segment_id
JOIN documents d ON d.id = ci.document_id WHERE s.answer_id = :id ORDER BY s.ord, ci.created_at;
```

`my_feedback`: `SELECT value FROM feedback WHERE answer_id=:id AND user_id=:uid`.

- `_ensure_owner_cached`: cache miss → truy vấn quyền sở hữu (join conversations) → không phải chủ thì `NotFound`.
- Chỉ chủ hội thoại đọc được answer (kể cả ADMIN không đọc được — SADD §5.8.3).

## Tiêu chí xong

- [ ] 100 lần `read_tokens` liên tiếp cùng answer → 1 truy vấn DB.
- [ ] User khác gọi `read_tokens`/`get_answer` → `NotFound`.
- [ ] Citation của tài liệu vừa xoá mềm có `deleted=True` ngay (trước khi purge).

## Test

`tests/integration/qa/test_read_answer.py`; dòng tương ứng trong authz matrix (T-21-8).

## Tham chiếu

SADD §5.7.2, §5.8.3 · US-13, US-23
