# T-03-2 — Phát hiện PDF không có lớp văn bản (scan) trong ingest

| Thuộc tính | Giá trị |
|---|---|
| Story | US-03 (P0) — AC-03.3 |
| Sprint | S2 |
| Tầng | WRK / DOM |
| Ước lượng | 0.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-04-1 |
| Chặn | T-04-4 |

## Bối cảnh

OCR ngoài phạm vi (BR-028). PDF chỉ có ảnh scan phải kết thúc ở `ERROR` + `PDF_NO_TEXT`, không retry (C-14). PDF hỗn hợp (một số trang scan) vẫn được index phần có chữ.

## Phạm vi

**Làm:** hàm domain `classify_text_layer(pages, min_chars)` trong `app/ingestion/domain.py`, gọi trong handler ingest (T-04-4).

## Đặc tả

```python
@dataclass(frozen=True)
class TextLayerReport:
    total_pages: int; text_pages: int; empty_pages: list[int]
    @property
    def has_text(self) -> bool: return self.text_pages > 0

def classify_text_layer(pages: Sequence[PageText], min_chars: int) -> TextLayerReport:
    """Trang có len(text.strip()) >= min_chars là trang có chữ."""
```

Trong handler:

```text
report = classify_text_layer(pages, limits.min_text_chars_per_page)   # mặc định 20
if not report.has_text: raise PermanentJobError(DocErrorCode.PDF_NO_TEXT)
pages_to_chunk = [p for p in pages if p.page not in report.empty_pages]
log.info("text_layer", total=..., text_pages=..., empty=len(report.empty_pages))   # không log nội dung
```

- Ký tự đếm sau khi chuẩn hoá NFC và bỏ khoảng trắng; bỏ qua các ký tự rác thường gặp ở PDF scan có OCR lỗi (chuỗi toàn ký tự không chữ/số) — nếu tỉ lệ chữ/số < 30% thì coi như trang rỗng.
- Trường hợp `empty_pages` > 50% tổng số trang: tài liệu vẫn READY nhưng ghi `documents.error_detail = "partial_text:{n}"` để sau này có thể hiển thị cảnh báo (không bắt buộc hiển thị ở MVP).

## Tiêu chí xong

- [ ] `scan_only.pdf` → ERROR `PDF_NO_TEXT`, job FAILED (không retry).
- [ ] `mixed_scan.pdf` → READY; chunk chỉ đến từ trang có chữ.

## Test

`tests/unit/ingestion/test_text_layer.py` (dữ liệu giả); `tests/integration/ingestion/test_ingest_scan.py` (fixture T-03-4).

## Tham chiếu

US-03 AC-03.3 · SADD §10.4, RISK-03, TD-02 · Implement_plan §14 C-14
