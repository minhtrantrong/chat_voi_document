# F-03 — Từ điển chuỗi giao diện (i18n) và ánh xạ mã lỗi

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng dùng chung (Implement_plan §15) |
| Sprint | S0 |
| Tầng | UI |
| Ước lượng | 1d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | F-02 |
| Chặn | Mọi UI task; T-03-1; T-13b-2 |

## Bối cảnh

US-13b: chuỗi tách khỏi mã, sẵn sàng i18n, chịu giãn chữ +30%. Mọi component lấy chuỗi qua `t()`.

## Phạm vi

**Làm:** `app/ui/i18n/__init__.py` (hàm `t`, `error_text`), `vi.py` (đầy đủ), `en.py` (dự phòng, có thể chưa đủ), bộ khoá ban đầu.

**Không làm:** chọn ngôn ngữ theo người dùng (MVP chỉ tiếng Việt, OQ-006).

## Đặc tả

```python
# app/ui/i18n/__init__.py
def t(key: str, /, **params: object) -> str:
    """Tra vi → en → trả chính key (và log warn 'missing_i18n_key' một lần)."""
def error_text(err: AppError | DocErrorCode, **extra: object) -> str:
    """ErrorCode → t(f"error.{code}"), DocErrorCode → t(f"doc.error.{code}")."""
```

- Dùng `str.format_map` với `params`; thiếu tham số thì giữ nguyên `{tên}` và log warn, **không** ném lỗi.
- Khoá dạng `nhóm.mục` (ví dụ `upload.label`, `chat.stop`, `doc.error.PDF_NO_TEXT`).

Bộ khoá tối thiểu phải có từ S0 (các task story bổ sung thêm):

| Nhóm | Khoá ví dụ |
|---|---|
| `nav.*` | `nav.main` = "Trang chính", `nav.admin` = "Quản trị" |
| `topbar.*` | `topbar.new_conversation` = "＋ Hội thoại mới", `topbar.logout` = "Đăng xuất" |
| `error.*` | mỗi `ErrorCode`, ví dụ `error.ERR-RATE-LIMIT` = "Bạn đã gửi quá nhiều câu hỏi, hãy thử lại sau {retry_after} giây"; `error.ERR-INTERNAL` = "Đã xảy ra lỗi, mã tra cứu {corr_id}" |
| `doc.error.*` | theo bảng chuỗi của T-03-1 |
| `common.*` | `common.cancel` = "Huỷ", `common.close` = "Đóng", `common.retry` = "Thử lại" |

Lấy nguyên văn chuỗi trong SADD §5.7.5, §10.4 và AC của User Stories; chỗ nào khác nhau thì **AC thắng**.

## Tiêu chí xong

- [ ] Mọi `ErrorCode` và `DocErrorCode` có chuỗi trong `vi.py` (test kiểm tra).
- [ ] `t("khoa.khong.ton.tai")` trả về chính khoá và không ném lỗi.

## Test

`tests/unit/ui/test_i18n.py`: đủ khoá cho mọi mã lỗi; format tham số; thiếu tham số không ném lỗi; fallback `en`.

## Tham chiếu

US-13b · Blueprint §3.8 (i18n) · SADD §5.7.5, §10.4
