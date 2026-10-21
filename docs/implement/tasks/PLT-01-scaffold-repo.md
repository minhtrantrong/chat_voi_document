# PLT-01 — Khởi tạo cấu trúc repository và dependency

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S0, mục 0.1) |
| Sprint | S0 |
| Tầng | OPS |
| Ước lượng | 1d |
| Owner gợi ý | Tech Lead |
| Phụ thuộc | — |
| Chặn | Mọi task khác |

## Bối cảnh

Repo hiện chỉ có `docs/`. Cần một bộ khung code đúng cấu trúc SADD §5.5.1 để mọi developer làm việc song song mà không phải bàn lại tổ chức thư mục.

## Phạm vi

**Làm:**
- Tạo cây thư mục và các file `__init__.py` rỗng.
- `pyproject.toml` khai báo dependency, `uv.lock` sinh ra từ `uv lock`.
- Ba entrypoint chạy được nhưng chưa có logic: `app/main.py`, `app/worker.py`, `app/ops.py`.
- `.gitignore`, `.env.example`, `README.md` ngắn (cách chạy local).

**Không làm:** CI (PLT-03), Docker (PLT-04), cấu hình (PLT-05).

## Đặc tả

Cây thư mục (mỗi module nghiệp vụ có đủ 5 file `domain.py`, `service.py`, `ports.py`, `repository.py`, `schemas.py`, có thể để trống):

```
app/
  __init__.py
  main.py            # streamlit entry
  worker.py          # python -m app.worker --queues ...
  ops.py             # python -m app.ops
  config.py
  bootstrap.py
  shared/            # types.py, errors.py, ids.py, clock.py, logging.py, metrics.py, uow.py
  identity/ documents/ ingestion/ conversation/ qa/ feedback/ telemetry/ admin/
  qa/                # thêm retrieval.py, prompt.py, citation.py, worker_handler.py
  ingestion/         # thêm chunker.py, worker_handler.py
  infrastructure/
    db/ storage/ redis/ llm/ embedding/ pdf/ oidc/
  ui/
    pages/ components/ i18n/ state.py theme.py
prompts/             # qa_answer.v1.md (để trống, T-08-1 điền)
migrations/          # do PLT-08 khởi tạo bằng alembic init
tests/
  unit/ integration/ e2e/ security/ eval/ load/ perf/ fixtures/pdf/
deploy/
docs/                # đã có
```

`pyproject.toml` (phiên bản tối thiểu theo SADD §5.5.0; `uv lock` sẽ pin chính xác):

| Nhóm | Gói |
|---|---|
| runtime | `streamlit>=1.42`, `sqlalchemy>=2.0`, `psycopg[binary]>=3.2`, `pgvector>=0.3`, `alembic>=1.13`, `redis>=5.0`, `boto3>=1.34`, `pymupdf>=1.24` (chờ G-03), `pydantic>=2.7`, `pydantic-settings>=2.3`, `structlog>=24.1`, `httpx>=0.27`, `tiktoken>=0.7`, `prometheus-client>=0.20`, `uuid-utils>=0.9` (UUIDv7), `pyyaml>=6` |
| dev | `pytest`, `pytest-cov`, `pytest-timeout`, `testcontainers[postgres,redis,minio]`, `respx`, `ruff`, `mypy`, `import-linter`, `pre-commit`, `playwright`, `types-pyyaml`, `boto3-stubs[s3]` |

- `requires-python = ">=3.12,<3.13"`.
- `[project.scripts]` không cần; chạy bằng `python -m`.
- `app/worker.py` và `app/ops.py` dùng `argparse`, có `--help`, lúc này chỉ in thông báo và thoát 0.
- `app/main.py`: `st.set_page_config(page_title="Chat với tài liệu", layout="wide")` và `st.write("skeleton")`.

`.env.example` liệt kê **mọi** biến môi trường ở SADD §10.2, kèm giá trị giả cho local (không có secret thật).

## Tiêu chí xong

- [ ] `uv sync` chạy thành công trên máy sạch (Linux và Windows).
- [ ] `uv run streamlit run app/main.py` mở được trang "skeleton".
- [ ] `uv run python -m app.worker --help` và `uv run python -m app.ops --help` thoát với mã 0.
- [ ] `uv run pytest` chạy được (0 test vẫn thoát 0 nhờ `-p no:cacheprovider` hoặc có 1 test smoke).
- [ ] `.gitignore` loại `.env`, `.streamlit/secrets.toml`, `.venv`, `reports/`, `__pycache__`.

## Test

- `tests/unit/test_smoke.py`: import được `app`, `app.shared`, `app.ui`.

## Tham chiếu

SADD §5.5.0, §5.5.1, §10.2 · Implement_plan Phần I §4 S0
