# T-10-5 — AnswerView: hiển thị câu trả lời hoàn tất theo segment

| Thuộc tính | Giá trị |
|---|---|
| Story | US-10 (P0); US-09 (nhiều tài liệu) |
| Sprint | S3 |
| Tầng | UI |
| Ước lượng | 0.75d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-10-4, T-07-1 |
| Chặn | T-13-7, T-15-2 (hiển thị lịch sử) |

## Bối cảnh

Quyết định **C-03**: mỗi segment là một khối `st.markdown`, ngay dưới là hàng chip của segment đó — chip gắn đúng đoạn, không gom cuối câu trả lời (ADR-UX-02).

## Phạm vi

**Làm:** `app/ui/components/answer_view.py::render_answer(answer: AnswerDTO)` cho outcome `ANSWERED` (các biến thể khác ở T-11-4, T-13-7).

## Đặc tả

```python
def render_answer(svc, actor, a: AnswerDTO, flags: Flags) -> None:
    with st.chat_message("assistant", avatar="📄"):
        for seg in a.segments:
            st.markdown(seg.text)                         # HTML trong text bị escape (không unsafe_allow_html)
            if seg.cited:
                citation_row(a.id, seg, flags)            # T-10-4
        if flags.feedback:
            feedback_bar(svc, actor, a)                   # T-19-2
```

- Câu hỏi của người dùng: `st.chat_message("user")` + `st.markdown(escape_md(question))` (escape để câu hỏi không render markdown lạ).
- Segment `cited=False`: hiển thị như chữ thường, không chip.
- Markdown an toàn: Streamlit không render HTML khi `unsafe_allow_html=False`; thêm kiểm tra: link trong câu trả lời (`[x](javascript:...)`) — Streamlit đã chặn `javascript:`; vẫn thêm test xác nhận.
- Danh sách tin nhắn: render toàn bộ hội thoại hiện tại từ `ConversationDTO` (T-15-1); key container theo `answer.id`.

## Tiêu chí xong

- [ ] Câu trả lời 2 segment từ 2 tài liệu hiển thị 2 khối, mỗi khối có chip của đúng tài liệu (SCR-05, US-09).
- [ ] Câu trả lời chứa `<script>` hiển thị như chữ.

## Test

`tests/unit/ui/test_answer_view.py` (AppTest với AnswerDTO giả).

## Tham chiếu

Blueprint §3.5.3 (AnswerMessage), ADR-UX-02 · Implement_plan §14 C-03 · US-09, US-10
