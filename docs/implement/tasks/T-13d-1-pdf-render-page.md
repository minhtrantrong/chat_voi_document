# T-13d-1 — `PdfPort.render_page`: render trang PNG có highlight

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13d — Bấm trích dẫn để mở tài liệu gốc đúng trang (P1, khuyến nghị P0) — AC-13d.1 |
| Sprint | S4 |
| Tầng | INF |
| Ước lượng | 1d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | F-10 (SandboxPool), T-01-2 |
| Chặn | T-13d-2 |

## Bối cảnh

SADD §5.3.5 (SD-04): PyMuPDF render trang 144 dpi; highlight quote; không parse PDF trong process web chính (§5.8.4) → render qua pool subprocess.

## Phạm vi

**Làm:** hàm sandbox `_render(path, page, quote) -> bytes` và method `render_page` của adapter; pool dài hạn trong web.

## Đặc tả

```text
_render(path, page_no, quote):
  doc = fitz.open(path); page = doc[page_no - 1]
  rects = []
  if quote:
     for probe in (quote[:80], quote[:40], first_sentence(quote)[:60]):
         probe = probe.strip()
         if len(probe) >= 8 and (rects := page.search_for(probe, quads=False)): break
  for r in rects[:20]:
     annot = page.add_highlight_annot(r); annot.set_colors(stroke=(1, 0.92, 0.23)); annot.update()
  pix = page.get_pixmap(dpi=144, annots=True)
  return pix.tobytes("png")
```

- Không lưu thay đổi vào tệp (chỉ annot trong bộ nhớ).
- Trang xoay: `get_pixmap` đã tính `rotation`; kiểm tra với `rotated.pdf`.
- Kích thước PNG: trang A4 ở 144 dpi ≈ 1190 × 1684; nếu > 2 MB thì giảm còn 110 dpi.
- `PyMuPdfAdapter.render_page(path, page, highlight)` = `pool.submit(_render, str(path), page, highlight, timeout_s=15)`.
- Pool: `SandboxPool(max_workers=2, mem_mb=768)` tạo một lần trong `get_services()` (web).

## Tiêu chí xong

- [ ] `text.pdf` trang 2 với quote "Hạn chót nộp hồ sơ là 30/11/2026." → PNG có vùng màu vàng tại câu đó.
- [ ] Quote không tìm thấy → PNG không có highlight, không lỗi.
- [ ] `hyphen.pdf`: quote có từ bị ngắt dòng vẫn tìm được với probe ngắn hơn.
- [ ] Render một trang ≤ 1 s (pool đã khởi động).

## Test

`tests/integration/pdf/test_render.py` (kiểm tra pixel vàng bằng Pillow: tồn tại ≥ 200 pixel gần màu (255, 235, 59)).

## Tham chiếu

SADD §5.3.5, §5.8.4 · US-13d · UXQ-08
