# T-14-3 — Eval hỏi tiếp: 10 kịch bản, đạt ≥ 8/10

| Thuộc tính | Giá trị |
|---|---|
| Story | US-14 (P1) — AC-14.1 |
| Sprint | S4 |
| Tầng | TEST |
| Ước lượng | 1d |
| Owner gợi ý | AI/Backend + BA |
| Phụ thuộc | T-12-1, T-12-2, T-14-2 |
| Chặn | PLT-16 |

## Bối cảnh

AC-14.1: câu hỏi có đại từ tham chiếu được hiểu đúng ≥ 8/10 kịch bản mẫu.

## Phạm vi

**Làm:** mở rộng `golden_v1.yaml` lên 10 mục `followup`; chạy với cờ rewrite tắt và bật; ghi kết quả vào `docs/implement/eval_log.md`.

## Đặc tả

Mỗi mục có `history` 1–2 câu và `question` chứa tham chiếu:

| Loại tham chiếu | Ví dụ history → question |
|---|---|
| Đại từ "nó" | "Hợp đồng ký với bên nào?" → "Còn hạn chót của nó?" |
| "cái đó / điều đó" | "Phụ lục B nói gì về bảo hành?" → "Điều đó áp dụng trong bao lâu?" |
| Lược chủ ngữ | "Giá gói Cơ bản là bao nhiêu?" → "Còn gói Nâng cao?" |
| Tham chiếu số thứ tự | "Liệt kê các mốc nghiệm thu" → "Mốc thứ hai cần những gì?" |
| Chuyển tài liệu | "Hợp đồng quy định phạt chậm thế nào?" → "Báo giá có nhắc tới việc này không?" |

Quy trình:
1. Chạy `--only followup` với `FEATURE_QUERY_REWRITE=false` → ghi `followup_accuracy`.
2. Nếu < 0.8 → bật cờ, chạy lại; ghi chi phí và p90 first-token tăng thêm.
3. Đề xuất giá trị cờ cho release cho PO (kèm số liệu).

## Tiêu chí xong

- [ ] 10 mục được BA duyệt.
- [ ] Có số liệu hai cấu hình và đề xuất.

## Tham chiếu

US-14 AC-14.1 · TD-08 · T-12-3 (`followup_accuracy`)
