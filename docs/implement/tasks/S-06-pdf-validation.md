# S-06 — Validate và inspect PDF

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01, US-03 |
| Phase | P1 |
| Tầng | APP |
| Ước lượng | 0,5d |
| Phụ thuộc | S-03 |
| Chặn | S-07, S-11, S-14 |
| Owner gợi ý | Backend |

## 1. Mục tiêu

Chặn file không hợp lệ **trước khi** extract/embed: không phải PDF, quá dung lượng, quá số trang, PDF mã hoá, PDF hỏng. Trả về `PdfInfo` hoặc raise `PdfError` có mã ổn định để UI map thông điệp.

## 2. Phạm vi

**Làm:**

- `app/pdf.py`: `validate_filename`, `inspect_pdf`.
- Kiểm tra theo thứ tự: đuôi → size → magic bytes → mở PDF → mã hoá → số trang.
- Mã lỗi: `PDF_NOT_PDF`, `PDF_TOO_LARGE`, `PDF_TOO_MANY_PAGES`, `PDF_ENCRYPTED`, `PDF_CORRUPT`.
- `PdfInfo(page_count, needs_pass, is_pdf)`.

**Không làm:**

- Chưa extract text (S-07).
- Chưa OCR.
- Chưa kiểm tra virus/malware.
- Chưa dedupe theo checksum (ngoài phạm vi).

## 3. File chính

```text
app/pdf.py
tests/test_pdf.py
tests/fixtures/ (PDF mẫu tạo trong test)
```

## 4. Đặc tả

### 4.1 DTO và lỗi

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class PdfInfo:
    page_count: int
    needs_pass: bool
    is_pdf: bool

class PdfError(Exception):
    def __init__(self, code: str, message: str, *, detail: str | None = None):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(message)
```

### 4.2 Validate tên file

```python
def validate_filename(file_name: str) -> None:
    if not file_name.lower().endswith(".pdf"):
        raise PdfError("PDF_NOT_PDF", "Chỉ chấp nhận tệp PDF.")
```

Không tin `content_type` của trình duyệt; kiểm tra cả đuôi và magic.

### 4.3 Inspect

```python
from pathlib import Path
import fitz  # PyMuPDF

PDF_MAGIC = b"%PDF-"

def inspect_pdf(path: Path, *, max_pages: int, max_bytes: int) -> PdfInfo:
    if not path.exists():
        raise PdfError("PDF_CORRUPT", "Không tìm thấy tệp PDF.")
    if path.stat().st_size == 0:
        raise PdfError("PDF_CORRUPT", "Tệp PDF rỗng.")
    if path.stat().st_size > max_bytes:
        raise PdfError(
            "PDF_TOO_LARGE",
            f"Tệp vượt quá {max_bytes // (1024 * 1024)} MB.",
            detail=f"size={path.stat().st_size}",
        )

    with path.open("rb") as f:
        if f.read(5) != PDF_MAGIC:
            raise PdfError("PDF_NOT_PDF", "Tệp không phải PDF hợp lệ.")

    try:
        doc = fitz.open(path)
    except Exception as exc:
        raise PdfError("PDF_CORRUPT", "Không mở được tệp PDF.", detail=str(exc)) from exc

    try:
        if doc.needs_pass:
            raise PdfError("PDF_ENCRYPTED", "PDF đang được bảo vệ bằng mật khẩu.")
        if doc.page_count == 0:
            raise PdfError("PDF_CORRUPT", "PDF không có trang nào.")
        if doc.page_count > max_pages:
            raise PdfError(
                "PDF_TOO_MANY_PAGES",
                f"PDF có {doc.page_count} trang, vượt giới hạn {max_pages} trang.",
            )
        return PdfInfo(page_count=doc.page_count, needs_pass=False, is_pdf=True)
    finally:
        doc.close()
```

### 4.4 Hàm tiện dụng

```python
def validate_uploaded(path: Path, settings) -> PdfInfo:
    return inspect_pdf(
        path,
        max_pages=settings.max_pages,
        max_bytes=settings.max_upload_mb * 1024 * 1024,
    )
```

## 5. Trường hợp biên

- Đuôi `.PDF` viết hoa → chấp nhận.
- File `.pdf` nhưng nội dung là text/HTML → magic fail → `PDF_NOT_PDF`.
- File 0 byte → `PDF_CORRUPT`.
- PDF mã hoá nhưng `needs_pass=False`? PyMuPDF có thể mở; nếu extract rỗng S-07 xử lý.
- PDF có 0 trang → `PDF_CORRUPT`.
- PDF đúng số trang nhưng trang bị hỏng → S-07 xử lý từng trang; S-06 chỉ mở tổng.
- Tên file chứa Unicode/khoảng trắng → không ảnh hưởng; lưu bằng doc_id.
- `max_bytes` tính bằng byte; dùng `MAX_UPLOAD_MB`.
- File lớn hơn giới hạn: **kiểm tra size trước khi đọc toàn bộ** để tránh tốn RAM.

## 6. Tiêu chí xong

- [ ] Hàm validate không đọc toàn bộ file vào RAM.
- [ ] Mỗi mã lỗi có thể test độc lập.
- [ ] Không lộ stack trace/đường dẫn nội bộ trong `message`; `detail` chỉ để log.
- [ ] `PdfInfo.page_count` đúng với PDF thật.
- [ ] File hợp lệ → không raise.

## 7. Test

`tests/test_pdf.py`:

- Tạo PDF hợp lệ bằng `fitz.open()` + `insert_page` + `insert_text`.
- `test_valid_pdf`.
- `test_uppercase_extension`.
- `test_not_pdf`.
- `test_empty_file`.
- `test_too_large` (monkeypatch max_bytes nhỏ).
- `test_too_many_pages` (3 trang, max_pages=2).
- `test_encrypted_pdf` (tạo PDF có mật khẩu).
- `test_corrupt_pdf` (bytes rác có magic).
- `test_missing_file`.

## 8. Tham chiếu

- Kế hoạch §1.2, §7.1.
- S-07, S-11, S-14.
