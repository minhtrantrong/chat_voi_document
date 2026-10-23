# S-07 — Extract text theo trang

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01, US-03, US-08 |
| Phase | P1 |
| Tầng | APP |
| Ước lượng | 0,25d |
| Phụ thuộc | S-06 |
| Chặn | S-08, S-11 |
| Owner gợi ý | Backend |

## 1. Mục tiêu

Extract text từng trang PDF, chuẩn hoá Unicode, bỏ trang rỗng và phát hiện PDF scan (không có text) để báo lỗi thay vì đưa vào Qdrant.

## 2. Phạm vi

**Làm:**

- `extract_pages(path, *, min_text_chars_per_page=20) -> list[PageText]`.
- Page number **1-based**.
- Chuẩn hoá NFC, bỏ ký tự NUL, strip đầu/cuối.
- Bỏ trang có text < ngưỡng.
- Nếu không còn trang nào có text → raise `PdfError("PDF_NO_TEXT", ...)`.
- Log số trang đọc được / bỏ qua (không log nội dung).

**Không làm:**

- OCR ảnh trong PDF.
- Giữ layout cột/phức tạp chính xác tuyệt đối.
- Extract bảng/biểu mẫu có cấu trúc.

## 3. File chính

```text
app/pdf.py   # thêm PageText + extract_pages
tests/test_pdf_extract.py
```

## 4. Đặc tả

### 4.1 DTO

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class PageText:
    page: int          # 1-based
    text: str
```

### 4.2 Hàm

```python
import unicodedata
import fitz

def _clean_text(raw: str) -> str:
    text = raw.replace("\x00", "")
    text = unicodedata.normalize("NFC", text)
    return text.strip()

def extract_pages(
    path: Path,
    *,
    min_text_chars_per_page: int = 20,
) -> list[PageText]:
    try:
        doc = fitz.open(path)
    except Exception as exc:
        raise PdfError("PDF_CORRUPT", "Không mở được tệp PDF.", detail=str(exc)) from exc

    pages: list[PageText] = []
    skipped = 0
    try:
        for index in range(doc.page_count):
            page = doc.load_page(index)
            try:
                raw = page.get_text("text", sort=True)
            except Exception:
                skipped += 1
                continue
            text = _clean_text(raw)
            if len(text) < min_text_chars_per_page:
                skipped += 1
                continue
            pages.append(PageText(page=index + 1, text=text))
    finally:
        doc.close()

    if not pages:
        raise PdfError(
            "PDF_NO_TEXT",
            "PDF không có văn bản để tìm kiếm (có thể là PDF scan). "
            "Ứng dụng chưa hỗ trợ OCR.",
            detail=f"pages={doc.page_count}, skipped={skipped}",
        )
    return pages
```

**Lưu ý:** không dùng `doc.page_count` sau `doc.close()` trong thực tế; lưu biến `page_count = doc.page_count` trước khi đóng. Đoạn trên chỉ minh hoạ, khi implement phải sửa.

### 4.3 Quy ước offset

- `PageText.text` là text **sau khi clean**; S-08 tính `char_start/char_end` trên chính chuỗi này.
- Không giữ text gốc để tránh lệch offset.
- Với trang có header/footer lặp, chấp nhận giữ lại; không làm sạch nâng cao trong bản này.

### 4.4 Chọn `sort=True`

- `sort=True` giúp thứ tự đọc tự nhiên hơn với PDF nhiều cột.
- Nếu chất lượng text giảm ở một số PDF, có thể thử `sort=False`; ghi chú trong code. Không cần config hoá.

## 5. Trường hợp biên

- PDF toàn ảnh scan → `PDF_NO_TEXT`.
- PDF có 1 trang text + 10 trang scan → giữ trang text, bỏ trang scan; vẫn chat được nhưng thiếu nội dung scan.
- Trang chỉ có số trang/header ngắn < 20 ký tự → bị bỏ; có thể làm mất nội dung ngắn thật. Ghi rõ ngưỡng trong config; có thể giảm còn 5 nếu cần.
- Text có ký tự Unicode tổ hợp (tiếng Việt) → NFC để tìm kiếm/embedding ổn định.
- PDF có ký tự NUL → bỏ.
- Trang hỏng giữa PDF → bỏ trang đó, không làm hỏng cả tài liệu; nếu tất cả hỏng → `PDF_NO_TEXT`.
- PDF mã hoá → S-06 đã chặn; nếu vào tới đây, `get_text` có thể rỗng → `PDF_NO_TEXT`.

## 6. Tiêu chí xong

- [ ] Trả đúng số trang có text, page 1-based.
- [ ] Text NFC, không còn NUL.
- [ ] PDF scan → `PDF_NO_TEXT`.
- [ ] PDF hỗn hợp → giữ trang có text.
- [ ] Không log nội dung text.
- [ ] Đóng `fitz.Document` trong `finally`.

## 7. Test

`tests/test_pdf_extract.py`:

- `test_extract_single_page`.
- `test_extract_multiple_pages` (kiểm tra số trang + thứ tự).
- `test_text_is_nfc` (chuỗi có dấu tổ hợp).
- `test_blank_pages_skipped`.
- `test_scanned_pdf_raises_no_text` (tạo PDF chỉ có ảnh hoặc trang trắng).
- `test_mixed_pdf_keeps_text_pages`.
- `test_page_numbers_are_one_based`.

Fixture: tạo PDF bằng PyMuPDF, `insert_text` với font mặc định; tiếng Việt có thể không hiển thị đúng trong PDF test, nên test NFC bằng cách gọi `_clean_text` trực tiếp.

## 8. Tham chiếu

- Kế hoạch §1.2, §7.1.
- S-06, S-08, S-11.
