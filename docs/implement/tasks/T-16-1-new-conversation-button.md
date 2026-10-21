# T-16-1 — Nút "＋ Hội thoại mới" ở TopBar

| Thuộc tính | Giá trị |
|---|---|
| Story | US-16 — Bắt đầu hội thoại mới không mang ngữ cảnh cũ (P1) |
| Sprint | S4 |
| Tầng | UI |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | PLT-07, F-11 (`reset_chat_state`), T-07-6 |
| Chặn | T-16-2 |

## Bối cảnh

Blueprint: nút "＋ Hội thoại mới" ở TopBar, hiển thị trên mọi màn hình chính; sau khi bấm thấy trạng thái SCR-03. Hội thoại chỉ được tạo khi gửi câu đầu tiên (T-07-6).

## Phạm vi

**Làm:** nút trong `top_bar.py`.

## Đặc tả

```python
if st.button(t("topbar.new_conversation"), key="topbar.new", icon="➕"):
    reset_chat_state(keep_scope=True)
    st.rerun()
```

`reset_chat_state(keep_scope=True)` xoá: `K.CHAT_CONV_ID`, `K.CHAT_ACTIVE_ANSWER`, `K.CHAT_LAST_ID`, `K.CHAT_BUF`, `K.CHAT_PHASE`, `K.CHAT_DONE`, `K.CHAT_STARTED_AT`, toàn bộ `source.*`; giữ `K.CHAT_SCOPE` và `docs.*`.

- Bấm khi đang stream: answer cũ vẫn chạy và được lưu ở hội thoại cũ; UI chuyển sang trạng thái trống ngay.
- Nút luôn bật (kể cả khi chưa có tài liệu).

## Tiêu chí xong

- [ ] Sau khi bấm: cột giữa ở trạng thái SCR-03 (hoặc SCR-02/04 theo tài liệu), khung Nguồn rỗng, phạm vi giữ nguyên.
- [ ] Không có bản ghi `conversations` mới cho tới khi gửi câu hỏi.

## Test

`tests/unit/ui/test_new_conversation.py` (AppTest).

## Tham chiếu

US-16 · Blueprint §3.1 (TopBar) · SADD §5.7.1
