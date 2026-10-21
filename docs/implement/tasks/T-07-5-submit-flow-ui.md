# T-07-5 — Luồng gửi câu hỏi ở UI: hiển thị tức thì và khởi động stream

| Thuộc tính | Giá trị |
|---|---|
| Story | US-07 (P0) — AC-07.1; US-13 — AC-13.2 (chỉ báo ≤ 300 ms) |
| Sprint | S3 |
| Tầng | UI |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-07-2, T-07-4, T-13-6 |
| Chặn | — |

## Bối cảnh

AC-13.2: chỉ báo "đang tìm trong tài liệu…" hiển thị ≤ 300 ms sau khi gửi. `ask` chỉ là một transaction ngắn, nên có thể hiển thị câu hỏi + chỉ báo ngay trong cùng lần chạy script.

## Phạm vi

**Làm:** hàm `on_submit(q)` trong `app/ui/components/chat_panel.py`.

## Đặc tả

```python
q = render_composer(svc, actor)
if q is not None:
    if session_expired(...): ... (T-21-6)
    with message_container:
        user_message(q)                                   # hiện ngay câu hỏi
        st.caption(t("chat.phase.retrieving"))            # "Đang tìm trong tài liệu…"
    key = st.session_state.setdefault("chat.submit_key", str(new_id()))
    handle = run_safely(lambda: svc.qa.ask(actor, AskCommand(
        conversation_id=st.session_state.get(K.CHAT_CONV_ID), question=q,
        scope_doc_ids=selected_scope_ids(), idempotency_key=key)))
    del st.session_state["chat.submit_key"]
    if handle:
        st.session_state.update({K.CHAT_CONV_ID: handle.conversation_id,
                                 K.CHAT_ACTIVE_ANSWER: handle.answer_id,
                                 K.CHAT_LAST_ID: "0-0", K.CHAT_BUF: "", K.CHAT_DONE: None,
                                 K.CHAT_PHASE: "retrieving", K.CHAT_STARTED_AT: time.monotonic()})
        st.rerun()                                        # lần chạy sau render fragment stream (T-13-6)
```

- `chat.submit_key` sinh một lần cho mỗi lần submit, nên double-click hoặc rerun giữa chừng không tạo hai answer (kết hợp T-07-3).
- Lỗi `RateLimited` / `ERR_BUDGET` / `ERR_NO_READY_DOC` hiển thị bằng `st.error` ngay dưới câu hỏi; câu hỏi vẫn hiển thị (không mất nội dung người dùng nhập).
- Scope: `selected_scope_ids()` từ T-13c-1 (cờ tắt → `[]`).

## Tiêu chí xong

- [ ] Gửi câu hỏi: câu hỏi và chỉ báo hiện trước khi `ask` trả về (đo E2E ≤ 300 ms).
- [ ] Lỗi rate limit hiện thông báo có số giây chờ; câu hỏi vẫn hiển thị.

## Test

`tests/unit/ui/test_submit_flow.py` (AppTest với `FakeQaService`); E2E đo thời gian thuộc T-13-6.

## Tham chiếu

US-07, US-13 AC-13.2 · Blueprint §3.6.2, §3.7.2
