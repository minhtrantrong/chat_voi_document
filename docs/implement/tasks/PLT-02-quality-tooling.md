# PLT-02 — Công cụ chất lượng: ruff, mypy, import-linter, pre-commit

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S0, mục 0.2) |
| Sprint | S0 |
| Tầng | OPS |
| Ước lượng | 1d |
| Owner gợi ý | Tech Lead |
| Phụ thuộc | PLT-01 |
| Chặn | PLT-03 |

## Bối cảnh

Quy tắc phụ thuộc của SADD §4.1 (domain không import framework, UI không chạm hạ tầng) phải được **máy** kiểm tra từ ngày đầu, không dựa vào review.

## Phạm vi

**Làm:** cấu hình ruff (format + lint + security rules), mypy (strict cho core), import-linter (3 contract), pre-commit, kiểm tra Conventional Commits.

**Không làm:** chạy trong CI (PLT-03).

## Đặc tả

**Ruff** (`pyproject.toml`):

```toml
[tool.ruff]
line-length = 110
target-version = "py312"
[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP", "S", "SIM", "RUF", "T20", "DTZ"]
ignore = ["S101"]            # cho phép assert trong test
[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S", "T20"]
```

- `T20` cấm `print` (dùng structlog). `DTZ` cấm `datetime.now()` không timezone; mọi thời gian lấy qua `Clock` (F-01).

**Mypy:**

```toml
[tool.mypy]
python_version = "3.12"
warn_unused_ignores = true
[[tool.mypy.overrides]]
module = ["app.shared.*", "app.identity.*", "app.documents.*", "app.ingestion.*",
          "app.conversation.*", "app.qa.*", "app.feedback.*", "app.telemetry.*", "app.admin.*"]
strict = true
[[tool.mypy.overrides]]
module = ["app.infrastructure.*", "app.ui.*"]
ignore_missing_imports = true
```

**Import-linter** (`.importlinter`):

```ini
[importlinter]
root_package = app

[importlinter:contract:core-pure]
name = Core (domain + application) không import hạ tầng / UI / framework
type = forbidden
source_modules =
    app.shared
    app.identity
    app.documents
    app.ingestion
    app.conversation
    app.qa
    app.feedback
    app.telemetry
    app.admin
forbidden_modules =
    app.infrastructure
    app.ui
    streamlit
    sqlalchemy
    psycopg
    redis
    boto3
    httpx
    fitz

[importlinter:contract:ui-no-infra]
name = UI không import hạ tầng trực tiếp
type = forbidden
source_modules = app.ui
forbidden_modules =
    app.infrastructure
    sqlalchemy
    psycopg
    redis
    boto3
    httpx
    fitz
allow_indirect_imports = True       # ui -> app.bootstrap -> infrastructure là hợp lệ

[importlinter:contract:no-cross-repository]
name = Module không import repository của module khác
type = independence
modules =
    app.documents.repository
    app.conversation.repository
    app.qa.repository
    app.feedback.repository
```

Chỉ `app.bootstrap`, `app.worker`, `app.ops`, `app.main` được nối core với `app.infrastructure`.

**Pre-commit** (`.pre-commit-config.yaml`): `ruff-format`, `ruff`, `mypy` (local hook `uv run mypy app`), `lint-imports`, `check-added-large-files --maxkb=1024` (không commit PDF lớn), `detect-private-key`, `conventional-pre-commit` (stage `commit-msg`).

## Tiêu chí xong

- [ ] `uv run ruff format --check . && uv run ruff check . && uv run mypy app && uv run lint-imports` xanh trên skeleton.
- [ ] Thử thêm `import streamlit` vào `app/documents/domain.py` thì `lint-imports` báo lỗi (ghi lại trong PR mô tả, rồi bỏ).
- [ ] `pre-commit install --hook-type pre-commit --hook-type commit-msg` hoạt động; commit message sai chuẩn bị chặn.
- [ ] README có mục "Quy tắc code" link tới Implement_plan §13.

## Test

Không có test pytest; bằng chứng là log chạy lệnh ở trên.

## Tham chiếu

SADD §4.1, §4.5, §5.5.2, §7.4 · Implement_plan §13
