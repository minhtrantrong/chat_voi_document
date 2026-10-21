# T-19-1 — FeedbackService.upsert

| Thuộc tính | Giá trị |
|---|---|
| Story | US-19 — Đánh giá từng câu trả lời (P0) — AC-19.1, AC-19.2, AC-19.3 |
| Sprint | S4 |
| Tầng | APP / INF |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-13-4 (kiểm tra sở hữu answer), F-06 |
| Chặn | T-19-2 |

## Bối cảnh

DR-05: một feedback / (answer, user); đổi lựa chọn = update. SADD §5.3.5: `INSERT … ON CONFLICT(answer_id, user_id) DO UPDATE`.

## Phạm vi

**Làm:** `app/feedback/{service,schemas,repository}.py`.

## Đặc tả

```python
class FeedbackValue(StrEnum): HELPFUL = "HELPFUL"; NOT_HELPFUL = "NOT_HELPFUL"

@dataclass(frozen=True)
class FeedbackDTO:
    answer_id: UUID; value: FeedbackValue; reason: str | None; updated_at: datetime

class FeedbackService:
    def upsert(self, actor: Actor, answer_id: UUID, value: FeedbackValue,
               reason: str | None = None) -> FeedbackDTO:
        reason = (reason or "").strip()[:500] or None
        if value is FeedbackValue.HELPFUL: reason = None          # lý do chỉ dành cho NOT_HELPFUL
        with self._uow() as tx:
            a = self._answers.owner_and_outcome(tx, answer_id)    # (conversation_user_id, outcome)
            if a is None or a.user_id != actor.user_id: raise NotFound(ERR_DOC_404)
            if a.outcome not in ("ANSWERED", "NOT_FOUND"): raise Invalid(ERR_DOC_422, {"reason": "not_ratable"})
            row = self._repo.upsert(tx, new_id(), answer_id, actor.user_id, value, reason)
            self._telemetry.emit("feedback_submitted", actor.user_id, answer_id=answer_id, tx=tx,
                                 value=value.value, has_reason=reason is not None)
        return row
```

SQL (`repository.upsert`):

```sql
INSERT INTO feedback (id, answer_id, user_id, value, reason)
VALUES (:id, :answer_id, :uid, :value, :reason)
ON CONFLICT (answer_id, user_id)
DO UPDATE SET value = EXCLUDED.value, reason = EXCLUDED.reason, updated_at = now()
RETURNING answer_id, value, reason, updated_at;
```

- `reason` là nội dung người dùng nhập: lưu DB, **không** log, không vào telemetry (chỉ `has_reason`).

## Tiêu chí xong

- [ ] Bấm 👍 rồi 👎 → 1 dòng, giá trị cuối `NOT_HELPFUL` (AC-19.2).
- [ ] 👎 kèm lý do 600 ký tự → lưu 500 ký tự.
- [ ] Đánh giá answer ERROR/ABORTED → `Invalid`; answer của người khác → `NotFound`.

## Test

`tests/integration/feedback/test_feedback_service.py`; dòng `feedback.upsert` trong authz matrix.

## Tham chiếu

SADD §5.2.4 DR-05, §5.3.5 · US-19
