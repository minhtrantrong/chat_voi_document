# T-21-5 — Màn hình 403 "Không có quyền" (SCR-08)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-21 (P0) — AC-21.1 |
| Sprint | S1 |
| Tầng | UI |
| Ước lượng | 0.25d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | T-21-2, T-21-3, F-03, F-04 (`ACCESS_REQUEST_CONTACT`) |
| Chặn | — |

## Bối cảnh

Người đăng nhập được ở IdP nhưng chưa được cấp quyền ứng dụng (không thuộc nhóm `cvd-*`) phải thấy hướng dẫn xin quyền, **không** lộ sự tồn tại của tài liệu (Blueprint SCR-08).

## Phạm vi

**Làm:** `render_forbidden()` trong `app/ui/pages/forbidden.py`; được `auth_guard` gọi khi `resolve_actor` ném `Forbidden`.

## Đặc tả

Theo [08-forbidden-403.html](../../design/html_design/08-forbidden-403.html):
- Biểu tượng 🔒, tiêu đề `t("forbidden.title")` = "Bạn chưa được cấp quyền sử dụng công cụ này".
- Đoạn mô tả: "Tài khoản {email} đã đăng nhập nhưng chưa nằm trong nhóm được phép. Hãy liên hệ {contact} để được cấp quyền."
- Nút "Đăng xuất" (`st.logout`) và nút phụ "Thử lại" (`st.rerun`, để sau khi được thêm nhóm và đăng nhập lại).
- Không render TopBar, không có link Admin, không gọi service tài liệu.

Lưu ý: trường hợp người dùng **có** quyền ứng dụng nhưng truy cập một tài liệu không thuộc quyền thì **không** dùng màn hình này, mà dùng `NotFound` + toast "Tài liệu không tồn tại hoặc đã bị xoá" (ERR-DOC-404), để không lộ việc tài liệu tồn tại.

## Tiêu chí xong

- [ ] User `nogroup1` (Keycloak dev) thấy đúng SCR-08 sau khi đăng nhập.
- [ ] Không có request nào tới `DocumentService` trong phiên đó (kiểm bằng service giả trong AppTest).

## Test

`tests/unit/ui/test_forbidden.py` (AppTest, `IdentityService` giả ném `Forbidden`).

## Tham chiếu

Blueprint SCR-08, §3.7.3 · SADD §5.7.5 · US-21
