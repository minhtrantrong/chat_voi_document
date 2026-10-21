# T-05-3 — UI danh sách tài liệu và DocumentItem

| Thuộc tính | Giá trị |
|---|---|
| Story | US-05 (P0) — AC-05.1 |
| Sprint | S2 |
| Tầng | UI |
| Ước lượng | 1d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-05-2, F-03, PLT-07 |
| Chặn | T-03-3, T-04-7, T-06-5, T-13c-1, T-17-3 |

## Bối cảnh

Thiết kế [03-main-ready.html](../../design/html_design/03-main-ready.html) cột Tài liệu: tên (cắt giữa nếu dài), ngày, số trang, chip trạng thái, hộp chọn phạm vi, menu "⋯". Blueprint §3.4 quy tắc hiển thị.

## Phạm vi

**Làm:** `render_document_list(svc, actor, page)` và `document_item(d)` trong `app/ui/components/document_list.py`; helper định dạng ở `app/ui/format.py`.

**Không làm:** nội dung nhánh lỗi (T-03-3), checkbox phạm vi (T-13c-1), dialog xoá (T-06-5).

## Đặc tả

Mỗi `document_item(d)` nằm trong `st.container(border=True, key=f"doc:{d.id}")`:

| Phần tử | Cách làm |
|---|---|
| Checkbox phạm vi | chỗ đặt sẵn, T-13c-1 điền |
| Tên | `st.markdown(f"**{escape_md(truncate_middle(d.file_name, 32))}**", help=d.file_name)` |
| Dòng phụ | `"{relative_date(d.uploaded_at)} · {d.page_count} trang"` |
| Chip trạng thái | PROCESSING: `◐ Đang xử lý` (`st.caption` màu `status.processing`); READY: `✔ Sẵn sàng`; ERROR: nhánh T-03-3 |
| Menu ⋯ | `st.popover("⋯", help=t("doc.actions"))`: "Xoá" (nếu `can_delete`), "Thử lại" (nếu `can_retry`), "Tóm tắt" (chỉ khi cờ `summarize` bật và READY, T-17-3) |

Helper (`app/ui/format.py`, có unit test):
- `truncate_middle("hop-dong-ky-thuat-phien-ban-cuoi.pdf", 24) == "hop-dong-ky…ban-cuoi.pdf"` (giữ đuôi `.pdf`).
- `relative_date(dt)`: theo `Asia/Ho_Chi_Minh`: "Hôm nay", "Hôm qua", còn lại `dd/MM/yyyy`.
- `escape_md(s)`: escape ký tự markdown (`*`, `_`, `[`, `]`, `` ` ``, `#`) để tên tệp không bị hiểu thành định dạng.

Danh sách: hiển thị `page.items`; có `next_cursor` thì nút "Xem thêm" tăng `K.DOCS_LIMIT` thêm 50 (đơn giản hơn ghép nhiều trang cursor, đủ cho ≤ 1.000 tài liệu).

Trạng thái rỗng (0 tài liệu): EmptyState SCR-02 "Tải PDF đầu tiên để bắt đầu hỏi".

## Tiêu chí xong

- [ ] Giao diện khớp SCR-03 về nội dung từng dòng.
- [ ] Tên tệp chứa `*` hoặc `_` hiển thị đúng chữ, không thành in nghiêng.
- [ ] Mọi widget lặp có key theo `doc.id`.

## Test

`tests/unit/ui/test_format.py`; `tests/unit/ui/test_document_list.py` (AppTest).

## Tham chiếu

US-05 · Blueprint §3.4, §3.5.3, SCR-02/03 · SADD §5.7.1
