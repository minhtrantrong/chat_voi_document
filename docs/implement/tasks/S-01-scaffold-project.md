# S-01 — Scaffold project, dependencies và cấu trúc thư mục

| Thuộc tính | Giá trị |
|---|---|
| Story | Nền tảng (US-01…US-09) |
| Phase | P0 |
| Tầng | SETUP |
| Ước lượng | 0,5d |
| Phụ thuộc | — |
| Chặn | S-02, S-03, S-04, S-05 |
| Owner gợi ý | Backend/Full-stack |

## 1. Mục tiêu

Tạo repo chạy được tối thiểu: cài dependency, có cấu trúc `app/`, `.env.example`, `.gitignore`, `pyproject.toml`, và một trang Streamlit placeholder. Sau task này, bất kỳ ai clone repo đều có thể chạy `streamlit run app/main.py` và thấy trang trống.

## 2. Phạm vi

**Làm:**

- `pyproject.toml` với Python 3.12 và dependency của app.
- Cấu trúc thư mục theo §4 của kế hoạch.
- `app/main.py` placeholder (title + caption).
- `.env.example` đầy đủ khoá cấu hình.
- `.gitignore` chặn `.env`, `data/`, cache, DB.
- `tests/__init__.py`, `tests/conftest.py` rỗng.
- `data/uploads/.gitkeep` (hoặc tạo runtime).
- README skeleton (S-26 sẽ hoàn thiện).

**Không làm:**

- Chưa gọi Qdrant/LLM.
- Chưa có upload/chat.
- Chưa có Docker compose (S-02).

## 3. File chính

```text
pyproject.toml
.env.example
.gitignore
README.md
app/__init__.py
app/main.py
tests/__init__.py
tests/conftest.py
data/uploads/.gitkeep
```

## 4. Đặc tả

### 4.1 `pyproject.toml`

```toml
[project]
name = "chat-voi-document"
version = "0.1.0"
description = "Upload PDF và chat với AI bằng Qdrant"
requires-python = ">=3.12"
dependencies = [
    "streamlit>=1.42",
    "qdrant-client>=1.12",
    "openai>=1.50",
    "pymupdf>=1.24",
    "pydantic-settings>=2.6",
    "tiktoken>=0.8",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3",
    "pytest-cov>=5.0",
    "ruff>=0.7",
    "mypy>=1.11",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "integration: cần Qdrant đang chạy",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.12"
ignore_missing_imports = true
```

> Có thể dùng `uv` hoặc `pip`. README ghi cả hai.

### 4.2 `app/main.py` placeholder

```python
import streamlit as st

st.set_page_config(page_title="Chat với tài liệu", page_icon="📄", layout="wide")

st.title("Chat với tài liệu")
st.caption("Tải PDF và hỏi AI về nội dung tài liệu.")
st.info("Khung ứng dụng đã sẵn sàng. Upload/chat sẽ được thêm ở các task tiếp theo.")
```

### 4.3 `.gitignore`

```gitignore
.env
.venv/
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.mypy_cache/
data/
*.db
*.sqlite3
.DS_Store
```

### 4.4 `.env.example`

Sao chép đầy đủ từ kế hoạch §3.3. Không đưa key thật vào repo.

## 5. Trường hợp biên

- Chạy với Python < 3.12 → pip báo lỗi rõ; README ghi yêu cầu.
- `data/` chưa tồn tại → app vẫn chạy; S-03/S-04 sẽ tạo.
- Chạy từ thư mục khác → dùng đường dẫn tương đối theo `Path(__file__)` hoặc `DATA_DIR` tuyệt đối.
- Thiếu dependency → README có lệnh cài.

## 6. Tiêu chí xong

- [ ] `uv sync` hoặc `pip install -e ".[dev]"` thành công trên Python 3.12.
- [ ] `streamlit run app/main.py` mở trang có title, không exception.
- [ ] `pytest` chạy và collect 0 test (không lỗi).
- [ ] `ruff check .` không lỗi.
- [ ] `.env.example` có đủ khoá ở kế hoạch §3.3.
- [ ] Không có `.env`, `data/app.db`, file PDF trong git.

## 7. Test

| Test | Cách kiểm |
|---|---|
| Import app | `python -c "import app"` |
| Chạy Streamlit | `streamlit run app/main.py --server.headless true` rồi mở localhost |
| Pytest collect | `pytest --collect-only` |
| Ruff | `ruff check .` |

## 8. Tham chiếu

- Kế hoạch §3.1, §3.3, §4, §11.
- S-02, S-03, S-04, S-05.
