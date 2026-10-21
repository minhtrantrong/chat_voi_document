# T-03-1 — Bảng thông điệp lỗi tệp đúng nguyên văn AC

| Thuộc tính | Giá trị |
|---|---|
| Story | US-03 — Biết tệp nào bị từ chối và vì sao (P0) — AC-03.1…03.3 |
| Sprint | S2 |
| Tầng | UI |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | F-02, F-03 |
| Chặn | T-01-6, T-03-3 |

## Bối cảnh

AC-03.x quy định nguyên văn thông điệp. Mọi nơi hiển thị lỗi tệp (dropzone, chip Lỗi) dùng chung bảng này qua `error_text`.

## Phạm vi

**Làm:** thêm các khoá `doc.error.*` vào `app/ui/i18n/vi.py` và test so khớp nguyên văn.

## Đặc tả

| Khoá | Chuỗi (bắt buộc giữ nguyên phần in nghiêng của AC) |
|---|---|
| `doc.error.PDF_NOT_PDF` | `{file_name}: chỉ hỗ trợ PDF` |
| `doc.error.PDF_ENCRYPTED` | `{file_name}: tệp được bảo vệ bằng mật khẩu, không thể đọc` |
| `doc.error.PDF_NO_TEXT` | `{file_name}: không có văn bản trích xuất được (PDF dạng ảnh scan chưa được hỗ trợ)` |
| `doc.error.PDF_TOO_LARGE` | `{file_name}: dung lượng {actual_mb} MB vượt giới hạn {limit_mb} MB` |
| `doc.error.PDF_TOO_MANY_PAGES` | `{file_name}: {actual} trang vượt giới hạn {limit} trang` |
| `doc.error.PDF_CORRUPT` | `{file_name}: tệp PDF không hợp lệ hoặc bị hỏng` |
| `doc.error.EXTRACT_FAILED` | `{file_name}: không thể đọc tệp, hãy thử lại hoặc liên hệ quản trị` |
| `doc.error.EMBED_FAILED` | `{file_name}: tạm thời không xử lý được tài liệu, hãy thử lại` |
| `doc.error.INDEX_FAILED` | (như trên) |
| `doc.error.WORKER_LOST` | (như trên) |

Hiển thị ở chip Lỗi trong danh sách (T-03-3) có thể bỏ tiền tố `{file_name}: ` vì tên tệp đã nằm trên dòng — tạo thêm khoá rút gọn `doc.error_short.*` không có tên tệp.

`actual_mb` định dạng 1 chữ số thập phân, dấu phẩy thập phân theo tiếng Việt (`31,2`).

## Tiêu chí xong

- [ ] Test so khớp nguyên văn 3 chuỗi của AC-03.1/03.2/03.3 xanh.
- [ ] Mọi `DocErrorCode` liên quan tài liệu có cả khoá đầy đủ và khoá rút gọn.

## Test

`tests/unit/ui/test_file_error_messages.py`:
- `error_text(DocErrorCode.PDF_NOT_PDF, file_name="bao-cao.docx") == "bao-cao.docx: chỉ hỗ trợ PDF"`.
- Tương tự cho `PDF_ENCRYPTED`, `PDF_NO_TEXT`.

## Tham chiếu

US-03 · SADD §10.4 · F-03
