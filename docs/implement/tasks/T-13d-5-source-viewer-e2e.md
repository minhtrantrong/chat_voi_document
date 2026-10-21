# T-13d-5 — E2E khung Nguồn và chip tài liệu đã xoá

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13d (P1) — AC-13d.1, AC-13d.2; US-23 |
| Sprint | S4 |
| Tầng | TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | T-13d-3, T-06-5 |
| Chặn | — |

## Bối cảnh

Chứng minh AC trên trình duyệt thật.

## Phạm vi

**Làm:** `tests/e2e/test_source_viewer.py` (Playwright, OIDC mock/Keycloak dev, worker thật, FakeLLM `echo_sources`).

## Đặc tả

| Kịch bản | Bước | Khẳng định |
|---|---|---|
| Mở đúng trang | Upload `text.pdf` → hỏi về hạn chót → bấm chip | Khung Nguồn hiện "tr. 2 / 3"; ảnh có vùng vàng (kiểm tra pixel trên screenshot phần tử `img`) |
| Điều hướng | Bấm ▶ rồi ◀ | Số trang đổi đúng; quay lại trang 2 thì có highlight |
| Tài liệu đã xoá | Xoá `text.pdf` (SCR-06) → quay lại hội thoại | Chip hiển thị "Tài liệu đã bị xoá", bấm không có tác dụng (`disabled`) |
| Truy cập trái phép | User B mở hội thoại của A qua thao tác state (không thể từ UI) → gọi service | `NotFound` (đã phủ ở authz matrix; ở đây chỉ kiểm UI B không thấy hội thoại A) |

## Tiêu chí xong

- [ ] 4 kịch bản xanh trên CI (job e2e chạy nightly và trước release).

## Tham chiếu

US-13d, US-23 · Blueprint SCR-05
