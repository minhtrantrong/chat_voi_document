# T-11-4 — NotFoundMessage: thẻ "Không tìm thấy" ở giao diện

| Thuộc tính | Giá trị |
|---|---|
| Story | US-11 (P0) — AC-11.1 |
| Sprint | S3 |
| Tầng | UI |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-10-5, F-03 |
| Chặn | — |

## Bối cảnh

Blueprint ADR-UX-06: "Không tìm thấy" là **trạng thái UI riêng**, không phải lỗi — thẻ trung tính (xám), biểu tượng 🔍, gợi ý "thử diễn đạt khác / chọn thêm tài liệu", không có chip, **có** FeedbackBar.

## Phạm vi

**Làm:** nhánh `outcome == NOT_FOUND` trong `render_answer`.

## Đặc tả

```python
if a.outcome == "NOT_FOUND":
    with st.chat_message("assistant", avatar="🔍"):
        with st.container(border=True):
            st.markdown(a.segments[0].text if a.segments else t("answer.not_found"))
            st.caption(t("answer.not_found_hint"))     # "Thử diễn đạt khác hoặc chọn thêm tài liệu trong phạm vi hỏi."
        if flags.feedback: feedback_bar(svc, actor, a)
    return
```

- Không dùng `st.error`/`st.warning` (màu đỏ/vàng gây hiểu là lỗi).
- Nội dung thẻ lấy từ segment đã lưu (đúng ngôn ngữ, T-11-1), không dịch lại ở UI.

## Tiêu chí xong

- [ ] Thẻ NOT_FOUND không có chip, có 🔍 và gợi ý, có 👍/👎.

## Test

`tests/unit/ui/test_not_found_message.py` (AppTest).

## Tham chiếu

Blueprint ADR-UX-06, §3.5.3 (AnswerMessage) · US-11
