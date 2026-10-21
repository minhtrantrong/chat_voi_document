# T-01-7 — Hộp thoại tệp trùng tên (SCR-07)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01 (P0), US-02 (P1) |
| Sprint | S2 |
| Tầng | UI |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-01-5, T-01-6 |
| Chặn | T-02-2 |

## Bối cảnh

Thiết kế [07-duplicate-file.html](../../design/html_design/07-duplicate-file.html). Quyết định C-12.

## Phạm vi

**Làm:** `app/ui/components/duplicate_dialog.py` dùng `@st.dialog`.

## Đặc tả

```python
@st.dialog(t("dup.title"))                 # "Tệp đã tồn tại"
def duplicate_dialog(svc, actor, pending: UploadInput, remaining: int) -> None:
    st.write(t("dup.body", file_name=pending.file_name))
    # "Đã có tài liệu tên «{file_name}». Bạn muốn thay thế tài liệu cũ hay giữ cả hai?"
    st.caption(t("dup.replace_warning"))   # "Thay thế sẽ xoá tài liệu cũ; trích dẫn cũ sẽ hiển thị «Tài liệu đã bị xoá»."
    apply_all = st.checkbox(t("dup.apply_all"), key="dup.apply_all") if remaining > 0 else False
    c1, c2, c3 = st.columns(3)
    if c1.button(t("dup.replace"), type="primary", key="dup.replace"): decide("REPLACE", apply_all)
    if c2.button(t("dup.keep_both"), key="dup.keep_both"):            decide("KEEP_BOTH", apply_all)
    if c3.button(t("common.cancel"), key="dup.cancel"):               decide(None, apply_all)
```

`decide(choice, apply_all)`:
- `choice is None`: bỏ tệp này (không tải lên), toast "Đã bỏ qua {file_name}".
- Ngược lại: gọi `svc.documents.upload(actor, [replace(pending, on_conflict=choice)], ...)`. Với `apply_all` thì áp cho mọi tệp `NAME_CONFLICT` còn lại trong lô.
- Xong tất cả tệp đang chờ: tăng `K.DOCS_UPLOAD_NONCE`, đóng dialog, `st.rerun()`.

State chờ: `st.session_state["docs.pending_conflicts"]: list[str]` (lưu **tên tệp**; tham chiếu `UploadedFile` lấy lại từ widget hiện tại theo tên).

## Tiêu chí xong

- [ ] Tải lại tệp cùng tên khác nội dung → dialog hiện tên tệp; "Giữ cả hai" tạo `ten (2).pdf`; "Thay thế" thay tài liệu cũ.
- [ ] Lô 3 tệp trùng tên + "Áp dụng cho các tệp còn lại" → chỉ hỏi một lần.
- [ ] "Huỷ" không tạo tài liệu nào.

## Test

`tests/unit/ui/test_duplicate_dialog.py` (AppTest).

## Tham chiếu

Blueprint SCR-07, §3.1 (ConfirmDialog) · Implement_plan §14 C-12
