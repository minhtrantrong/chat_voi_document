# PLT-12 — Scheduler: lên lịch job định kỳ trong worker-ingest

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S1, mục 1.5) |
| Sprint | S1 |
| Tầng | WRK |
| Ước lượng | 0.75d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | F-08 |
| Chặn | PLT-10, T-15-3, T-23-1 (chạy tự động) |

## Bối cảnh

SADD §5.3.7: một thread trong `worker-ingest` giữ `pg_try_advisory_lock(hashtext('cvd_scheduler'))` và enqueue các job định kỳ, idempotent theo `runDate`.

## Phạm vi

**Làm:** `app/infrastructure/db/scheduler.py`, cờ `--scheduler` của `app.worker`.

**Không làm:** logic các job định kỳ (task riêng).

## Đặc tả

Lịch (giờ `Asia/Ho_Chi_Minh`):

| Job | Giờ chạy | Payload |
|---|---|---|
| `retention.sweep` | 01:00 hằng ngày | `{"runDate": "YYYY-MM-DD"}` |
| `storage.gc` | 03:00 hằng ngày | `{"runDate": ..., "olderThanHours": 24}` |
| `integrity.check` | 04:00 hằng ngày | `{"runDate": ...}` |

```text
scheduler_loop():                              # thread daemon, chu kỳ 60 s
  conn = connection riêng (không lấy từ pool, giữ lâu dài)
  if not conn.scalar("SELECT pg_try_advisory_lock(hashtext('cvd_scheduler'))"): sleep(60); retry
  while not stopping:
     today = clock.today_vn()
     for spec in SCHEDULE:
        if clock.now_vn() >= spec.time_today and not exists_job(spec.type, today):
            enqueue(spec.type, {"runDate": today, ...}, priority=50, max_attempts=spec.max_attempts)
     sleep(60)
exists_job: SELECT 1 FROM jobs WHERE type=:t AND payload->>'runDate'=:d LIMIT 1   (mọi trạng thái)
```

- Khoá advisory **session-level** gắn với connection riêng; worker chết thì Postgres tự nhả khoá, worker khác giành lấy.
- Shutdown: thread dừng, `pg_advisory_unlock`, đóng connection.

## Tiêu chí xong

- [ ] Chạy hai `worker-ingest --scheduler` đồng thời: mỗi job định kỳ chỉ được enqueue **một lần** mỗi ngày.
- [ ] Tắt worker giữ khoá: worker còn lại tiếp quản trong ≤ 2 phút.
- [ ] Khởi động lúc 05:00 (đã qua giờ) vẫn enqueue các job của ngày hôm đó nếu chưa có.

## Test

`tests/integration/jobs/test_scheduler.py` với Clock giả: hai scheduler đua nhau; giả lập ngày mới; giả lập worker giữ khoá bị kill (đóng connection).

## Tham chiếu

SADD §5.3.7 (Scheduler), §5.7.4
