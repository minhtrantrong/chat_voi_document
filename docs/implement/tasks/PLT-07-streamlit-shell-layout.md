# PLT-07 — Khung Streamlit: điều hướng, bố cục 3 cột, TopBar, cấu hình production

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S0, mục 0.8; quyết định C-01) |
| Sprint | S0 |
| Tầng | UI |
| Ước lượng | 1.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | PLT-01, F-03 (có thể làm song song, dùng chuỗi tạm) |
| Chặn | T-21-2, T-05-3, T-07-4, T-13d-3, T-16-1 |

## Bối cảnh

Theo **C-01**, ứng dụng có **một màn hình chính 3 cột** (Tài liệu / Hội thoại / Nguồn) như thiết kế HTML, cộng thêm trang `/admin`. Task này dựng khung để các story khác chỉ việc điền component vào đúng chỗ.

## Phạm vi

**Làm:**
- `app/main.py`: `set_page_config`, chỗ đặt AuthGuard (T-21-2 điền logic), `st.navigation`.
- `app/ui/pages/main.py`: TopBar + 3 cột với component giữ chỗ.
- `app/ui/pages/admin.py`: trang trống "Quản trị".
- `.streamlit/config.toml` cho production.
- `app/ui/theme.py`: CSS tĩnh tối thiểu.

**Không làm:** logic đăng nhập, danh sách tài liệu, chat (các task story).

## Đặc tả

```python
# app/main.py
st.set_page_config(page_title="Chat với tài liệu", page_icon="📄", layout="wide",
                   initial_sidebar_state="collapsed")
apply_theme()                                  # app/ui/theme.py
actor = auth_guard()                           # T-21-2; tạm thời trả Actor giả khi APP_ENV=local
pages = [st.Page("app/ui/pages/main.py", title=t("nav.main"), default=True)]
if actor.role in (Role.ADMIN, Role.PM):
    pages.append(st.Page("app/ui/pages/admin.py", title=t("nav.admin"), url_path="admin"))
st.navigation(pages, position="hidden").run()
```

```python
# app/ui/pages/main.py
render_top_bar()                                  # logo · "＋ Hội thoại mới" (T-16-1) · menu người dùng (T-21-7)
col_docs, col_chat, col_source = st.columns([0.22, 0.48, 0.30], gap="medium")
with col_docs:   render_document_panel()          # placeholder: st.caption("Tài liệu")
with col_chat:   render_chat_panel()              # placeholder
with col_source: render_source_panel()            # placeholder
```

- Mỗi `render_*` nằm ở `app/ui/components/<tên>.py`, lúc này chỉ có tiêu đề cột.
- `top_bar`: `st.columns([0.6, 0.2, 0.2])`; menu người dùng dùng `st.popover(display_name)`; link Admin chỉ hiện với ADMIN/PM (`st.page_link`).
- Ở màn hình < 768 px Streamlit tự xếp chồng các cột; chấp nhận cho MVP (Blueprint §3.5.1 cho phép "hỗ trợ mức cơ bản").

**`.streamlit/config.toml`** (theo SADD §5.6.4, kèm C-04):

```toml
[server]
headless = true
enableCORS = true
enableXsrfProtection = true
maxUploadSize = 30            # MAX_UPLOAD_MB + 5 (C-04)
maxMessageSize = 200
enableWebsocketCompression = true
[browser]
gatherUsageStats = false
[client]
showErrorDetails = "none"
toolbarMode = "minimal"
[theme]
base = "light"
primaryColor = "#2563EB"
font = "sans serif"
```

**`app/ui/theme.py`:** một hằng chuỗi CSS **tĩnh** (độ rộng tối đa của cột, khoảng cách theo thang 4 px, kiểu chip trạng thái). Đây là **nơi duy nhất** được gọi `st.markdown(CSS, unsafe_allow_html=True)`, và tuyệt đối không chèn dữ liệu động vào chuỗi này. Thêm test kiểm tra không file nào khác dùng `unsafe_allow_html`.

## Tiêu chí xong

- [ ] Ở 1440 × 900, trang chính hiển thị 3 cột với tỷ lệ gần đúng thiết kế [05-main-conversation.html](../../design/html_design/05-main-conversation.html).
- [ ] Trang `/admin` không xuất hiện trong điều hướng với END_USER (tạm kiểm bằng Actor giả).
- [ ] Lỗi Python trong page không hiển thị stack trace cho người dùng (`showErrorDetails = "none"`).
- [ ] Test `tests/unit/ui/test_no_unsafe_html.py` (quét mã nguồn) xanh.

## Test

- AppTest `tests/unit/ui/test_shell.py`: trang chính chạy không exception, có 3 tiêu đề cột.
- `test_no_unsafe_html.py`: grep `unsafe_allow_html=True` chỉ được xuất hiện trong `app/ui/theme.py`.

## Tham chiếu

Blueprint §3.1, §3.5.1 · SADD §5.6.4, §5.7.1 · Implement_plan §14 C-01, C-04
