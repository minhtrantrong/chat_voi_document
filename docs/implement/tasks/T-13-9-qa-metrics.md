# T-13-9 — Metric hỏi đáp: first-token, thời gian trả lời, outcome

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13 (P0) — AC-13.1 (đo p90) |
| Sprint | S3 |
| Tầng | OPS |
| Ước lượng | 0.25d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | PLT-06, T-13-3 |
| Chặn | PLT-17, T-24-5 |

## Bối cảnh

SLI first token p90 ≤ 4 s (SADD §5.9.1); alert FirstTokenSlow (PLT-17). Metric phải phát từ đúng chỗ để số liệu khớp với `answers.first_token_ms`.

## Phạm vi

**Làm:** gắn metric đã khai báo ở PLT-06 vào code QA.

## Đặc tả

| Metric | Nơi ghi | Giá trị |
|---|---|---|
| `cvd_ask_total{outcome="submitted"}` | `QaService.ask` thành công | +1 |
| `cvd_ask_total{outcome=...}` | `finalize` | +1 theo outcome cuối |
| `cvd_first_token_seconds` | `record_first_token` | `first_ms / 1000` (từ `answers.created_at`) |
| `cvd_answer_seconds` | `finalize` | `total_ms / 1000` |
| `cvd_retrieval_hits`, `cvd_retrieval_score` | `Retriever.search` | số chunk, điểm cao nhất |
| `cvd_rate_limited_total{reason="ask"}` | `ask` bị chặn | +1 |

Ghi chú: first-token đo ở server **chưa** gồm độ trễ poll UI (≤ 0.4 s). Báo cáo load test (T-24-5) cộng thêm phần UI đo bằng Playwright.

## Tiêu chí xong

- [ ] Sau 10 câu hỏi trên compose, `/metrics` của worker-answer có histogram với `_count = 10`.

## Test

`tests/integration/qa/test_qa_metrics.py` (đọc `REGISTRY` sau khi chạy handler).

## Tham chiếu

SADD §5.9.1, §5.9.2 · PLT-06
