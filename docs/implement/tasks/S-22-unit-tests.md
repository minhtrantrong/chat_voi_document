# S-22 — Bộ unit test lõi

| Thuộc tính | Giá trị |
|---|---|
| Story | Chất lượng (US-01…US-09) |
| Phase | P3 |
| Tầng | TEST |
| Ước lượng | 0,75d |
| Phụ thuộc | S-04…S-17 |
| Chặn | S-26 |
| Owner gợi ý | Backend |

## 1. Mục tiêu

Có bộ unit test chạy **không cần mạng, không cần Qdrant, không cần API key**, bao phủ các logic dễ sai: chunking, validate PDF, config, DB, prompt, history trim, error mapping. Đây là lưới an toàn trước khi demo.

## 2. Phạm vi

**Làm:**

- `tests/conftest.py` với fixture dùng chung.
- Test cho: `config`, `db`, `pdf` (validate + extract), `chunking`, `embeddings` (fake client), `errors`, `rag` (context + answer + diversity), `llm` (fake client), `ingest_many` (fake ingest), UI state (AppTest nếu ổn định).
- Không gọi API thật; không đọc/ghi `data/` thật.
- Đánh dấu integration riêng; mặc định `pytest` bỏ qua integration.
- Mục tiêu coverage: ≥ 75% line cho `app/` (không tính `main.py`).

**Không làm:**

- E2E browser (Playwright).
- Load test.
- Test Qdrant thật (S-23).
- Test LLM thật (S-24/manual).

## 3. File chính

```text
tests/conftest.py
tests/test_config.py
tests/test_db.py
tests/test_pdf.py
tests/test_pdf_extract.py
tests/test_chunking.py
tests/test_embeddings.py
tests/test_errors.py
tests/test_rag_context.py
tests/test_rag_answer.py
tests/test_diversity.py
tests/test_llm.py
tests/test_ingest_many.py
tests/test_sources.py
tests/test_ui_state.py
```

## 4. Đặc tả

### 4.1 `conftest.py`

```python
import pytest
from pathlib import Path
from app.config import get_settings

@pytest.fixture
def tmp_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("EMBEDDING_DIM", "8")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    get_settings.cache_clear()
    s = get_settings()
    yield s
    get_settings.cache_clear()

@pytest.fixture
def make_pdf(tmp_path):
    import fitz
    def _make(name="test.pdf", pages=1, text="Hello world"):
        path = tmp_path / name
        doc = fitz.open()
        for i in range(pages):
            page = doc.new_page()
            page.insert_text((72, 72), f"{text} page {i+1}")
        doc.save(path)
        doc.close()
        return path
    return _make
```

**Lưu ý:** `Settings` đọc `.env`; test phải set env trước khi gọi. `get_settings.cache_clear()` bắt buộc.

### 4.2 Danh sách test tối thiểu

| File | Test chính |
|---|---|
| `test_config.py` | default, env override, invalid dim/overlap/score, dirs created, API key repr |
| `test_db.py` | init idempotent, create/get, ready/error, list order, delete, duplicate |
| `test_pdf.py` | valid, not pdf, empty, too large, too many pages, encrypted, corrupt |
| `test_pdf_extract.py` | single/multi page, NFC, blank skip, scan raises, mixed |
| `test_chunking.py` | short/long, max size, no cross-page, offsets, global index, overlap, long word |
| `test_embeddings.py` | empty, single, batch order, dim mismatch, count mismatch, retry, blank |
| `test_errors.py` | all codes, fallback, file name prefix, no raw exception |
| `test_rag_context.py` | empty, labels, max chars, dedupe, missing payload, truncate |
| `test_rag_answer.py` | no hits no LLM, prompt built, marker→not found, history trim, filter forwarded |
| `test_diversity.py` | cap per doc, top-k, dedupe, invalid params |
| `test_llm.py` | stream tokens, empty stream, retry before first token, no retry after |
| `test_ingest_many.py` | all success, one fail, all fail, order, empty |
| `test_sources.py` | dedupe, dict/dataclass, missing fields, truncate |
| `test_ui_state.py` | AppTest 0 doc / error / ready |

### 4.3 Quy ước test

- Không dùng `time.sleep` thật; monkeypatch `time.sleep`.
- Không dùng `openai` thật; fake client.
- PDF test tạo tại `tmp_path`, không commit file nhị phân.
- Test nào cần Qdrant → marker `@pytest.mark.integration`, skip nếu không có `QDRANT_URL`.
- Test nào cần API key → không; dùng fake.
- Không assert vào log message quá cụ thể; assert code/hành vi.
- Dùng `pytest.raises(..., match=...)` cho lỗi.

### 4.4 Chạy

```bash
pytest -q
pytest -q -m integration        # cần Qdrant
pytest --cov=app --cov-report=term-missing
```

## 5. Trường hợp biên

- Test chạy song song (`pytest-xdist`) → mỗi test dùng `tmp_path`, không đụng DB chung.
- `get_settings` cache giữa test → fixture `cache_clear`.
- AppTest có thể chậm; nếu flaky, đánh dấu `@pytest.mark.slow` và không chặn CI.
- PDF tiếng Việt trong PyMuPDF có thể lỗi font; test NFC ở hàm `_clean_text` thay vì PDF.
- Test encrypted PDF: PyMuPDF save với `encryption=fitz.PDF_ENCRYPT_AES_256`, `owner_pw`, `user_pw`.
- Test scan PDF: tạo trang trắng hoặc chèn ảnh; `get_text` rỗng.
- Test retry: fake raise 2 lần; monkeypatch sleep để nhanh.

## 6. Tiêu chí xong

- [ ] `pytest -q` xanh, không cần Qdrant/API key.
- [ ] `pytest --cov=app` ≥ 75% (hoặc ghi rõ phần chưa cover).
- [ ] Không có test gọi mạng thật.
- [ ] Không có test ghi vào `data/` thật.
- [ ] Integration test được skip rõ ràng nếu thiếu Qdrant.
- [ ] Thời gian chạy unit test < 30s.

## 7. Test (meta)

- Chạy `pytest -q` 2 lần liên tiếp → cùng kết quả.
- Chạy `pytest -q -m "not integration"` → pass.
- Chạy `pytest -q -m integration` khi Qdrant tắt → skip, không fail.

## 8. Tham chiếu

- Kế hoạch §9.1.
- S-23, S-24, S-26.
