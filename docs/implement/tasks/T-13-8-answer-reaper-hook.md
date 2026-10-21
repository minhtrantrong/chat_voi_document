# T-13-8 — Reaper hook cho `answer.generate`: kết thúc answer khi worker chết

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13 (P0); QA-08 |
| Sprint | S3 |
| Tầng | WRK |
| Ước lượng | 0.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | F-08 (REAPER_HOOKS), T-13-2, T-13-3 |
| Chặn | PLT-15 |

## Bối cảnh

SADD §5.3.7 (Reaper): job `answer.generate` chuyển DEAD/FAILED vĩnh viễn thì `answers.outcome='ERROR'`, `messages.state='INTERRUPTED'`, ghi `error_code`, `XADD done(error)` nếu Redis còn; **bỏ qua** job DEAD có `last_error='CANCELED'` hoặc answer đã terminal.

## Phạm vi

**Làm:** hook `REAPER_HOOKS["answer.generate"]`; cấu hình `visibility_timeout` 3 phút cho loại job này (F-08); xử lý job FAILED do exception không mong đợi trong handler.

## Đặc tả

```python
def on_answer_dead(tx: UnitOfWork, job: Job) -> None:
    if job.last_error == "CANCELED": return
    aid = UUID(job.payload["answerId"])
    updated = tx.execute("""UPDATE answers SET outcome='ERROR', error_code='WORKER_LOST', completed_at=now()
                            WHERE id=:aid AND outcome='PENDING' RETURNING assistant_message_id""", {"aid": aid})
    if not updated: return
    tx.execute("UPDATE messages SET state='INTERRUPTED' WHERE id=:mid", {"mid": updated.assistant_message_id})
    after_commit(lambda: stream.append(aid, "done", "error"))      # lỗi Redis chỉ log
    after_commit(lambda: telemetry.emit("answer_error", uid, answer_id=aid, error_code="WORKER_LOST"))
```

- Cần tiện ích `after_commit(fn)` trên UoW (bổ sung F-07: danh sách callback chạy sau commit thành công).
- Runtime F-09: khi handler `answer.generate` ném exception không bắt (lỗi lập trình) → job FAILED (max_attempts=1) → gọi cùng hook để answer không treo PENDING.

## Tiêu chí xong

- [ ] Kill worker giữa stream → ≤ 3 phút + 60 s (chu kỳ reaper) answer thành ERROR, UI hiện "Chưa hoàn tất" + Tạo lại.
- [ ] Job bị cancel (DEAD, CANCELED) không bị đổi thành ERROR.

## Test

`tests/integration/qa/test_answer_reaper.py`.

## Tham chiếu

SADD §5.3.4 (Hủy và phục hồi), §5.3.7 · QA-08
