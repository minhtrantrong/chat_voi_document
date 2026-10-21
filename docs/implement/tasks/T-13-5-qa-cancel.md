# T-13-5 — `QaService.cancel`: dừng câu trả lời

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13 (P0) — AC-13.2 (nút Dừng); NFR-UX-01 |
| Sprint | S3 |
| Tầng | APP |
| Ước lượng | 0.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-13-2, T-13-4, F-05, F-06, F-08 |
| Chặn | T-13-6 |

## Bối cảnh

SADD §5.3.4 (Hủy và phục hồi): cancel ghi cờ Redis + audit; job còn QUEUED thì một transaction đánh dấu job DEAD (`last_error='CANCELED'`), answer ABORTED, message INTERRUPTED; job RUNNING thì worker tự dừng ≤ 2 s.

## Phạm vi

**Làm:** method `cancel(actor, answer_id) -> None`.

## Đặc tả

```text
cancel(actor, aid):
  self._ensure_owner_cached(actor, aid)                     # NotFound nếu không phải chủ
  self._stream.request_cancel(aid)                          # Redis lỗi: log warn, vẫn tiếp tục nhánh DB
  with uow() as tx:
     rows = tx.execute("""UPDATE jobs SET status='DEAD', last_error='CANCELED', updated_at=now()
                          WHERE type='answer.generate' AND payload->>'answerId'=:aid AND status='QUEUED'
                          RETURNING id""")
     if rows:
        tx.execute("UPDATE answers SET outcome='ABORTED', completed_at=now() WHERE id=:aid AND outcome='PENDING'")
        tx.execute("UPDATE messages SET state='INTERRUPTED' WHERE id=(SELECT assistant_message_id FROM answers WHERE id=:aid)")
     audit.record(tx, actor, ANSWER_CANCEL, "answer", aid, {"was_queued": bool(rows)})
  if rows: self._stream.append(aid, "done", "aborted")
  telemetry.emit("answer_stopped", actor.user_id, answer_id=aid)
```

- Idempotent: bấm nhiều lần không lỗi, không tạo trạng thái lạ.
- Answer đã terminal: chỉ ghi audit, không đổi gì.
- Đua với worker vừa claim: `WHERE status='QUEUED'` bảo đảm chỉ một bên thắng; nếu worker đã claim thì worker thấy cờ Redis.

## Tiêu chí xong

- [ ] Cancel khi job QUEUED → answer ABORTED ngay, worker sau đó không gọi provider.
- [ ] Cancel khi job RUNNING → worker kết thúc ABORTED ≤ 2 s (kết hợp T-13-3).
- [ ] Cancel answer đã ANSWERED → không đổi outcome.

## Test

`tests/integration/qa/test_cancel.py`.

## Tham chiếu

SADD §5.3.4 (Hủy và phục hồi), §5.3.7 · US-13
