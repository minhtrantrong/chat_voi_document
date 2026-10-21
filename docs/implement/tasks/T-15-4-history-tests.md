# T-15-4 — Test lịch sử qua phiên mới và cách ly người dùng

| Thuộc tính | Giá trị |
|---|---|
| Story | US-15 (P1) — AC-15.1 |
| Sprint | S4 |
| Tầng | TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | T-15-1, T-15-2 |
| Chặn | — |

## Bối cảnh

AC-15.1 có hai vế: còn thấy sau khi đăng nhập lại; không thấy hội thoại của người khác.

## Phạm vi

**Làm:** test service + AppTest + một E2E.

## Đặc tả

| Test | Khẳng định |
|---|---|
| `test_history_survives_new_session` | Tạo hội thoại với session A1; tạo Actor mới cùng user (session A2) → `list` có hội thoại |
| `test_cannot_list_others_conversations` | User B `list` không chứa hội thoại của A |
| `test_cannot_read_others_conversation` | B `get(conv_a)` → `NotFound`; ADMIN `get(conv_a)` → `NotFound` |
| `test_retention_hides_old` | Hội thoại cũ hơn 180 ngày bị sweep → không còn trong `list` |
| E2E `test_history_after_relogin` | Hỏi 1 câu → đăng xuất → đăng nhập → mở Lịch sử → mở hội thoại → thấy câu trả lời và chip |

## Tiêu chí xong

- [ ] 5 test xanh.

## Tham chiếu

US-15 AC-15.1 · SADD §5.8.3
