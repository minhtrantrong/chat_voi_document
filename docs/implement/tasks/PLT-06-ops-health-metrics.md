# PLT-06 — Dịch vụ ops: health, readiness và endpoint metrics

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S0, mục 0.7) |
| Sprint | S0 |
| Tầng | OPS / INF |
| Ước lượng | 1d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | PLT-04, PLT-05 |
| Chặn | PLT-09, PLT-17, PLT-19 (blue/green dựa vào `/readyz`) |

## Bối cảnh

SADD §5.3.1 và §5.9.2: container `ops` phục vụ `/healthz`, `/readyz`; `web` và hai worker mở metrics trên `:9101/:9102/:9103` bằng `prometheus_client`.

## Phạm vi

**Làm:**
- `app/ops.py`: HTTP server nhỏ (stdlib `ThreadingHTTPServer`, không thêm framework).
- `app/shared/metrics.py`: khởi động metrics server một lần mỗi process; khai báo các metric dùng chung.

**Không làm:** dashboard và alert (PLT-17).

## Đặc tả

**`/healthz`:** luôn `200 {"status":"ok"}` khi process sống.

**`/readyz`:** chạy song song 3 kiểm tra, mỗi kiểm tra timeout 2 s:

| Check | Cách kiểm tra |
|---|---|
| `db` | `SELECT 1` qua engine (dùng `DATABASE_URL`) |
| `redis` | `PING` |
| `s3` | `head_bucket(S3_BUCKET)` |

Tất cả OK thì `200`, có lỗi thì `503`. Body: `{"status":"ok|degraded","checks":{"db":"ok","redis":"fail: timeout","s3":"ok"}}`. Thông điệp lỗi chỉ gồm loại lỗi, **không** in connection string.

**Metrics:**

```python
# app/shared/metrics.py
def start_metrics_server(port: int) -> None:     # idempotent: biến module _started
ASK_TOTAL = Counter("cvd_ask_total", "...", ["outcome"])
FIRST_TOKEN_SECONDS = Histogram("cvd_first_token_seconds", "...",
                                buckets=(0.5, 1, 1.5, 2, 3, 4, 6, 8, 12, 20))
ANSWER_SECONDS = Histogram("cvd_answer_seconds", "...")
JOBS_TOTAL = Counter("cvd_jobs_total", "...", ["type", "status"])
JOB_DURATION = Histogram("cvd_job_duration_seconds", "...", ["type"])
QUEUE_DEPTH = Gauge("cvd_queue_depth", "...", ["type"])
LLM_REQUESTS = Counter("cvd_llm_requests_total", "...", ["provider", "model"])
LLM_TOKENS = Counter("cvd_llm_tokens_total", "...", ["provider", "model", "kind"])
LLM_ERRORS = Counter("cvd_llm_errors_total", "...", ["provider", "model", "reason"])
AUTH_FAILURES = Counter("cvd_auth_failures_total", "...", ["reason"])
RATE_LIMITED = Counter("cvd_rate_limited_total", "...", ["reason"])
INTEGRITY_VIOLATIONS = Gauge("cvd_integrity_violations", "...", ["check"])
```

- Trong `web`: gọi `start_metrics_server(9101)` bên trong hàm `@st.cache_resource` để chỉ chạy một lần mỗi process.
- Trong worker: tham số `--metrics-port`.
- Bind `0.0.0.0` nhưng chỉ trong network `app` (không publish port).

## Tiêu chí xong

- [ ] `curl ops:9090/readyz` trả 200 khi đủ dependency; dừng Redis thì trả 503 với `redis` lỗi trong ≤ 3 s.
- [ ] `curl web:9101/metrics` có các metric `cvd_*` (giá trị 0).
- [ ] Rerun trang Streamlit nhiều lần không gây lỗi "port already in use".

## Test

- `tests/integration/test_ops.py`: dùng testcontainers, kiểm tra 200; dừng container Redis, kiểm tra 503.
- `tests/unit/test_metrics.py`: gọi `start_metrics_server` hai lần không lỗi.

## Tham chiếu

SADD §5.3.1 (quy tắc 7), §5.3.10, §5.9.1–§5.9.2
