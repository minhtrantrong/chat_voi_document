# T-06-5 — Hộp thoại xác nhận xoá (SCR-06) và xử lý sau khi xoá

| Thuộc tính | Giá trị |
|---|---|
| Story | US-06 (P0) — AC-06.1; US-23 |
| Sprint | S4 |
| Tầng | UI |
| Ước lượng | 0.75d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-06-2, T-05-3, T-13d-3 |
| Chặn | T-23-2 |

## Bối cảnh

Thiết kế [06-confirm-delete.html](../../design/html_design/06-confirm-delete.html): nêu tên tệp và cảnh báo ảnh hưởng tới trích dẫn trong hội thoại cũ. Thao tác trên tài liệu đã bị người khác xoá → toast "Tài liệu không còn tồn tại".

## Phạm vi

**Làm:** `app/ui/components/delete_dialog.py`.

## Đặc tả

```python
@st.dialog(t("delete.title"))                       # "Xoá tài liệu?"
def delete_dialog(svc, actor, doc: DocumentDTO) -> None:
    st.write(t("delete.body", file_name=doc.file_name))
    # "Tài liệu «{file_name}» sẽ bị xoá khỏi danh sách của mọi người và không còn được dùng để trả lời."
    st.caption(t("delete.citation_warning"))         # "Các trích dẫn tới tài liệu này trong hội thoại cũ sẽ hiển thị «Tài liệu đã bị xoá»."
    c1, c2 = st.columns(2)
    if c1.button(t("common.cancel"), key=f"del.cancel:{doc.id}"): st.rerun()
    if c2.button(t("delete.confirm"), key=f"del.ok:{doc.id}", type="primary"):
        try:
            svc.documents.delete(actor, doc.id)
            st.toast(t("delete.done", file_name=doc.file_name))
        except NotFound:
            st.toast(t("doc.not_exists"))            # "Tài liệu không còn tồn tại"
        after_delete_cleanup(doc.id)
        st.rerun()

def after_delete_cleanup(doc_id):
    st.session_state.get(K.CHAT_SCOPE, {}).pop(str(doc_id), None)
    if st.session_state.get(K.SOURCE_DOC) == doc_id: close_source()
```

- Lỗi khác (`AppError`) hiển thị trong dialog bằng `st.error(error_text(err))`, không đóng dialog.
- Nút "Xoá" chỉ hiện ở menu ⋯ khi `doc.can_delete`.

## Tiêu chí xong

- [ ] Dialog hiện đúng tên tệp và cảnh báo.
- [ ] Xác nhận → tài liệu biến khỏi danh sách sau rerun (≤ 1 s); chip trích dẫn cũ đổi sang "Tài liệu đã bị xoá".
- [ ] Tài liệu đã bị người khác xoá → toast "Tài liệu không còn tồn tại", danh sách làm mới.

## Test

`tests/unit/ui/test_delete_dialog.py` (AppTest).

## Tham chiếu

US-06 · Blueprint SCR-06, §3.6.4
