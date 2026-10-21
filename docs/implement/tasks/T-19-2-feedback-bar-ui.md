# T-19-2 — FeedbackBar 👍/👎 và ô lý do

| Thuộc tính | Giá trị |
|---|---|
| Story | US-19 (P0) — AC-19.1, AC-19.3 |
| Sprint | S4 |
| Tầng | UI |
| Ước lượng | 1d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-19-1, T-10-5, F-04 (cờ `feedback`) |
| Chặn | T-19-3 |

## Bối cảnh

Thiết kế SCR-05: thanh 👍/👎 dưới mỗi câu trả lời hoàn tất (ẩn khi đang stream, lỗi, chưa hoàn tất); bấm 👎 mở ô lý do tuỳ chọn; người dùng thấy xác nhận.

## Phạm vi

**Làm:** `app/ui/components/feedback_bar.py::feedback_bar(svc, actor, answer)`.

## Đặc tả

```python
def feedback_bar(svc, actor, a: AnswerDTO) -> None:
    if a.outcome not in ("ANSWERED", "NOT_FOUND"): return
    state_key = f"fb.value:{a.id}"
    current = st.session_state.get(state_key, a.my_feedback)
    c1, c2, _ = st.columns([0.18, 0.22, 0.6])
    if c1.button(t("fb.helpful"), key=f"fb:{a.id}:up", icon="👍",
                 type="primary" if current == "HELPFUL" else "secondary"):
        submit(svc, actor, a.id, "HELPFUL"); st.toast(t("fb.thanks"))
    if c2.button(t("fb.not_helpful"), key=f"fb:{a.id}:down", icon="👎",
                 type="primary" if current == "NOT_HELPFUL" else "secondary"):
        submit(svc, actor, a.id, "NOT_HELPFUL"); st.session_state[f"fb.reason_open:{a.id}"] = True
    if st.session_state.get(f"fb.reason_open:{a.id}"):
        with st.form(key=f"fb.form:{a.id}", clear_on_submit=True, border=False):
            reason = st.text_input(t("fb.reason"), max_chars=500, key=f"fb.reason:{a.id}")   # "Lý do (không bắt buộc)"
            s1, s2 = st.columns(2)
            if s1.form_submit_button(t("common.send")): submit(svc, actor, a.id, "NOT_HELPFUL", reason); close_reason(a.id); st.toast(t("fb.thanks"))
            if s2.form_submit_button(t("fb.skip")): close_reason(a.id); st.toast(t("fb.thanks"))
```

- `submit` cập nhật `st.session_state[state_key]` **trước** (lạc quan) rồi gọi service với retry (T-19-3).
- Nhãn: "Hữu ích", "Không hữu ích"; toast "Cảm ơn phản hồi của bạn".
- Cờ `FEATURE_FEEDBACK=false` → không render.

## Tiêu chí xong

- [ ] Câu trả lời hoàn tất có 👍/👎; đang stream/lỗi/dừng không có.
- [ ] Bấm 👍 → nút được tô đậm + toast (AC-19.1).
- [ ] Bấm 👎 → ô lý do xuất hiện; bỏ qua vẫn lưu đánh giá (AC-19.3).

## Test

`tests/unit/ui/test_feedback_bar.py` (AppTest).

## Tham chiếu

US-19 · Blueprint §3.6.3, SCR-05
