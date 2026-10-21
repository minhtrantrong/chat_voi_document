# T-08-4 — Bộ eval "phản thực tế" (tài liệu khác kiến thức phổ thông)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-08 (P0) — AC-08.1 |
| Sprint | S3 |
| Tầng | TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | AI/Backend + BA |
| Phụ thuộc | T-12-1 (định dạng bộ eval) |
| Chặn | PLT-16 |

## Bối cảnh

AC-08.1: câu hỏi mà đáp án phổ thông khác với tài liệu → câu trả lời theo tài liệu, đạt ≥ 9/10.

## Phạm vi

**Làm:** tài liệu eval `tests/eval/docs/counter_factual.pdf` (sinh bằng script, nội dung hư cấu có chủ đích) và ≥ 10 mục `type: counter_factual` trong `golden_v1.yaml`.

## Đặc tả

Nguyên tắc soạn:
- Tài liệu chứa các "sự thật nội bộ" trái kiến thức phổ thông nhưng hợp lý trong bối cảnh dự án, ví dụ: "Theo hợp đồng này, tuần làm việc của nhà thầu là 4 ngày (thứ Hai–thứ Năm)", "Thủ đô được dùng làm địa điểm nghiệm thu là Đà Nẵng", "Thuế VAT áp dụng cho gói thầu là 0%".
- Câu hỏi hỏi trực tiếp điều đó ("Tuần làm việc của nhà thầu có mấy ngày?").
- `must_include` là đáp án theo tài liệu ("4 ngày"); thêm `must_not_include` là đáp án phổ thông ("5 ngày").

Mở rộng định dạng (T-12-1): khoá `must_not_include: [..]`; chỉ số `counter_factual_accuracy = tỉ lệ mục có đủ must_include và không có must_not_include`.

## Tiêu chí xong

- [ ] ≥ 10 mục, được BA review là rõ ràng, không mơ hồ.
- [ ] Chạy `python -m app.eval run --only counter_factual` ra chỉ số; mục tiêu ≥ 0.9 (đạt chính thức ở PLT-16).

## Tham chiếu

US-08 AC-08.1 · T-12-1 · ADR-013
