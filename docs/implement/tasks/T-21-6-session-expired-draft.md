# T-21-6 — Màn hình hết phiên (SCR-10) và giữ nháp câu hỏi

| Thuộc tính | Giá trị |
|---|---|
| Story | US-21 (P0) — AC-21.2 |
| Sprint | S1 (phần giữ nháp hoàn thiện ở S3 khi đã có Composer) |
| Tầng | UI / INF |
| Ước lượng | 0.75d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | T-21-4; T-07-4 (Composer) cho phần khôi phục |
| Chặn | — |

## Bối cảnh

AC-21.2: hết phiên thì chuyển về đăng nhập và **giữ nội dung đang nhập nếu có thể**. Theo **C-07**: sau `st.login()` là session mới, `session_state` mất, nên nháp được lưu vào Redis.

## Phạm vi

**Làm:**
- `render_session_expired()` (SCR-10).
- `DraftStore` (Redis): `save(sub, text)`, `pop(sub)`.
- Trong Composer (T-07-4): nếu hết phiên đúng lúc người dùng submit thì lưu câu hỏi vào `DraftStore` trước khi hiện SCR-10.
- Sau khi đăng nhập lại: banner khôi phục nháp.

## Đặc tả

Khoá Redis `draft:{hash_id(sub)}`, giá trị là câu hỏi (≤ `MAX_QUESTION_CHARS`), TTL 24 h. Nội dung nháp **không** được log.

Luồng:

```text
Composer submit(question):
  if session_expired(actor):                  # T-21-4 trả True
      draft_store.save(claims.sub, question)
      render_session_expired(); st.stop()

render_session_expired():                      # theo 10-session-expired.html
  st.warning(t("session.expired"))             # "Phiên đăng nhập đã hết hạn"
  st.caption(t("session.draft_saved")) nếu vừa lưu nháp   # "Câu hỏi bạn đang soạn đã được giữ lại"
  st.button(t("session.relogin"), on_click=lambda: (st.logout(),))   # sau logout guard hiện SCR-01

Sau đăng nhập lại, ở chat_panel (lần đầu mỗi session):
  draft = draft_store.pop(claims.sub)
  if draft: st.session_state[K.AUTH_DRAFT_BANNER] = draft
  if banner: st.info("Câu hỏi chưa gửi: «{draft cắt 120 ký tự}»") + [Gửi lại] (gọi ask với draft) + [Bỏ]
```

Giới hạn: `st.chat_input` không prefill được (C-06), nên dùng banner "Gửi lại" thay cho điền lại vào ô nhập.

## Tiêu chí xong

- [ ] Hết phiên khi gửi câu hỏi: thấy SCR-10; đăng nhập lại thấy banner với đúng câu hỏi; bấm "Gửi lại" thì câu hỏi được gửi.
- [ ] Bấm "Bỏ" thì nháp biến mất và không xuất hiện lại.
- [ ] Nháp không còn trong Redis sau khi đã khôi phục (pop).

## Test

`tests/unit/ui/test_session_expired.py` (AppTest với SessionTracker giả); `tests/integration/test_draft_store.py` (TTL, pop).

## Tham chiếu

US-21 AC-21.2 · Blueprint SCR-10, §3.4 · Implement_plan §14 C-06, C-07
