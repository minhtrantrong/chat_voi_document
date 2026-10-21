# T-13d-3 — Khung Nguồn (SourcePanel): xem trang, điều hướng, đóng

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13d (P1) — AC-13d.1 |
| Sprint | S4 |
| Tầng | UI |
| Ước lượng | 1d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-13d-2, T-10-4, PLT-07 |
| Chặn | T-13d-5 |

## Bối cảnh

Thiết kế SCR-05 cột phải "Nguồn": tên tệp, điều hướng `tr. 7 / 32`, đoạn liên quan tô vàng; khi chưa chọn trích dẫn: khung rỗng kèm hướng dẫn. Quyết định **C-08**: không có phím Esc; có nút "✕ Đóng".

## Phạm vi

**Làm:** `app/ui/components/source_panel.py::render_source_panel(svc, actor)`; hàm `open_source(citation, key)` gọi từ chip (T-10-4).

## Đặc tả

```python
def open_source(c: CitationDTO, cite_key: str) -> None:
    st.session_state.update({K.SOURCE_DOC: c.document_id, K.SOURCE_PAGE: c.page,
                             K.SOURCE_QUOTE: c.quote, K.SOURCE_CITE_KEY: cite_key,
                             "source.quote_page": c.page})

def render_source_panel(svc, actor):
    st.subheader(t("source.title"))                                   # "Nguồn"
    doc_id = st.session_state.get(K.SOURCE_DOC)
    if not doc_id:
        st.caption(t("source.empty")); return                         # "Bấm vào một trích dẫn để xem trang gốc"
    page = st.session_state[K.SOURCE_PAGE]
    quote = st.session_state[K.SOURCE_QUOTE] if page == st.session_state.get("source.quote_page") else None
    img = run_safely(lambda: svc.documents.render_page(actor, doc_id, page, quote), on_error_toast=False)
    if img is None:                                                   # NotFound: tài liệu đã xoá trong lúc xem
        st.toast(t("doc.not_exists")); close_source(); st.rerun(); return
    top = st.columns([0.6, 0.4])
    top[0].markdown(f"**{escape_md(truncate_middle(img.file_name, 30))}**", help=img.file_name)
    if top[1].button(t("common.close"), key="source.close", icon="✕"): close_source(); st.rerun()
    nav = st.columns([0.2, 0.6, 0.2])
    nav[0].button("◀", key="source.prev", disabled=page <= 1, on_click=lambda: _go(page - 1))
    nav[1].caption(t("source.page_of", page=page, total=img.page_count))   # "tr. 7 / 32"
    nav[2].button("▶", key="source.next", disabled=page >= img.page_count, on_click=lambda: _go(page + 1))
    st.image(img.png, use_container_width=True)
```

- Chỉ trang của citation mới có highlight; chuyển sang trang khác thì không highlight; quay lại thì có lại.
- Khung Nguồn **không** nằm trong fragment poll; chỉ render lại khi người dùng thao tác.
- Màn hình hẹp: cột tự xếp xuống dưới (PLT-07); chấp nhận cho MVP.

## Tiêu chí xong

- [ ] Bấm chip `hop-dong.pdf · tr. 7` → khung Nguồn hiện đúng trang 7 có highlight (≤ 1 thao tác).
- [ ] ◀/▶ đổi trang; đóng khung trở về hướng dẫn rỗng.
- [ ] Tài liệu bị xoá khi đang xem → bấm ▶ thì toast và đóng khung.

## Test

`tests/unit/ui/test_source_panel.py` (AppTest với service giả); E2E ở T-13d-5.

## Tham chiếu

US-13d · Blueprint SCR-05, §3.5.3 · Implement_plan §14 C-08
