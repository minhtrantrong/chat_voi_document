# T-20-2 — View `v_weekly_questions`

| Thuộc tính | Giá trị |
|---|---|
| Story | US-20 (P0) — AC-20.1 |
| Sprint | S3 |
| Tầng | DB |
| Ước lượng | 0.25d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | PLT-08, T-07-2 (telemetry có `answer_id`) |
| Chặn | T-20-3 |

## Bối cảnh

AC-20.1: số câu hỏi theo từng người dùng mỗi tuần khớp 100% với số câu đã thực hiện; **câu lỗi AI không tính**.

## Phạm vi

**Làm:** migration tạo view.

## Đặc tả

```sql
CREATE VIEW v_weekly_questions AS
SELECT e.user_id,
       date_trunc('week', e.created_at AT TIME ZONE 'Asia/Ho_Chi_Minh')::date AS week_start,
       count(*) AS questions
FROM telemetry_events e
JOIN answers a ON a.id = e.answer_id
WHERE e.event = 'question_submitted'
  AND a.outcome NOT IN ('ERROR', 'PENDING')
GROUP BY 1, 2;
```

- Tuần bắt đầu thứ Hai (`date_trunc('week')` của Postgres theo ISO).
- ABORTED và NOT_FOUND **có** tính (người dùng đã đặt câu hỏi; chỉ lỗi AI bị loại).
- Giới hạn: answer bị xoá do retention (180 ngày) thì event mất `answer_id` (`ON DELETE SET NULL`) và không còn tính — chấp nhận vì telemetry chỉ giữ 90 ngày.
- `GRANT SELECT ON v_weekly_questions TO app_ro` (cho công cụ báo cáo ngoài nếu có).

## Tiêu chí xong

- [ ] Migration có `downgrade` (`DROP VIEW`).

## Test

Thuộc T-20-4.

## Tham chiếu

US-20 AC-20.1 · PRD MET-004
