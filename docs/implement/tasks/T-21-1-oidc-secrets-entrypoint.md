# T-21-1 — Sinh `secrets.toml` OIDC lúc khởi động container

| Thuộc tính | Giá trị |
|---|---|
| Story | US-21 — Chỉ người được cấp quyền mới truy cập (P0) |
| Sprint | S1 |
| Tầng | OPS |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | PLT-04, PLT-05, gate G-02 (client ID/secret của IdP) |
| Chặn | T-21-2 |

## Bối cảnh

`st.login()` đọc cấu hình OIDC từ `.streamlit/secrets.toml` mục `[auth]` (SADD §5.6.4). File này chứa secret nên **không** được commit và không được bake vào image; phải sinh từ env/secret manager khi container khởi động.

## Phạm vi

**Làm:** thêm bước sinh file vào `deploy/entrypoint.sh` (chỉ với lệnh `web`); cấu hình local cho dev dùng IdP thử nghiệm (Keycloak container, profile `dev`).

**Không làm:** logic đăng nhập trong app (T-21-2).

## Đặc tả

Trong `entrypoint.sh`, trước khi chạy `streamlit`:

```sh
umask 077
mkdir -p /app/.streamlit
python -m app.ops render-secrets > /app/.streamlit/secrets.toml
```

`python -m app.ops render-secrets` (thêm subcommand vào `app/ops.py`) đọc `Settings` và in:

```toml
[auth]
redirect_uri = "<OIDC_REDIRECT_URI>"
cookie_secret = "<STREAMLIT_COOKIE_SECRET>"
client_id = "<OIDC_CLIENT_ID>"
client_secret = "<OIDC_CLIENT_SECRET>"
server_metadata_url = "<OIDC_ISSUER>/.well-known/openid-configuration"
client_kwargs = { scope = "openid email profile groups", prompt = "select_account" }
```

- Escape chuỗi TOML đúng chuẩn (dùng thư viện `tomli_w`, không tự nối chuỗi).
- Cookie secret của **session Streamlit** (`server.cookieSecret`) truyền qua env `STREAMLIT_SERVER_COOKIE_SECRET`, khác với `auth.cookie_secret` (SADD: hai secret độc lập). Thêm biến `STREAMLIT_AUTH_COOKIE_SECRET` vào PLT-05 nếu cần tách.
- Nếu IdP không trả `groups` trong ID token: ghi chú cho IT cấu hình mapper (Keycloak "Group Membership", Entra ID "groups claim").

Dev local: profile `dev` trong compose thêm `keycloak` với realm import `deploy/dev/keycloak-realm.json` có 3 user mẫu: `user1` (nhóm `cvd-users`), `pm1` (`cvd-pms`), `admin1` (`cvd-admins`), và `nogroup1` (không nhóm).

## Tiêu chí xong

- [ ] Container `web` khởi động thì có `/app/.streamlit/secrets.toml` với quyền `600`, không xuất hiện trong `docker image history`.
- [ ] Thiếu biến OIDC thì container thoát với thông báo nêu tên biến.
- [ ] Local với Keycloak: đăng nhập được bằng 4 user mẫu (phân quyền xử lý ở T-21-3).

## Test

`tests/unit/test_render_secrets.py`: TOML hợp lệ (parse lại bằng `tomllib`), giá trị có ký tự `"` và `\` được escape đúng.

## Tham chiếu

SADD §5.6.4, §5.8.2, ADR-006 · US-21
