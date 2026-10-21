# T-17-3 — Mục "Tóm tắt" trong menu ⋯ của tài liệu (P2)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-17 (P2) |
| Sprint | S4 — chỉ khi còn dung lượng |
| Tầng | UI |
| Ước lượng | 0.25d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-17-1, T-05-3, T-13-6 |
| Chặn | — |

## Bối cảnh

US-17: mục "Tóm tắt" trong menu "⋯" của `DocumentItem` (cờ tính năng P2); kết quả hiển thị trong khung hội thoại.

## Phạm vi

**Làm:** thêm mục vào `st.popover("⋯")` (T-05-3).

## Đặc tả

```python
if flags.summarize and d.status == "READY":
    if st.button(t("doc.summarize"), key=f"sum:{d.id}"):           # "Tóm tắt"
        handle = run_safely(lambda: svc.qa.summarize(actor, d.id, st.session_state.get(K.CHAT_CONV_ID)))
        if handle: start_streaming(handle); st.rerun()
```

- Đang có câu trả lời stream → nút bị `disabled` (như Composer).
- `start_streaming` là hàm dùng chung với T-07-5 (đặt state và rerun).

## Tiêu chí xong

- [ ] Cờ tắt: không thấy mục. Cờ bật: bấm → hội thoại hiện câu "Tóm tắt tài liệu «…»" và câu trả lời stream.

## Test

`tests/unit/ui/test_summarize_menu.py` (AppTest).

## Tham chiếu

US-17 · Implement_plan §14 C-18
