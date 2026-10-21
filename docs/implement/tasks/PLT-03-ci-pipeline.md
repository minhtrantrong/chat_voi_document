# PLT-03 — Pipeline CI

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S0, mục 0.3) |
| Sprint | S0 |
| Tầng | OPS |
| Ước lượng | 1.5d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | PLT-01, PLT-02, PLT-04 (build image) |
| Chặn | Merge PR đầu tiên có code nghiệp vụ |

## Bối cảnh

SADD §5.5.4 định nghĩa pipeline: lint/type → unit → integration (testcontainers) → build → scan → staging. Task này làm phần **PR + main**; deploy staging tự động làm ở PLT-19 (bản đầu có thể là deploy thủ công).

## Phạm vi

**Làm:** workflow PR, workflow main (build + push image), workflow nightly (eval, fuzz). Mặc định dùng **GitHub Actions**; nếu tổ chức dùng GitLab thì chuyển tương đương 1-1.

**Không làm:** nội dung test eval/fuzz (T-12-5, PLT-11) — chỉ tạo khung job gọi lệnh.

## Đặc tả

`.github/workflows/pr.yml`:

| Job | Lệnh | Thời gian mục tiêu | Chặn merge |
|---|---|---|---|
| `lint` | `uv sync --frozen` · `ruff format --check` · `ruff check` · `mypy app` · `lint-imports` | ≤ 3 phút | Có |
| `unit` | `pytest tests/unit --cov=app --cov-report=xml --cov-fail-under=60` | ≤ 3 phút | Có |
| `integration` | `pytest tests/integration -m "not slow"` (testcontainers: `pgvector/pgvector:pg16`, `redis:7.2-alpine`, `minio/minio`) | ≤ 10 phút | Có |
| `migrations` | `alembic upgrade head` → `alembic downgrade base` → `alembic upgrade head` trên Postgres container | ≤ 2 phút | Có |
| `security` | `pip-audit --strict`, `trivy fs --severity CRITICAL,HIGH --exit-code 1 .` | ≤ 3 phút | Có (Critical/High) |
| `ui` | `pytest tests/unit/ui` (AppTest) | ≤ 3 phút | Có |

- Cache: `astral-sh/setup-uv` với `enable-cache: true`.
- Coverage domain/application ≥ 80% kiểm bằng `coverage report --include="app/*/domain.py,app/*/service.py" --fail-under=80` (bật từ S2 khi đã có code; S0–S1 để `continue-on-error`).
- Concurrency group theo branch, hủy run cũ.

`.github/workflows/main.yml` (push lên `main`): chạy lại `lint/unit/integration`, sau đó `docker build -t <registry>/cvd-app:${GITHUB_SHA}`, `trivy image --exit-code 1 --severity CRITICAL,HIGH`, SBOM `syft <image> -o cyclonedx-json > sbom.json` (đính kèm artifact), push registry.

`.github/workflows/nightly.yml` (cron `0 19 * * *` UTC = 02:00 giờ VN): job `eval` (`python -m app.eval run …` trên staging, cần secret) và `fuzz` (`pytest tests/security -m fuzz`). Lúc S0 cả hai chỉ `echo "TODO"`.

Secrets CI: `REGISTRY_USER/PASSWORD`, `STAGING_*`. **Không** đưa key LLM thật vào workflow PR.

## Tiêu chí xong

- [ ] Một PR mẫu chạy đủ các job, tổng thời gian ≤ 15 phút.
- [ ] Branch protection trên `main`: bắt buộc `lint`, `unit`, `integration`, `migrations`, `security`, `ui` và 1 approval.
- [ ] Image được đẩy lên registry với tag = git SHA khi merge `main`.
- [ ] SBOM xuất hiện trong artifact của run `main`.

## Test

PR thử nghiệm cố ý vi phạm import rule và một test fail để thấy CI đỏ đúng job.

## Tham chiếu

SADD §5.5.4, §5.8.7, §7.4 · Implement_plan Phần I §4 S0
