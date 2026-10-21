# T-13-6 — UI fragment stream: hiển thị dần, nút Dừng, fallback DB, watchdog

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13 (P0) — AC-13.2; NFR-UX-01 |
| Sprint | S3 (bắt đầu cuối S2 trên `FakeQaService`) |
| Tầng | UI |
| Ước lượng | 1.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-13-1 (GO), T-07-1, T-10-3, T-13-4, T-13-5 |
| Chặn | T-07-5, T-13-7 |

## Bối cảnh

ADR-005 + kết quả spike T-13-1. SADD §5.3.4 bảng: poll 350–500 ms, fallback DB mỗi 2 s hoặc khi stream im > 5 s, watchdog 120 s, nút Dừng render **bên trong** fragment.

## Phạm vi

**Làm:** `app/ui/components/streaming.py::render_streaming(svc, actor, answer_id)`; gọi từ `chat_panel` khi `K.CHAT_ACTIVE_ANSWER` khác `None`.

## Đặc tả

```python
def render_streaming(svc, actor, aid):
    s = st.session_state
    with st.chat_message("assistant", avatar="📄"):
        @st.fragment(run_every=POLL_S)                     # POLL_S = 0.4 (hoặc giá trị chốt ở spike)
        def _stream():
            batch = run_safely(lambda: svc.qa.read_tokens(actor, aid, s[K.CHAT_LAST_ID]), on_error_toast=False)
            now = time.monotonic()
            if batch:
                for ev in batch.events:
                    if ev.type == "status": s[K.CHAT_PHASE] = ev.data
                    elif ev.type == "token": s[K.CHAT_BUF] += ev.data
                    elif ev.type == "reset": s[K.CHAT_BUF] = ""
                    elif ev.type == "done": s[K.CHAT_DONE] = ev.data
                if batch.events: s["chat.last_event_at"] = now
                s[K.CHAT_LAST_ID] = batch.last_id
            if not s.get(K.CHAT_DONE) and fallback_due(s, now):       # mỗi 2 s, hoặc im lặng > 5 s, hoặc read lỗi
                a = run_safely(lambda: svc.qa.get_answer(actor, aid), on_error_toast=False)
                if a and a.is_terminal: s[K.CHAT_DONE] = "db"
            if s.get(K.CHAT_DONE):
                s[K.CHAT_ACTIVE_ANSWER] = None
                st.rerun()                                            # rerun toàn app → render AnswerDTO (T-13-7)
            if not s[K.CHAT_BUF]:
                st.caption(t(f"chat.phase.{s.get(K.CHAT_PHASE, 'retrieving')}"))   # "Đang tìm trong tài liệu…" / "Đang soạn câu trả lời…"
            else:
                st.markdown(strip_markers_for_stream(s[K.CHAT_BUF]) + " ▌")
            if now - s[K.CHAT_STARTED_AT] > 120:
                st.warning(t("chat.slow"))                            # "Đang xử lý lâu hơn dự kiến"
            st.button(t("chat.stop"), key=f"stop:{aid}", icon="⏹",
                      on_click=lambda: run_safely(lambda: svc.qa.cancel(actor, aid)))
        _stream()
```

- `fallback_due`: `now - s.get("chat.last_db_check", 0) >= 2` hoặc `now - s.get("chat.last_event_at", start) > 5`; cập nhật `chat.last_db_check`.
- Chỉ `answer_id` đang hoạt động được stream; các câu trả lời cũ render tĩnh (T-10-5).
- Người dùng chuyển hội thoại khi đang stream: `chat_panel` không gọi `render_streaming` nữa (answer vẫn chạy và được lưu). Khi quay lại hội thoại đó, nếu answer cuối vẫn `PENDING` thì đặt lại `K.CHAT_ACTIVE_ANSWER` với `last_id="0-0"` để tiếp tục.
- Không đặt widget nào khác của trang vào trong fragment.

## Tiêu chí xong

- [ ] Câu trả lời hiện dần với con trỏ ▌; marker `[S#]` không bao giờ hiện.
- [ ] Bấm Dừng → trong ≤ 2 s chuyển sang trạng thái "Đã dừng" (T-13-7), phần đã nhận còn.
- [ ] Sự kiện `reset` xoá vùng đang stream nhưng giữ câu hỏi.
- [ ] Dừng Redis giữa stream → UI kết thúc ở trạng thái lỗi trong ≤ 7 s nhờ fallback DB.
- [ ] Sau khi xong, không còn request poll (kiểm bằng log/metric).

## Test

- `tests/unit/ui/test_streaming.py` (AppTest với `FakeQaService`: answered, reset, done qua DB, stop).
- `tests/e2e/test_stop_midstream.py` (Playwright + worker thật + FakeLLM chậm).
- E2E đo AC-13.2: từ submit tới khi chỉ báo hiện ≤ 300 ms.

## Tham chiếu

ADR-005 · SADD §5.3.4, §5.7.1 · Blueprint §3.7.2 · US-13
