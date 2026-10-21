# T-13b-1 — Trả lời cùng ngôn ngữ câu hỏi

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13b — Hỏi và nhận câu trả lời bằng ngôn ngữ làm việc (P0) — AC-13b.1 |
| Sprint | S3 |
| Tầng | APP |
| Ước lượng | 0.25d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-08-1, T-08-2, T-11-3 |
| Chặn | T-13b-4 |

## Bối cảnh

DR-07: câu trả lời cùng ngôn ngữ câu hỏi; thực thi bằng prompt + kiểm tra heuristic. Tài liệu có thể khác ngôn ngữ câu hỏi (hỏi tiếng Anh về tài liệu tiếng Việt).

## Phạm vi

**Làm:** bảo đảm quy tắc 1 của prompt (T-08-1) có hiệu lực; thêm chỉ dẫn ngôn ngữ tường minh vào user message; kiểm tra hậu kiểm.

## Đặc tả

- `PromptBuilder` (T-08-2) thêm dòng cuối user message: `Ngôn ngữ trả lời: Tiếng Việt` hoặc `Answer language: English` theo `detect_lang(question)`.
- Hậu kiểm trong `handle_answer` sau khi `Answered`: nếu `detect_lang(text các segment) != lang` → log warn `answer_lang_mismatch` + metric `cvd_answer_lang_mismatch_total` (không chặn câu trả lời; eval T-13b-4 mới là chốt chặn).
- Thông điệp NOT_FOUND do hệ thống tạo theo `lang` (T-11-1).
- Giao diện vẫn tiếng Việt (OQ-006); chỉ nội dung câu trả lời theo ngôn ngữ câu hỏi.

## Tiêu chí xong

- [ ] Câu hỏi tiếng Anh → prompt có "Answer language: English".
- [ ] Metric mismatch tăng khi FakeLLM cố tình trả sai ngôn ngữ.

## Test

`tests/unit/qa/test_prompt_language.py`; `tests/integration/qa/test_lang_mismatch_metric.py`.

## Tham chiếu

SADD §5.2.4 DR-07 · US-13b
