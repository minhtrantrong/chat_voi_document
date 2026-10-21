# T-13b-4 — Eval ngôn ngữ trả lời

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13b (P0) — AC-13b.1 |
| Sprint | S3 |
| Tầng | TEST |
| Ước lượng | 0.25d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-12-1, T-12-3, T-11-3 |
| Chặn | PLT-16 |

## Bối cảnh

AC-13b.1: câu hỏi bằng ngôn ngữ trong OQ-006 → câu trả lời bằng cùng ngôn ngữ.

## Phạm vi

**Làm:** ≥ 2 mục `lang_en` (bắt buộc theo phân bổ) + thêm 4 mục tiếng Anh/tiếng Việt không dấu; chỉ số `lang_match` (đã định nghĩa ở T-12-3).

## Đặc tả

| Mục | Câu hỏi | Tài liệu | expected_lang |
|---|---|---|---|
| L1 | "What is the submission deadline?" | hop-dong.pdf (tiếng Việt) | en |
| L2 | "Which appendix extends the deadline?" | phu-luc-B.pdf | en |
| L3 | "han chot nop ho so la ngay nao" (không dấu) | hop-dong.pdf | vi |
| L4 | "Bảng giá có hiệu lực đến khi nào?" | bao-gia.pdf (tiếng Anh) | vi |
| L5 | "Is there a penalty clause?" (ngoài phạm vi) | — | en (câu NOT_FOUND tiếng Anh) |
| L6 | "Điều khoản phạt là gì?" | hop-dong.pdf | vi |

Mục tiêu: `lang_match == 1.0` (T-12-5 `thresholds.yaml`).

## Tiêu chí xong

- [ ] 6 mục có trong `golden_v1.yaml`, validate xanh.

## Tham chiếu

US-13b · T-12-3, T-12-5
