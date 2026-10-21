# T-12-5 — Eval gate: so sánh baseline và chặn hồi quy trong CI

| Thuộc tính | Giá trị |
|---|---|
| Story | US-12 (P0); ADR-013 |
| Sprint | S3 |
| Tầng | OPS / TEST |
| Ước lượng | 1d |
| Owner gợi ý | AI/Backend + QA/DevOps |
| Phụ thuộc | T-12-3, PLT-03 |
| Chặn | PLT-16 |

## Bối cảnh

ADR-013: chặn release nếu chỉ số giảm > 5% hoặc dưới ngưỡng OQ-002; chạy nightly và trước khi đổi prompt/model.

## Phạm vi

**Làm:** `python -m app.eval compare`, tệp ngưỡng, job nightly và job PR có điều kiện.

## Đặc tả

`tests/eval/thresholds.yaml`:

```yaml
absolute:                         # dưới ngưỡng → fail
  citation_precision: 0.90
  not_found_accuracy: 0.90
  counter_factual_accuracy: 0.90
  followup_accuracy: 0.80
  lang_match: 1.00
  uncited_informative_segments_max: 0
  p90_first_token_ms_max: 4000    # chỉ áp ở staging có LLM thật
  error_rate_max: 0.02
relative_drop_max: 0.05           # giảm quá 5% (tương đối) so với baseline → fail
```

`python -m app.eval compare --baseline tests/eval/baselines/<file>.json --current reports/eval/<run>/summary.json --thresholds tests/eval/thresholds.yaml` → in bảng so sánh (Markdown, dùng làm comment PR), thoát mã 1 nếu vi phạm.

CI:
- **Nightly** (PLT-03 `nightly.yml`): chạy trên staging với provider thật (khi G-01 cho phép) hoặc giả; so với baseline mới nhất; fail thì báo kênh đội.
- **PR có điều kiện**: workflow chạy khi PR thay đổi `prompts/**`, `app/qa/**`, `app/ingestion/chunker.py`, hoặc có label `needs-eval`; dùng môi trường staging riêng (`concurrency: eval-staging`).
- Cập nhật baseline: chỉ bằng PR riêng do AI Lead tạo, đính kèm summary mới + lý do.

## Tiêu chí xong

- [ ] Đổi một ký tự trong prompt → PR tự kích hoạt eval và đăng bảng so sánh.
- [ ] Giả lập summary tệ hơn baseline 6% → compare thoát mã 1.

## Test

`tests/unit/eval/test_compare.py`.

## Tham chiếu

ADR-013 · SADD §5.5.3, §5.5.4 · RISK-12
