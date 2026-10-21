# T-12-2 — Eval runner chạy qua đúng luồng production

| Thuộc tính | Giá trị |
|---|---|
| Story | US-12 (P0) |
| Sprint | S3 |
| Tầng | TEST |
| Ước lượng | 1.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-12-1, T-07-2, T-13-3, T-01-4, T-04-4 |
| Chặn | T-12-3, T-12-4, T-12-5 |

## Bối cảnh

Eval phải đo hệ thống **thật** (`DocumentService`, `QaService`, worker), không gọi LLM trực tiếp, để kết quả phản ánh retrieval + prompt + validator.

## Phạm vi

**Làm:** `app/eval/__main__.py` (CLI), `app/eval/runner.py`. Package `app.eval` nằm trong app (dùng được trên staging), không import UI.

## Đặc tả

CLI:

```
python -m app.eval run --dataset tests/eval/golden_v1.yaml [--only TYPE[,TYPE]] [--out reports/eval/<run_id>]
```

Luồng:

```text
1. Actor hệ thống: user "eval-bot" (subject "system:eval", role END_USER) — tạo nếu chưa có.
2. Nạp tài liệu: với mỗi file trong dataset.documents, nếu eval-bot chưa có tài liệu READY cùng checksum → upload;
   chờ tất cả READY (timeout 10 phút; lỗi → dừng với báo cáo).
3. Với mỗi item (tuần tự, để đo latency sạch):
   - Hội thoại mới; nếu có history: hỏi lần lượt từng câu history (chờ terminal), rồi hỏi question trong cùng hội thoại.
   - scope: map tên tệp → document_id.
   - ask(); poll get_answer mỗi 200 ms tới khi is_terminal (timeout 90 s → ghi outcome "TIMEOUT").
   - Ghi kết quả: outcome, segments (text), citations (file, page), first_token_ms, total_ms,
     prompt/completion tokens, cost_estimate_usd, error_code.
4. Ghi reports/eval/<run_id>/results.jsonl + summary.json (chỉ số ở T-12-3) + meta.json
   (git sha, LLM_MODEL, EMBEDDING_MODEL, prompt_version, app_config liên quan, thời gian).
```

- Rate limit: eval-bot được miễn rate limit bằng cấu hình `RATE_LIMIT_EXEMPT_SUBJECTS=system:eval` (thêm vào `RedisGuard`, T-07-3) — chỉ bật ở staging/CI.
- Không ghi nội dung câu trả lời ra log; chỉ ghi vào thư mục report (được coi là dữ liệu kiểm thử, không phải log vận hành). Report **không** commit nếu tài liệu eval là tài liệu thật (thêm `reports/` vào `.gitignore`).

## Tiêu chí xong

- [ ] Chạy trên compose local với `FakeLLM`/`FakeEmbedding` hoàn tất 30 câu và sinh đủ 3 tệp kết quả.
- [ ] Chạy lại không upload lại tài liệu (dùng checksum).

## Test

`tests/integration/eval/test_runner_smoke.py` (dataset 3 câu, Fake providers).

## Tham chiếu

US-12 · ADR-013 · SADD §5.5.3
