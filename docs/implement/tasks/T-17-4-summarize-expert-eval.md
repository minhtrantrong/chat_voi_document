# T-17-4 — Chuyên gia chấm 5 bản tóm tắt mẫu (P2)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-17 (P2) — AC-17.1 |
| Sprint | S4–S5 — chỉ khi tính năng được làm |
| Tầng | TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | AI/Backend + chuyên gia nghiệp vụ |
| Phụ thuộc | T-17-2, T-12-4 (công cụ chấm) |
| Chặn | Quyết định bật cờ `FEATURE_SUMMARIZE` |

## Bối cảnh

AC-17.1: chuyên gia chấm ≥ 4/5 bản tóm tắt mẫu phản ánh đúng, không thêm nội dung ngoài tài liệu.

## Phạm vi

**Làm:** chọn 5 tài liệu đại diện, chạy tóm tắt, xuất bảng chấm, thu kết quả.

## Đặc tả

- Mở rộng eval runner: loại item `summarize` với khoá `document` (tên tệp); runner gọi `summarize` thay vì `ask`.
- `grading.csv` thêm cột `faithful` (Y/N: không có nội dung ngoài tài liệu) và `coverage` (Y/N: phản ánh ý chính).
- Đạt khi ≥ 4/5 bản có cả `faithful=Y` và `coverage=Y`.

## Tiêu chí xong

- [ ] Kết quả chấm ghi vào `docs/implement/eval_log.md`; PO quyết định bật/tắt cờ dựa trên kết quả.

## Tham chiếu

US-17 AC-17.1 · T-12-4
