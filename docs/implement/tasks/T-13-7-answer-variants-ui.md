# T-13-7 — Các biến thể AnswerMessage: Đã dừng, Chưa hoàn tất, Lỗi AI, Thử lại

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13 (P0) |
| Sprint | S3 |
| Tầng | UI |
| Ước lượng | 1d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-10-5, T-11-4, T-13-6 |
| Chặn | — |

## Bối cảnh

Blueprint §3.5.3 (AnswerMessage — biến thể) và §3.7.2; sheet component [11-component-states.html](../../design/html_design/11-component-states.html). Quyết định **C-17**: "Thử lại"/"Tạo lại" = hỏi lại cùng câu trong cùng hội thoại.

## Phạm vi

**Làm:** mở rộng `render_answer` cho mọi outcome/state.

## Đặc tả

| outcome / message_state | Hiển thị | Chip | FeedbackBar | Hành động |
|---|---|---|---|---|
| ANSWERED / COMPLETE | T-10-5 | Có | Có | — |
| NOT_FOUND / COMPLETE | T-11-4 | Không | Có | — |
| ABORTED / INTERRUPTED | Phần đã nhận + nhãn `t("answer.stopped")` "Đã dừng" (`st.caption`) | Chỉ citation hợp lệ của phần đã nhận | Không | — |
| ERROR / INTERRUPTED, có segment | Phần đã nhận + nhãn "Chưa hoàn tất" | Như trên | Không | Nút **Tạo lại** |
| ERROR, không segment | Thẻ lỗi nhẹ: `error_text` theo `error_code` (`LLM_TIMEOUT` → "Câu trả lời mất quá nhiều thời gian", `LLM_UNAVAILABLE` → "Dịch vụ AI tạm thời không khả dụng, vui lòng thử lại", khác → "Hệ thống tạm thời không trả lời được, vui lòng thử lại") | Không | Không | Nút **Thử lại** |
| PENDING (tải lại trang) | Giao cho `render_streaming` (T-13-6) | — | — | — |

Thử lại / Tạo lại:

```python
if st.button(t("common.retry"), key=f"retry_answer:{a.id}"):
    handle = run_safely(lambda: svc.qa.ask(actor, AskCommand(conversation_id=a.conversation_id,
                                    question=a.question, scope_doc_ids=selected_scope_ids(),
                                    idempotency_key=f"retry:{a.id}")))
    if handle: start_streaming(handle); st.rerun()
```

- Chỉ hiện nút khi `a.is_terminal` (watchdog: không cho thử lại khi job còn active).
- `idempotency_key=f"retry:{a.id}"` chống tạo nhiều answer khi bấm nhanh hai lần.
- Dùng `st.container(border=True)` cho thẻ lỗi, **không** `st.error` toàn khối (tránh cảm giác hệ thống hỏng nặng); có icon ⚠.

## Tiêu chí xong

- [ ] Mỗi dòng của bảng có AppTest riêng.
- [ ] Thử lại tạo cặp message mới trong cùng hội thoại và bắt đầu stream.

## Test

`tests/unit/ui/test_answer_variants.py`.

## Tham chiếu

Blueprint §3.5.3, §3.7.2, PRD 4.2 (Lỗi AI, mất mạng) · Implement_plan §14 C-17
