# PLT-04 — Dockerfile một image và Docker Compose local/staging

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S0, mục 0.4) |
| Sprint | S0 |
| Tầng | OPS |
| Ước lượng | 1.5d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | PLT-01 |
| Chặn | PLT-03 (build), PLT-06, mọi integration test chạy trên compose |

## Bối cảnh

ADR-001/ADR-012: một image, ba entrypoint (`web`, `worker`, `ops`), chạy bằng Docker Compose trên VM. Developer cũng dùng compose này để chạy toàn bộ hệ thống ở máy local.

## Phạm vi

**Làm:** `Dockerfile`, `deploy/compose.yaml`, `deploy/Caddyfile`, `deploy/.env.example`, script `deploy/init-db.sql` (tạo role), `make`/`justfile` lệnh tắt.

**Không làm:** observability stack (PLT-09), blue/green production (PLT-19), sinh `secrets.toml` (T-21-1).

## Đặc tả

**Dockerfile** (multi-stage):

```dockerfile
FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY app ./app
COPY prompts ./prompts
COPY migrations ./migrations
COPY alembic.ini ./
RUN uv sync --frozen --no-dev

FROM python:3.12-slim
RUN useradd --uid 10001 --create-home cvd
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
USER cvd
COPY --chown=cvd deploy/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["web"]
```

`deploy/entrypoint.sh` nhận `web | worker-answer | worker-ingest | ops | migrate`:

| Lệnh | Chạy |
|---|---|
| `web` | `streamlit run app/main.py --server.port 8501` |
| `worker-answer` | `python -m app.worker --queues answer.generate,document.purge --threads 10 --metrics-port 9102` |
| `worker-ingest` | `python -m app.worker --queues document.ingest,retention.sweep,storage.gc,integrity.check --threads 2 --metrics-port 9103 --scheduler` |
| `ops` | `python -m app.ops --port 9090` |
| `migrate` | `alembic upgrade head` |

(Phần sinh `secrets.toml` được T-21-1 thêm vào đầu script.)

**Compose** — dịch vụ, port, healthcheck theo SADD §5.6.2:

| Service | Image | Network | Healthcheck |
|---|---|---|---|
| `caddy` | `caddy:2` | edge, app | — |
| `web` | `cvd-app:${TAG:-local}` cmd `web` | app, data | `curl -f http://localhost:8501/_stcore/health` |
| `worker-answer` | cùng image | app, data | `python -m app.worker --healthcheck` (kiểm tra heartbeat file < 60 s) |
| `worker-ingest` | cùng image | app, data | như trên |
| `ops` | cùng image | app, data | `curl -f localhost:9090/healthz` |
| `migrate` | cùng image, `restart: "no"` | data | — (các service app `depends_on: migrate: condition: service_completed_successfully`) |
| `postgres` | `pgvector/pgvector:pg16` | data | `pg_isready` |
| `redis` | `redis:7.2-alpine`, `--appendonly yes` | data | `redis-cli ping` |
| `minio` | `minio/minio` `server /data --console-address :9001` | data | `curl -f localhost:9000/minio/health/live` |
| `minio-init` | `minio/mc` tạo bucket `cvd-documents` private | data | — |

- Network `data` là `internal: true`; chỉ `caddy` publish `443` (local publish thêm `8501` để debug, qua profile `dev`).
- Volume: `pgdata`, `redisdata`, `miniodata`, `caddy_data`.
- `deploy/init-db.sql`: tạo role `migrator` (owner schema) và `app_rw` (chỉ DML); `DATABASE_URL` của app dùng `app_rw`, của `migrate` dùng `migrator`.

**Caddyfile:**

```
{$APP_DOMAIN:localhost} {
  encode gzip
  header {
    Strict-Transport-Security "max-age=31536000"
    X-Content-Type-Options nosniff
    Referrer-Policy no-referrer
    Content-Security-Policy "frame-ancestors 'none'"
  }
  request_body { max_size 35MB }
  reverse_proxy web:8501            # Caddy tự hỗ trợ websocket
}
```

## Tiêu chí xong

- [ ] `docker compose -f deploy/compose.yaml up -d` trên máy sạch: mọi service `healthy` trong ≤ 2 phút.
- [ ] `https://localhost` mở được trang skeleton qua Caddy (chứng chỉ local).
- [ ] Postgres, Redis, MinIO không truy cập được từ host khi không bật profile `dev`.
- [ ] Image chạy bằng user không phải root (`docker compose exec web id` → uid 10001).
- [ ] Kích thước image ≤ 600 MB.

## Test

Smoke script `deploy/smoke.sh`: chờ healthy, `curl` health của web và `ops /readyz` (sau PLT-06).

## Tham chiếu

SADD §5.3.1, §5.6.1–§5.6.4, ADR-001, ADR-012
