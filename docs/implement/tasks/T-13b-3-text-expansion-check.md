# T-13b-3 — Kiểm tra giãn chữ +30%

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13b (P0) — "chịu giãn chữ +30%" |
| Sprint | S3 |
| Tầng | UI / TEST |
| Ước lượng | 0.25d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | F-03, T-13b-2 |
| Chặn | PLT-13 |

## Bối cảnh

Giao diện phải không vỡ khi bản dịch dài hơn 30%. Streamlit tự xuống dòng phần lớn chữ; rủi ro nằm ở CSS tĩnh (PLT-07) và nhãn nút/chip.

## Phạm vi

**Làm:** chế độ giả lập `UI_LOCALE=vi_long` sinh từ `vi.py` (mỗi chuỗi thêm ~30% ký tự `·`), chụp ảnh các màn hình chính.

## Đặc tả

- `app/ui/i18n/__init__.py`: nếu env `UI_LOCALE=vi_long` thì `t()` trả `s + " " + "·" * ceil(len(s) * 0.3)`. Chỉ bật ở local/test.
- Không dùng chiều rộng cố định px cho nhãn/nút trong `theme.py`; nếu cần, dùng `max-width` + `white-space: normal`.
- Playwright chụp SCR-02, 03, 04, 05, 06, 07, 09 ở 1440 × 900 và 1024 × 768 với `vi_long`; đính kèm ảnh vào PR.

## Tiêu chí xong

- [ ] Không chữ nào bị cắt mất (overflow hidden) hoặc nút tràn khỏi cột trong ảnh chụp.

## Test

`tests/e2e/test_text_expansion.py` (chụp ảnh, kiểm tra không có phần tử có `scrollWidth > clientWidth` trong các nút/chip).

## Tham chiếu

US-13b · Blueprint §3.8 · PLT-13
