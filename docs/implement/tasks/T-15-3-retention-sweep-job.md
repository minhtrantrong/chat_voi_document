# T-15-3 — Job `retention.sweep`: xoá dữ liệu quá hạn lưu trữ

| Thuộc tính | Giá trị |
|---|---|
| Story | US-15 (P1) — "trong thời hạn OQ-012"; SADD §5.4.4 |
| Sprint | S4 |
| Tầng | WRK |
| Ước lượng | 0.75d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | F-08, F-09, PLT-12, F-04 |
| Chặn | — |

## Bối cảnh

SADD §5.4.4: hội thoại/message/answer 180 ngày (OQ-012), feedback 180 ngày, telemetry 90 ngày, audit 365 ngày, job history 30 ngày.

## Phạm vi

**Làm:** handler `@handles("retention.sweep")` (payload `{"runDate"}`), max_attempts 2.

## Đặc tả

Xoá theo lô 500 dòng mỗi transaction, lặp tới hết, để không khoá bảng lâu:

| Dữ liệu | Điều kiện | Cách xoá |
|---|---|---|
| Hội thoại | `updated_at < now() - CONVERSATION_RETENTION_DAYS` | `DELETE FROM conversations WHERE id IN (SELECT id … LIMIT 500)` — cascade messages → answers → segments → citations → feedback |
| Telemetry | `created_at < now() - TELEMETRY_RETENTION_DAYS (90)` | `DELETE … LIMIT 500` (qua subquery id) |
| Job | `status='SUCCEEDED' AND updated_at < now() - 30 days`; `FAILED/DEAD` giữ 90 ngày | như trên |
| Audit | `created_at < now() - AUDIT_RETENTION_DAYS (365)` | role `app_rw` **không** có DELETE trên audit_log → chạy bằng role riêng `retention` (chỉ DELETE audit_log), hoặc partition theo tháng và drop (ưu tiên khi bảng lớn). MVP: role riêng |

- Log số dòng xoá mỗi loại; metric `cvd_retention_deleted_total{kind}`.
- Feedback bị xoá theo cascade cùng answer (đáp ứng 180 ngày).
- Không xoá citation riêng lẻ (citation là snapshot sống cùng answer).

## Tiêu chí xong

- [ ] FrozenClock + dữ liệu cũ/mới: chỉ dữ liệu quá hạn bị xoá, cascade đúng.
- [ ] Chạy lại cùng `runDate` không lỗi.
- [ ] Role `retention` được tạo trong `deploy/init-db.sql` và chỉ có quyền DELETE trên `audit_log`.

## Test

`tests/integration/jobs/test_retention.py`.

## Tham chiếu

SADD §5.4.4, §5.8.6 · OQ-012 · US-15
