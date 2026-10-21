# PLT-17 — Dashboard, alert và runbook vận hành

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S5, mục 5.7) |
| Sprint | S5 |
| Tầng | OPS |
| Ước lượng | 2d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | PLT-09, các metric ở PLT-06 đã được ghi từ code |
| Chặn | M5 |

## Bối cảnh

NFR-OPS-01: phát hiện sự cố ≤ 5 phút. SADD §5.9.4 liệt kê 11 alert, §10.5 có runbook RUN-01…RUN-09.

## Phạm vi

**Làm:** alert rule Prometheus, Alertmanager route, 3 dashboard, 9 runbook dạng markdown, test alert.

## Đặc tả

`deploy/observability/alerts.yml` (biểu thức gợi ý):

| Alert | Biểu thức | for | Mức |
|---|---|---|---|
| WebDown | `probe_success{job="web-health"} == 0` | 2m | P1 |
| DbDown | `pg_up == 0` | 1m | P1 |
| RedisDown | `redis_up == 0` | 1m | P1 |
| QueueBacklog | `max(cvd_queue_oldest_age_seconds) > 600` | 5m | P2 |
| IngestFailureHigh | `sum(rate(cvd_jobs_total{type="document.ingest",status=~"FAILED|DEAD"}[15m])) / sum(rate(cvd_jobs_total{type="document.ingest"}[15m])) > 0.2` | 15m | P2 |
| LlmErrorHigh | `sum(rate(cvd_llm_errors_total[10m])) / sum(rate(cvd_llm_requests_total[10m])) > 0.05` | 10m | P2 |
| FirstTokenSlow | `histogram_quantile(0.9, sum(rate(cvd_first_token_seconds_bucket[15m])) by (le)) > 8` | 15m | P2 |
| DiskHigh | `node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.2` | 10m | P2 |
| BackupFailed | `cvd_backup_last_success_timestamp < time() - 26*3600` | 0m | P2 |
| AuthAnomaly | `increase(cvd_auth_failures_total[5m]) > 50` | 0m | P1 |
| CostOverBudget | `cvd_daily_tokens / cvd_daily_token_budget > 1.2` | 0m | P2 |
| IntegrityViolation | `max(cvd_integrity_violations) > 0` | 0m | P2 |

- Bổ sung metric còn thiếu: `cvd_queue_oldest_age_seconds{type}` (worker-ingest cập nhật cùng `QUEUE_DEPTH`), `cvd_daily_tokens`, `cvd_daily_token_budget` (BudgetService T-24-2), `cvd_backup_last_success_timestamp` (PLT-18, qua textfile/pushgateway).
- Probe web: `blackbox_exporter` gọi `http://web:8501/_stcore/health`.
- Alertmanager: P1 gửi kênh on-call (Teams/Slack/email theo tổ chức), P2 gửi kênh đội; giờ hành chính.

Dashboard: "Tổng quan" (từ PLT-09, mở rộng), "Hỏi đáp" (ask/phút, outcome, p50/p90 first-token, lỗi LLM, token/ngày, chi phí), "Ingestion" (job theo trạng thái, thời gian xử lý p95, mã lỗi phổ biến).

Runbook: `docs/runbooks/RUN-01-web-down.md` … `RUN-09-cost-overrun.md`, mỗi file gồm: triệu chứng, alert liên quan, kiểm tra đầu tiên (lệnh cụ thể), xử lý, khi nào leo thang, sau sự cố. Lấy nội dung gốc từ SADD §10.5 và bổ sung lệnh docker compose thực tế.

## Tiêu chí xong

- [ ] Mỗi alert được test bằng cách gây lỗi thật trên staging (dừng service, tiêm lỗi LLM) và thông báo đến kênh trong ≤ 5 phút.
- [ ] 3 dashboard có dữ liệu.
- [ ] 9 runbook được Ops review.

## Tham chiếu

SADD §5.9.1–§5.9.5, §10.5
