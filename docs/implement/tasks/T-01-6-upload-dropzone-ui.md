# T-01-6 — UI vùng tải lên (UploadDropzone) và thông báo lỗi theo tệp

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01 (P0), US-03 (P0), US-24 (hiển thị giới hạn) |
| Sprint | S2 |
| Tầng | UI |
| Ước lượng | 1d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-01-4, F-03, F-04, F-11, PLT-07 |
| Chặn | T-01-7, T-02-2 |

## Bối cảnh

Màn hình SCR-02/SCR-03 cột Tài liệu. Quyết định **C-04** (`type=None` để tự báo lỗi bằng tiếng Việt) và **C-05** (không copy bytes).

## Phạm vi

**Làm:** `app/ui/components/upload_dropzone.py`: widget, xử lý một lần mỗi nonce, hiển thị kết quả từng tệp, caption giới hạn.

**Không làm:** dialog trùng tên (T-01-7), hiển thị lô nhiều tệp đầy đủ (T-02-2 mở rộng).

## Đặc tả

```python
def render_upload_dropzone(svc: Services, actor: Actor) -> None:
    limits = svc.config.limits()
    nonce = st.session_state.setdefault(K.DOCS_UPLOAD_NONCE, 0)
    files = st.file_uploader(t("upload.label"), accept_multiple_files=True, type=None,
                             key=f"upl:{nonce}", help=t("upload.help"))
    st.caption(t("upload.limits", mb=limits.max_upload_mb, pages=limits.max_pages,
                 files=limits.max_files_per_upload))    # "Chỉ PDF · tối đa 25 MB / tệp · 400 trang · 5 tệp mỗi lần"
    if files and st.session_state.get(K.DOCS_PROCESSED_NONCE) != nonce:
        inputs = [UploadInput(f.name, f.size, f) for f in files]
        results = run_safely(lambda: svc.documents.upload(actor, inputs, idempotency_key=f"{actor.session_id}:{nonce}"))
        st.session_state[K.DOCS_PROCESSED_NONCE] = nonce
        handle_results(results)          # REJECTED → thêm vào K.DOCS_UPLOAD_ERRORS; DUPLICATE → st.toast; NAME_CONFLICT → T-01-7
        if no NAME_CONFLICT pending:
            st.session_state[K.DOCS_UPLOAD_NONCE] = nonce + 1   # xoá widget cho lần sau
            st.rerun()
    render_upload_errors()               # danh sách st.error, mỗi lỗi có nút ✕ (key=f"uplerr:{i}:{hash}")
```

- Thông báo lỗi dùng `error_text(code, file_name=..., **params)` (bảng chuỗi T-03-1); thông điệp **phải** chứa tên tệp + giới hạn + thực tế (AC-01.2).
- `DUPLICATE`: `st.toast(t("upload.duplicate", file_name=...))` = "Tệp {file_name} đã có trong danh sách".
- `ACCEPTED`: `st.toast(t("upload.accepted", n=...))`; danh sách tài liệu (T-05-3) tự hiện tài liệu mới với chip "Đang xử lý".
- Khi có `NAME_CONFLICT` thì **không** tăng nonce cho tới khi người dùng chọn xong trong SCR-07 (giữ `UploadedFile`).
- Tệp > `server.maxUploadSize` (30 MB) bị Streamlit chặn với thông điệp riêng — chấp nhận (C-04).

## Tiêu chí xong

- [ ] Tải một PDF hợp lệ: toast + tài liệu xuất hiện với "Đang xử lý" (AC-01.1).
- [ ] Tải `.docx`: dòng lỗi "<tên tệp>: chỉ hỗ trợ PDF" và tài liệu không vào danh sách (AC-03.1).
- [ ] Đổi `MAX_UPLOAD_MB` trong `app_config` → caption đổi sau ≤ 30 s (US-24).
- [ ] Rerun trang sau khi upload không gửi lại tệp.

## Test

`tests/unit/ui/test_upload_dropzone.py` (AppTest, service giả trả đủ 4 loại outcome).

## Tham chiếu

Blueprint §3.6.1, SCR-02/03 · Implement_plan §14 C-04, C-05 · US-01, US-03, US-24
