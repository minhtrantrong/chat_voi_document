# T-12-3 — Chỉ số eval tự động

| Thuộc tính | Giá trị |
|---|---|
| Story | US-12 (P0); US-08, US-09, US-10, US-11, US-13, US-13b, US-14 |
| Sprint | S3 |
| Tầng | TEST |
| Ước lượng | 1d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-12-2 |
| Chặn | T-12-5, PLT-16 |

## Bối cảnh

SADD §5.5.3: đo accuracy, citation precision, not-found accuracy, p90 first-token, cost/answer. Accuracy chính thức do chuyên gia chấm (T-12-4); task này tính các chỉ số tự động làm xấp xỉ và để chặn hồi quy.

## Phạm vi

**Làm:** `app/eval/metrics.py::compute(results, dataset) -> Summary`.

## Đặc tả

| Chỉ số | Định nghĩa | Áp dụng cho |
|---|---|---|
| `must_include_recall` | tỉ lệ item mà câu trả lời chứa **mọi** chuỗi `must_include` (so khớp sau chuẩn hoá NFC + lowercase + gộp khoảng trắng) và không chứa `must_not_include` | in_doc, multi_doc, counter_factual, followup, lang_en |
| `citation_precision` | citation khớp (cùng file, cùng page) / tổng citation | item có `expected_citations` |
| `citation_recall` | expected_citations được trích / tổng expected | như trên |
| `multi_doc_coverage` | item multi_doc có citation tới **tất cả** file mong đợi / tổng item multi_doc | multi_doc |
| `not_found_accuracy` | item `expected_outcome=NOT_FOUND` mà outcome = NOT_FOUND và 0 citation / tổng | out_of_scope |
| `false_not_found_rate` | item mong đợi ANSWERED nhưng NOT_FOUND / tổng | còn lại |
| `uncited_informative_segments` | số segment `cited=False`, dài > 40 ký tự, không kết thúc bằng ":" trong các câu ANSWERED | tất cả |
| `lang_match` | `detect_lang(answer) == expected_lang` (mặc định = ngôn ngữ câu hỏi) | tất cả ANSWERED |
| `counter_factual_accuracy` | như `must_include_recall` nhưng chỉ cho counter_factual | counter_factual |
| `followup_accuracy` | như trên cho followup | followup |
| `p50/p90_first_token_ms`, `p90_total_ms` | từ `answers.first_token_ms/total_ms` | tất cả |
| `error_rate` | outcome ERROR/TIMEOUT / tổng | tất cả |
| `cost_per_answer_usd`, `tokens_per_answer` | trung bình | tất cả |

`summary.json` có `metrics` (tổng) và `by_type` (theo từng `type`). In bảng tóm tắt ra stdout.

## Tiêu chí xong

- [ ] Unit test với `results` dựng tay cho từng chỉ số (gồm trường hợp chia cho 0 → `null`).
- [ ] Summary của bộ tạm 30 câu sinh được.

## Test

`tests/unit/eval/test_metrics.py`.

## Tham chiếu

SADD §5.5.3 · US-08…US-14 (AC dựa trên eval)
