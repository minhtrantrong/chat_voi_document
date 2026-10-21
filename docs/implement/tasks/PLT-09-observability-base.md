# PLT-09 — Nền observability: Prometheus, Loki, Grafana, trace ID

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S1, mục 1.9) |
| Sprint | S1 |
| Tầng | OPS |
| Ước lượng | 1.5d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | PLT-04, PLT-06, F-12 |
| Chặn | PLT-17 |

## Bối cảnh

SADD §5.9: log JSON ra stdout, metrics Prometheus scrape 15 s, dashboard Grafana tự host. Từ S1 cần có dashboard tối thiểu để đội nhìn được job queue và lỗi khi phát triển.

## Phạm vi

**Làm:**
- Profile compose `observability`: `prometheus`, `loki`, `promtail` (hoặc Grafana Alloy), `grafana`.
- File `deploy/observability/prometheus.yml` scrape `web:9101`, `worker-answer:9102`, `worker-ingest:9103`, `ops:9090` (không có metrics, chỉ để probe), `postgres-exporter`, `redis-exporter`.
- Dashboard "CVD — Tổng quan" bản đầu.
- Trace ID: mỗi lần chạy script Streamlit sinh `corr_id`; truyền vào payload job (`payload["corrId"]`) và log của worker.

**Không làm:** alert rule và runbook (PLT-17), OTLP tracing đầy đủ (để sau MVP; chỉ cần `corr_id` xuyên suốt).

## Đặc tả

- Retention Prometheus 15 ngày, Loki 30 ngày (SADD §5.9.3).
- Dashboard bản đầu có các panel: số job theo `type,status` (`cvd_jobs_total`), độ sâu queue (`cvd_queue_depth`), tỉ lệ lỗi job, `pg_stat_activity` connections, Redis memory, log lỗi gần nhất (Loki `{service=~"web|worker.*"} |= "error"`).
- Dashboard lưu dạng JSON ở `deploy/observability/dashboards/overview.json`, nạp qua provisioning.
- `corr_id`: `app/shared/logging.py` dùng `contextvars.ContextVar("corr_id")`. UI gán ở đầu mỗi lần chạy script (`uuid7` rút gọn 12 ký tự). `JobQueue.enqueue` tự thêm `corrId` vào payload nếu có; worker gán lại contextvar khi xử lý job.
- `QUEUE_DEPTH` được worker-ingest cập nhật mỗi 30 s bằng `SELECT type, count(*) FROM jobs WHERE status='QUEUED' GROUP BY type`.

## Tiêu chí xong

- [ ] `docker compose --profile observability up -d` → Grafana có dashboard "CVD — Tổng quan" với dữ liệu thật.
- [ ] Một thao tác upload ở UI: tìm được trên Loki các dòng log của `web` và `worker-ingest` có **cùng** `corr_id`.
- [ ] Không port observability nào publish ra ngoài (trừ Grafana qua Caddy có đăng nhập, nếu cần).

## Test

Kiểm thủ công theo tiêu chí trên; ghi ảnh chụp dashboard vào PR.

## Tham chiếu

SADD §5.9.2, §5.9.3 · PLT-06 · F-12
