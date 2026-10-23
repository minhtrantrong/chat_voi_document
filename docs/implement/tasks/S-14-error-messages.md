# S-14 — Mã lỗi và thông điệp tiếng Việt

| Thuộc tính | Giá trị |
|---|---|
| Story | US-03, US-04 |
| Phase | P1 |
| Tầng | APP + UI |
| Ước lượng | 0,25d |
| Phụ thuộc | S-06, S-11, S-12 |
| Chặn | S-17, S-18, S-25 |
| Owner gợi ý | Full-stack |

## 1. Mục tiêu

Mọi lỗi hiển thị cho người dùng có **mã ổn định** + **thông điệp tiếng Việt dễ hiểu** + gợi ý hành động. Không lộ stack trace, đường dẫn nội bộ, API key hay nội dung tài liệu.

## 2. Phạm vi

**Làm:**

- `app/errors.py`: bảng mã → thông điệp, hàm `error_message(exc, file_name=None)`.
- Map mã từ `PdfError`, `EmbeddingError`, `IngestError`, lỗi Qdrant/LLM.
- UI dùng `st.error(error_message(...))`.
- Log chi tiết ở mức `debug`/`warning` (không log nội dung).
- Fallback `INTERNAL` cho lỗi không xác định.

**Không làm:**

- Không sửa `app/shared/errors.py` (legacy của kế hoạch cũ). Task này tạo module mới độc lập.
- Không i18n đa ngôn ngữ; chỉ tiếng Việt.
- Không hiển thị mã lỗi cho người dùng cuối (chỉ trong log/expand DEBUG).

## 3. File chính

```text
app/errors.py
tests/test_errors.py
```

## 4. Đặc tả

### 4.1 Bảng mã

```python
ERROR_MESSAGES: dict[str, str] = {
    "PDF_NOT_PDF": "Tệp không phải PDF hợp lệ.",
    "PDF_TOO_LARGE": "Tệp vượt quá dung lượng cho phép.",
    "PDF_TOO_MANY_PAGES": "Tệp có quá nhiều trang.",
    "PDF_ENCRYPTED": "PDF đang được bảo vệ bằng mật khẩu. Hãy bỏ mật khẩu rồi tải lại.",
    "PDF_CORRUPT": "Không đọc được tệp PDF. Tệp có thể bị hỏng.",
    "PDF_NO_TEXT": "PDF không có văn bản để tìm kiếm (có thể là PDF scan). Ứng dụng chưa hỗ trợ OCR.",
    "EMBEDDING_FAILED": "Không tạo được vector cho tài liệu. Kiểm tra cấu hình embedding và thử lại.",
    "QDRANT_UNAVAILABLE": "Cơ sở dữ liệu vector chưa sẵn sàng. Kiểm tra Qdrant đang chạy.",
    "LLM_FAILED": "Trợ lý tạm thời không trả lời được. Thử lại sau.",
    "INGEST_FAILED": "Không xử lý được tài liệu. Thử lại hoặc xoá tệp.",
    "INTERNAL": "Đã xảy ra lỗi. Thử lại; nếu vẫn lỗi, kiểm tra log.",
}
```

### 4.2 Hàm

```python
def error_code(exc: BaseException) -> str:
    return getattr(exc, "code", "INTERNAL")

def error_message(exc: BaseException, file_name: str | None = None) -> str:
    code = error_code(exc)
    msg = ERROR_MESSAGES.get(code, ERROR_MESSAGES["INTERNAL"])
    if file_name:
        return f"{file_name}: {msg}"
    return msg
```

**Quy tắc:**

- Nếu `exc` có `message` riêng (ví dụ `PdfError.message` đã nói rõ giới hạn), ưu tiên `message`? Có thể dùng:
  ```python
  detail = getattr(exc, "message", None)
  base = detail if detail else ERROR_MESSAGES.get(code, ...)
  ```
  Nhưng `message` có thể chứa chi tiết kỹ thuật. Để an toàn, dùng bảng mã; chỉ dùng `message` cho các mã `PDF_TOO_LARGE`/`PDF_TOO_MANY_PAGES` nếu đã thân thiện. Đơn giản: bảng mã là nguồn chính; `PdfError.message` chỉ log.
- Không nối `str(exc)` vào UI.
- Với `file_name`, escape markdown nếu hiển thị qua `st.markdown`; `st.error` render markdown, nên dùng `st.error` với text thường hoặc escape.

### 4.3 Log

```python
import logging
logger = logging.getLogger(__name__)

def log_error(exc: BaseException, *, context: str) -> None:
    logger.warning(
        "error context=%s code=%s type=%s",
        context,
        error_code(exc),
        type(exc).__name__,
        exc_info=True,
    )
```

Không log `file_name`? Tên file không quá nhạy cảm nhưng có thể chứa thông tin; chỉ log khi cần debug. Không log text/PDF/question.

### 4.4 UI

```python
except Exception as exc:
    log_error(exc, context="ingest")
    st.error(error_message(exc, file_name))
```

Với chat (S-18):

```python
except Exception as exc:
    log_error(exc, context="chat")
    st.error(ERROR_MESSAGES["LLM_FAILED"])
```

## 5. Trường hợp biên

- Lỗi không có `code` → `INTERNAL`.
- `code` lạ → `INTERNAL`.
- `PdfError.message` chứa đường dẫn → không hiển thị; bảng mã an toàn.
- Lỗi Qdrant có message dài → không hiển thị.
- File name chứa markdown/HTML → escape hoặc dùng `st.error` với text; tránh XSS (Streamlit render markdown, HTML bị hạn chế nhưng vẫn cẩn thận).
- Nhiều lỗi cùng lúc → hiển thị từng lỗi, không gộp mất thông tin.
- Lỗi API key thiếu (`RuntimeError` từ `require_api_key`) → map `CONFIG_MISSING` (thêm mã).
- Lỗi LLM timeout → `LLM_FAILED`.

## 6. Tiêu chí xong

- [ ] Mỗi mã ở §4.1 có test.
- [ ] UI không bao giờ hiển thị `str(exc)` thô/stack trace.
- [ ] `file_name` được đính kèm khi có.
- [ ] Mã lạ → `INTERNAL`.
- [ ] Log có `exc_info` nhưng không có nội dung nhạy cảm.
- [ ] Không sửa `app/shared/`.

## 7. Test

`tests/test_errors.py`:

- `test_each_code_has_message`.
- `test_unknown_code_fallback`.
- `test_file_name_prefix`.
- `test_pdf_error_uses_code`.
- `test_no_raw_exception_text`.
- `test_log_does_not_include_secret` (tuỳ chọn).

## 8. Tham chiếu

- Kế hoạch §1.2 US-03, §8 trạng thái UI.
- S-06, S-11, S-12, S-18.
