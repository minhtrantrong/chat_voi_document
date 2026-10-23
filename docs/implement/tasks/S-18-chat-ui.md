# S-18 — Chat UI, lịch sử phiên và streaming

| Thuộc tính | Giá trị |
|---|---|
| Story | US-07, US-08, US-09 |
| Phase | P2 |
| Tầng | UI |
| Ước lượng | 0,75d |
| Phụ thuộc | S-17 |
| Chặn | S-19, S-20, S-24, S-25 |
| Owner gợi ý | Full-stack |

## 1. Mục tiêu

Khu vực chat chính: hiển thị lịch sử trong phiên, nhận câu hỏi, stream câu trả lời, hiển thị nguồn và xử lý NOT_FOUND/lỗi. Không cần đăng nhập, không cần lưu DB.

## 2. Phạm vi

**Làm:**

- Render `st.session_state.messages` bằng `st.chat_message`.
- `st.chat_input` (S-19 sẽ thêm disabled).
- Gọi `prepare_answer` → nếu NOT_FOUND hiển thị thông báo; nếu có → stream.
- Lưu message assistant vào session (content + sources dạng dict).
- Hiển thị nguồn qua `render_sources` (S-20).
- Xử lý lỗi LLM/embedding bằng thông điệp thân thiện.
- Giới hạn hiển thị lịch sử (ví dụ 50 message) để tránh chậm.

**Không làm:**

- Lưu lịch sử qua refresh/restart.
- Nhiều cuộc hội thoại.
- Nút Stop/Cancel.
- Chọn tài liệu trong UI (S-21 chỉ chuẩn bị backend).
- Markdown nâng cao/LaTeX.

## 3. File chính

```text
app/main.py
app/ui.py            # render_sources, render_history (tuỳ chọn)
tests/test_chat_ui.py
```

## 4. Đặc tả

### 4.1 Cấu trúc message

```python
# st.session_state.messages
[
    {"role": "user", "content": "Hạn chót là khi nào?"},
    {
        "role": "assistant",
        "content": "Hạn chót là 30/11/2026 [S1].",
        "sources": [
            {"label": "S1", "file_name": "hop-dong.pdf", "page": 7,
             "text": "...", "score": 0.82}
        ],
    },
]
```

Khi gửi prompt cho LLM, chỉ lấy `role` + `content` (S-17 `_trim_history`).

### 4.2 Render lịch sử

```python
for msg in st.session_state.messages[-50:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            render_sources(msg["sources"])
```

**Lưu ý:** `st.markdown` render markdown; nội dung LLM có thể chứa HTML. Streamlit mặc định không cho HTML nguy hiểm; không bật `unsafe_allow_html`. Với nguồn, dùng expander + text thường.

### 4.3 Xử lý câu hỏi

```python
question = st.chat_input("Hỏi về nội dung tài liệu…", disabled=not has_ready)
if question and question.strip():
    question = question.strip()
    history_before = list(st.session_state.messages)

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            prepared = prepare_answer(question, history_before)
        except Exception as exc:
            log_error(exc, context="prepare_answer")
            st.error(error_message(exc))
            st.session_state.messages.pop()   # bỏ user vừa thêm? hoặc giữ
            st.stop()

        if prepared.not_found:
            st.markdown(NOT_FOUND)
            st.session_state.messages.append(
                {"role": "assistant", "content": NOT_FOUND, "sources": []}
            )
        else:
            placeholder = st.empty()
            with placeholder.container():
                text = st.write_stream(stream_answer(prepared))
            final_text, final_sources, not_found = finalize_answer(
                text, prepared.sources
            )
            if not_found or "KHONG_TIM_THAY" in text:
                placeholder.empty()
                placeholder.markdown(NOT_FOUND)
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_text,
                "sources": [_source_to_dict(s) for s in final_sources],
            })
            render_sources(final_sources)
```

**Vấn đề rerun:** Streamlit rerun sau khi nhập chat input; đoạn trên chạy một lần, append message, hiển thị. Lần tương tác sau, lịch sử được render từ session. Không gọi `st.rerun()` sau khi append để tránh mất stream/dup.

**Lỗi giữa stream:** `st.write_stream` có thể raise; bọc try/except, hiển thị `LLM_FAILED`, không append assistant rỗng. Có thể giữ user message để người dùng thử lại; hoặc pop cả user. Chọn giữ user, thêm assistant lỗi? Đơn giản: hiển thị `st.error(ERROR_MESSAGES["LLM_FAILED"])`, không append assistant. Lần render sau chỉ có user; chấp nhận.

### 4.4 `has_ready`

S-19 chịu trách nhiệm disable. S-18 có thể dùng:

```python
has_ready = any(d.status == "READY" for d in list_documents())
```

### 4.5 Chống trùng

- Nếu `question` rỗng → bỏ qua.
- Nếu đang stream và người dùng nhập tiếp → Streamlit chặn input trong lúc chạy; không cần lock.
- Nếu `prepare_answer` lỗi → không append assistant; user có thể hỏi lại.
- Không append 2 lần cùng câu hỏi do rerun: chỉ xử lý khi `question` có giá trị trong một run; `st.chat_input` trả None ở run sau.

## 5. Trường hợp biên

- Chưa có tài liệu READY → input disabled (S-19).
- Câu hỏi toàn khoảng trắng → bỏ qua.
- Câu hỏi rất dài → cắt 2000 ký tự trước khi gửi? Thêm:
  ```python
  question = question[:2000]
  ```
  tránh prompt quá lớn.
- LLM trả markdown có code block → `st.markdown` hiển thị; chấp nhận.
- LLM trả `KHONG_TIM_THAY` → thay bằng NOT_FOUND, không nguồn.
- LLM trả rỗng → NOT_FOUND.
- Embedding lỗi → `st.error(EMBEDDING_FAILED)`.
- Qdrant down → `st.error(QDRANT_UNAVAILABLE)`.
- Refresh trang → mất lịch sử (chấp nhận; ghi README).
- Xoá tài liệu (S-12) → clear `messages`; nếu không, lịch sử cũ vẫn hiển thị (xem S-12).
- Nguồn bị xoá nhưng message cũ còn → S-12 clear để tránh.
- Nhiều message → chỉ render 50 gần nhất; session vẫn giữ tất cả (có thể trim).

## 6. Tiêu chí xong

- [ ] Hỏi–đáp nhiều lượt trong một phiên.
- [ ] Câu trả lời stream ra từng token.
- [ ] Nguồn hiển thị dưới câu trả lời.
- [ ] NOT_FOUND không gọi LLM, không hiển thị nguồn.
- [ ] Lỗi LLM/embedding có thông báo thân thiện.
- [ ] Không append trùng message.
- [ ] Không dùng `unsafe_allow_html` cho nội dung LLM.

## 7. Test

- AppTest: render với `messages` seed → thấy nội dung.
- Manual: hỏi trong tài liệu, ngoài phạm vi, nhiều lượt.
- Unit: `_source_to_dict`, `has_ready`.
- Không test streaming thật trong CI (cần API); dùng manual hoặc fake.

## 8. Tham chiếu

- Kế hoạch §2 luồng chat, §8.
- S-12, S-17, S-19, S-20.
