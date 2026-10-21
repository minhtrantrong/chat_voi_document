# T-03-4 — Bộ PDF mẫu cho test

| Thuộc tính | Giá trị |
|---|---|
| Story | US-03 (P0); dùng chung US-01, US-02, US-04, US-13d, PLT-11 |
| Sprint | S2 (làm đầu sprint) |
| Tầng | TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | PLT-01 |
| Chặn | T-01-2, T-01-4, T-02-3, T-03-2, T-04-4 |

## Bối cảnh

Nhiều task cần cùng một bộ PDF có đặc điểm xác định. Tệp lớn không commit; sinh bằng script.

## Phạm vi

**Làm:** `tests/fixtures/pdf/generate.py` (dùng PyMuPDF hoặc reportlab) + fixture pytest `pdf_fixtures` (sinh vào thư mục tạm của session, cache theo hash script).

## Đặc tả

| Tệp | Đặc điểm | Dùng cho |
|---|---|---|
| `text.pdf` | 3 trang tiếng Việt có dấu, mỗi trang 3 đoạn; trang 2 chứa câu "Hạn chót nộp hồ sơ là 30/11/2026." | upload, ingest, chunk, highlight |
| `text2.pdf` | 2 trang tiếng Anh | lô, đa tài liệu |
| `scan_only.pdf` | 2 trang chỉ có ảnh (raster chữ) | `PDF_NO_TEXT` |
| `mixed_scan.pdf` | trang 1 chữ, trang 2 ảnh, trang 3 chữ | ingest một phần |
| `encrypted.pdf` | `text.pdf` mã hoá AES-256, mật khẩu `x` | `PDF_ENCRYPTED` |
| `corrupt.pdf` | header `%PDF-1.7` + byte ngẫu nhiên | `PDF_CORRUPT` |
| `fake.docx` | tệp DOCX thật | `PDF_NOT_PDF` |
| `fake_ext.pdf` | nội dung DOCX nhưng đuôi `.pdf` | magic bytes |
| `big_401_pages.pdf` | 401 trang mỗi trang 1 dòng | `PDF_TOO_MANY_PAGES` |
| `big_20mb.pdf` | ~20 MB (nhúng ảnh nén thấp) + 50 trang chữ | perf upload |
| `long_page.pdf` | 1 trang ~5.000 từ | chunk nhiều khối trong 1 trang |
| `rotated.pdf` | trang xoay 90° | render/highlight |
| `hyphen.pdf` | từ bị ngắt dòng bằng gạch nối | highlight quote |
| `unicode_name_hợp-đồng.pdf` | tên tệp tiếng Việt | tên Unicode |

- Nội dung chữ cố định (seed) để test chunk/citation tất định.
- Tệp > 1 MB không commit (`.gitignore`); script chạy tự động trong fixture.

## Tiêu chí xong

- [ ] `pytest --fixtures` liệt kê `pdf_fixtures`; sinh đủ 14 tệp trong ≤ 20 s.
- [ ] `encrypted.pdf` thật sự yêu cầu mật khẩu khi mở bằng trình xem PDF.

## Tham chiếu

US-03 · PLT-11 · F-10
