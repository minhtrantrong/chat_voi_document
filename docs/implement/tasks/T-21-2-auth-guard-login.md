# T-21-2 — AuthGuard "fail closed" và màn hình đăng nhập SCR-01

| Thuộc tính | Giá trị |
|---|---|
| Story | US-21 (P0) — AC-21.1 |
| Sprint | S1 |
| Tầng | UI |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | T-21-1, PLT-07, F-03, F-11 |
| Chặn | T-21-3…T-21-7, mọi UI task cần Actor |

## Bối cảnh

SADD §5.8.2: `app/main.py` kiểm tra `st.user.is_logged_in` **trước khi render bất kỳ page nào**; chưa đăng nhập thì `st.login()` và `st.stop()`. Không có page ẩn nào dựa vào việc "không hiển thị link".

## Phạm vi

**Làm:** hàm `auth_guard()` trong `app/ui/auth.py`, màn hình SCR-01 `app/ui/pages/login.py` (render bởi guard, không phải page điều hướng).

**Không làm:** ánh xạ role (T-21-3), hết phiên (T-21-4), 403 (T-21-5).

## Đặc tả

```python
# app/ui/auth.py
def auth_guard() -> Actor:
    if not st.user.is_logged_in:
        render_login()                      # SCR-01
        st.stop()
    actor = run_safely(get_actor)           # T-21-3: resolve_actor; Forbidden → render_forbidden(); st.stop()
    check_session_timeout(actor)            # T-21-4
    return actor
```

SCR-01 (theo [01-login.html](../../design/html_design/01-login.html)):
- Tiêu đề "Chat với tài liệu", mô tả một dòng (`t("login.subtitle")`).
- Nút chính `t("login.button")` = "Đăng nhập bằng tài khoản công ty", `on_click=st.login` (không truyền tham số provider khi chỉ có một `[auth]`).
- Dòng nhỏ: "Bạn cần được cấp quyền để sử dụng. Liên hệ {ACCESS_REQUEST_CONTACT}".
- Không hiển thị thông tin nào về tài liệu, số người dùng…

`auth_guard()` được gọi **dòng đầu tiên** trong `app/main.py` sau `set_page_config`/`apply_theme` (PLT-07 đã chừa chỗ). Ở `APP_ENV=local` **không** có đường tắt bỏ qua đăng nhập; dev dùng Keycloak (T-21-1).

## Tiêu chí xong

- [ ] Truy cập `/` hoặc `/admin` khi chưa đăng nhập: chỉ thấy SCR-01, không component nào khác được render.
- [ ] Bấm nút chuyển sang IdP; đăng nhập xong quay lại trang chính.
- [ ] Code review xác nhận không có `st.Page` nào được `run()` trước `auth_guard()`.

## Test

`tests/unit/ui/test_auth_guard.py` (AppTest, patch `st.user`):
- `is_logged_in=False`: chỉ có nút đăng nhập; không gọi bất kỳ service nào (service giả đếm 0 lần gọi).
- `is_logged_in=True`: guard trả `Actor` và trang chính render.

## Tham chiếu

SADD §5.8.2 · US-21 AC-21.1 · Blueprint §3.7.3
