# T-02-2 — UI kết quả tải lên theo lô

| Thuộc tính | Giá trị |
|---|---|
| Story | US-02 (P1) |
| Sprint | S2 |
| Tầng | UI |
| Ước lượng | 1d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-02-1, T-01-6, T-01-7 |
| Chặn | — |

## Bối cảnh

Thiết kế [04-main-processing.html](../../design/html_design/04-main-processing.html): nhiều tệp, mỗi tệp một dòng trạng thái. Quyết định **C-15**: tiến trình tải lên do Streamlit hiển thị; bước xử lý chỉ có chip "Đang xử lý".

## Phạm vi

**Làm:** mở rộng `handle_results` của T-01-6 thành bảng kết quả lô; luồng nhiều `NAME_CONFLICT`.

## Đặc tả

Sau khi gọi `upload`, hiển thị một khối tóm tắt (giữ đến khi người dùng đóng hoặc tải lô mới):

| Outcome | Hiển thị |
|---|---|
| ACCEPTED | `✔ {file_name} — đã nhận, đang xử lý` |
| DUPLICATE | `ℹ {file_name} — đã có trong danh sách` |
| REJECTED | `⚠ {thông điệp lỗi T-03-1}` |
| NAME_CONFLICT | `? {file_name} — trùng tên, đang chờ bạn chọn` (mở SCR-07 lần lượt) |

- Dòng đầu: `t("upload.batch_summary", ok=a, dup=b, err=c)` ("Đã nhận 3 tệp · 1 trùng · 1 lỗi").
- Nhiều `NAME_CONFLICT`: lưu danh sách tên vào `docs.pending_conflicts`, mở `duplicate_dialog` cho tệp đầu, `remaining = len - 1`.
- Lỗi `ERR_DOC_413` (quá số tệp): một `st.error` duy nhất, không có dòng theo tệp.

## Tiêu chí xong

- [ ] Lô 5 tệp hỗn hợp hiển thị đúng 5 dòng với đúng biểu tượng.
- [ ] Lô 6 tệp hiển thị một thông báo "Tối đa 5 tệp mỗi lần, bạn đã chọn 6".

## Test

`tests/unit/ui/test_batch_upload_ui.py` (AppTest).

## Tham chiếu

US-02 · Blueprint SCR-04 · Implement_plan §14 C-13, C-15
