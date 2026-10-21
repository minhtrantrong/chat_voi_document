# T-21-7 — Menu người dùng ở TopBar và đăng xuất

| Thuộc tính | Giá trị |
|---|---|
| Story | US-21 (P0) |
| Sprint | S1 |
| Tầng | UI |
| Ước lượng | 0.25d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | PLT-07, T-21-3 |
| Chặn | — |

## Bối cảnh

SADD §5.8.2: đăng xuất xoá cookie + `st.logout()`. Blueprint TopBar: menu người dùng ở góc phải.

## Phạm vi

**Làm:** component `user_menu(actor, display_name)` trong `app/ui/components/top_bar.py`.

## Đặc tả

- `st.popover(display_name, icon="👤")` chứa:
  - Dòng `display_name` và nhãn role (`t(f"role.{actor.role}")`: "Người dùng" / "Quản lý dự án" / "Quản trị viên").
  - `st.page_link` tới `/admin` nếu role là ADMIN hoặc PM.
  - Nút "Đăng xuất": xoá toàn bộ `st.session_state` (`for k in list(st.session_state): del st.session_state[k]`) rồi gọi `st.logout()`.
- `display_name` lấy từ bản ghi `users` (đã có trong Actor DTO hoặc service), không đọc trực tiếp claim trong component.

## Tiêu chí xong

- [ ] Đăng xuất xong, bấm Back trên trình duyệt không xem lại được dữ liệu (guard hiện SCR-01).
- [ ] END_USER không thấy link Quản trị.

## Test

`tests/unit/ui/test_user_menu.py` (AppTest với 3 role).

## Tham chiếu

SADD §5.8.2 · Blueprint §3.1 (TopBar)
