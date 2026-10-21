# T-01-2 — `PdfPort.inspect`: kiểm tra nhanh PDF khi tải lên

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01 (P0) — AC-01.2; US-03 — AC-03.2 |
| Sprint | S2 |
| Tầng | INF |
| Ước lượng | 1d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | F-10, gate G-03 (chọn PyMuPDF hay pypdfium2) |
| Chặn | T-01-4 |

## Bối cảnh

SADD §5.3.2: upload kiểm tra nhanh `needs_pass` và `page_count` **trong subprocess** để từ chối ngay PDF mã hoá hoặc vượt số trang; kiểm tra text layer đầy đủ để cho worker.

## Phạm vi

**Làm:** định nghĩa `PdfPort` (đủ 3 method, 2 method còn lại để T-04-1/T-13d-1 cài), cài `inspect` cho adapter PyMuPDF.

## Đặc tả

```python
@dataclass(frozen=True)
class PdfInfo:
    is_pdf: bool
    needs_pass: bool
    page_count: int | None
    error: str | None = None          # "open_failed" | None

class PdfPort(Protocol):
    def inspect(self, path: Path) -> PdfInfo: ...
    def extract_pages(self, path: Path) -> list[PageText]: ...                       # T-04-1
    def render_page(self, path: Path, page: int, highlight: str | None) -> bytes: ...  # T-13d-1
```

Hàm chạy trong sandbox (`app/infrastructure/pdf/pymupdf_impl.py`, hàm top-level):

```python
def _inspect(path: str) -> dict:
    import fitz                                   # import trong process con
    try:
        with fitz.open(path, filetype="pdf") as doc:
            return {"is_pdf": doc.is_pdf, "needs_pass": bool(doc.needs_pass),
                    "page_count": None if doc.needs_pass else doc.page_count}
    except Exception:
        return {"is_pdf": False, "needs_pass": False, "page_count": None, "error": "open_failed"}
```

Adapter: `PyMuPdfAdapter.inspect(path)` = `run_in_sandbox(_inspect, str(path), timeout_s=10, mem_mb=512)`; `SandboxTimeout`/`SandboxCrashed` → `PdfInfo(is_pdf=False, needs_pass=False, page_count=None, error="open_failed")`.

Nếu G-03 chọn `pypdfium2`: viết `PdfiumAdapter` cùng interface (`pdfium.PdfDocument(path)`; mật khẩu sai ném `PdfiumError`). Service không đổi.

## Tiêu chí xong

- [ ] `text.pdf` → `is_pdf=True, needs_pass=False, page_count=N`.
- [ ] `encrypted.pdf` → `needs_pass=True`.
- [ ] `corrupt.pdf` và `fake.docx` → `error="open_failed"`.
- [ ] Thời gian `inspect` tệp 25 MB/400 trang ≤ 1 s (kể cả khởi động subprocess).

## Test

`tests/integration/pdf/test_inspect.py` với fixture T-03-4.

## Tham chiếu

SADD §5.3.2, §5.7.3, §5.8.4 · RISK-13 · F-10
