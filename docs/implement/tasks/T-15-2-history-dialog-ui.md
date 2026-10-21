# T-15-2 — Ngăn "Lịch sử hội thoại" (SCR-09)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-15 (P1) |
| Sprint | S4 |
| Tầng | UI |
| Ước lượng | 1d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-15-1, T-10-5, T-13-6 |
| Chặn | — |

## Bối cảnh

Thiết kế [09-history-drawer.html](../../design/html_design/09-history-drawer.html): mở từ nút "Lịch sử ▸" ở cột Tài liệu, nhóm theo Hôm nay / Hôm qua / 7 ngày trước. Quyết định **C-01**: dùng `@st.dialog`.

## Phạm vi

**Làm:** `app/ui/components/history_dialog.py`, nút mở ở cuối cột Tài liệu, việc mở một hội thoại cũ vào cột giữa.

## Đặc tả

```python
@st.dialog(t("history.title"), width="large")                 # "Lịch sử hội thoại"
def history_dialog(svc, actor):
    page = svc.conversations.list(actor, cursor=st.session_state.get("history.cursor"), limit=30)
    if not page.items: st.caption(t("history.empty")); return  # "Chưa có hội thoại nào"
    for group, items in group_by_day(page.items):               # "Hôm nay", "Hôm qua", "7 ngày trước", "Cũ hơn"
        st.caption(group)
        for c in items:
            if st.button(c.title, key=f"conv:{c.id}", use_container_width=True,
                         type="primary" if c.id == st.session_state.get(K.CHAT_CONV_ID) else "secondary"):
                open_conversation(c.id); st.rerun()
    if page.next_cursor and st.button(t("common.more"), key="history.more"): ...

def open_conversation(conv_id):
    reset_chat_state(keep_scope=True)                           # F-11
    st.session_state[K.CHAT_CONV_ID] = conv_id
```

Cột giữa (`chat_panel`): nếu có `K.CHAT_CONV_ID` thì `conv = svc.conversations.get(actor, id)` và render tất cả lượt (T-10-5 / T-11-4 / T-13-7). Nếu `conv.active_answer_id` có (answer cuối còn PENDING sau khi tải lại trang) → đặt `K.CHAT_ACTIVE_ANSWER`, `K.CHAT_LAST_ID="0-0"` để nối lại stream (T-13-6).

`group_by_day`: theo `Asia/Ho_Chi_Minh`; "7 ngày trước" = 2–7 ngày; còn lại "Cũ hơn".

## Tiêu chí xong

- [ ] Mở ngăn thấy hội thoại nhóm đúng ngày; bấm một mục hiển thị toàn bộ nội dung với chip trích dẫn.
- [ ] Đăng xuất/đăng nhập lại vẫn thấy hội thoại (AC-15.1).

## Test

`tests/unit/ui/test_history_dialog.py` (AppTest); `tests/unit/ui/test_group_by_day.py`.

## Tham chiếu

US-15 · Blueprint SCR-09 · Implement_plan §14 C-01
