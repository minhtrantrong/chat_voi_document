# T-07-4 — Composer: ô nhập câu hỏi, trạng thái bật/tắt, DisclaimerBar

| Thuộc tính | Giá trị |
|---|---|
| Story | US-07 (P0) — AC-07.2; US-08 (disclaimer); US-24 (giới hạn ký tự) |
| Sprint | S3 (có thể làm cuối S2 trên `FakeQaService`) |
| Tầng | UI |
| Ước lượng | 1d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-07-1, T-04-7 (`docs.has_ready`), F-03, F-11 |
| Chặn | T-07-5, T-21-6 (phần khôi phục nháp) |

## Bối cảnh

Blueprint §3.5.3 (Composer) và §3.7.4. Quyết định **C-06**: dùng `st.chat_input`; Enter gửi, Shift+Enter xuống dòng (có sẵn); khi đang trả lời thì `disabled`, nút Dừng nằm trong fragment stream.

## Phạm vi

**Làm:** `app/ui/components/composer.py`, EmptyState cho SCR-02/SCR-04 ở cột Hội thoại, `DisclaimerBar`.

## Đặc tả

```python
def render_composer(svc: Services, actor: Actor) -> str | None:
    limits = svc.config.limits()
    has_ready = st.session_state.get(K.DOCS_HAS_READY, False)
    busy = st.session_state.get(K.CHAT_ACTIVE_ANSWER) is not None
    placeholder = t("composer.placeholder") if has_ready else t("composer.no_docs")   # "Tải PDF để bắt đầu"
    q = st.chat_input(placeholder, max_chars=limits.max_question_chars,
                      disabled=(not has_ready) or busy, key="chat.input")
    st.caption(t("composer.disclaimer"))      # "AI có thể sai. Hãy kiểm tra lại với tài liệu gốc trước khi sử dụng."
    st.caption(t("composer.limit", n=limits.max_question_chars))   # "Tối đa 2000 ký tự"
    return q
```

EmptyState ở cột Hội thoại khi chưa có tin nhắn:

| Điều kiện (Blueprint §3.7.4) | Nội dung |
|---|---|
| 0 tài liệu | SCR-02: "Tải PDF đầu tiên để bắt đầu hỏi" + mũi tên chỉ sang cột Tài liệu |
| 0 READY, ≥ 1 PROCESSING | SCR-04: "Đang xử lý n tài liệu, thường mất vài phút" |
| ≥ 1 READY | SCR-03: "Hỏi bất cứ điều gì về tài liệu của bạn" + (P2) gợi ý câu hỏi |

- `st.chat_input` tự chặn nhập quá `max_chars`; gửi chuỗi toàn khoảng trắng thì Streamlit vẫn trả về chuỗi → service ném `ERR_Q_EMPTY` → UI bỏ qua im lặng (không hiện lỗi cho chuỗi rỗng).
- Vị trí: `st.chat_input` trong cột giữa (không phải đáy trang) — đặt trong `with col_chat:` (Streamlit ≥ 1.42 hỗ trợ chat_input trong container).

## Tiêu chí xong

- [ ] 0 tài liệu READY: ô nhập vô hiệu với placeholder "Tải PDF để bắt đầu" (AC-07.2).
- [ ] Có tài liệu READY: ô nhập bật; Enter gửi; Shift+Enter xuống dòng.
- [ ] Đang trả lời: ô nhập vô hiệu.
- [ ] Disclaimer luôn hiển thị dưới ô nhập.

## Test

`tests/unit/ui/test_composer.py` (AppTest: 3 trạng thái tài liệu × busy).

## Tham chiếu

US-07 · Blueprint §3.5.3, §3.7.4, SCR-02/03/04 · Implement_plan §14 C-06
