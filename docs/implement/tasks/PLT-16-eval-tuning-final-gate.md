# PLT-16 — Tinh chỉnh RAG và chốt eval gate phát hành

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S5, mục 5.6) |
| Sprint | S5 |
| Tầng | TEST / AI |
| Ước lượng | 3d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-12-1…T-12-6, G-04 (bộ câu hỏi thật), G-05 (ngưỡng) |
| Chặn | M5 |

## Bối cảnh

Eval ở S3 chỉ cần *đo được*; S5 phải *đạt* ngưỡng OQ-002 (mặc định accuracy ≥ 80%, citation precision ≥ 90%, NOT_FOUND ≥ 9/10) và lưu baseline phát hành (ADR-013).

## Phạm vi

**Làm:** vòng lặp tinh chỉnh có ghi chép, chấm tay với chuyên gia, chốt baseline, PO ký.

**Không làm:** đổi kiến trúc retrieval lớn (hybrid search TD-01) — nếu cần thì đề xuất ADR, không tự làm trong task này.

## Đặc tả

Tham số được phép chỉnh (đều trong `app_config`/prompt, không sửa code domain):

| Tham số | Khoảng thử |
|---|---|
| `RETRIEVAL_MIN_SCORE` | 0.20 – 0.40 |
| `RETRIEVAL_TOP_K` | 6 – 12 |
| `MAX_CHUNKS_PER_DOC` | 3 – 6 |
| `CHUNK_SIZE_TOKENS` / overlap | 500/75 – 900/135 (đổi thì phải re-ingest bộ eval) |
| Prompt | `qa_answer.v1` → `v2` (file mới, không sửa v1) |
| `FEATURE_QUERY_REWRITE` | on/off (US-14) |

Quy trình:
1. Chạy `app.eval run` với cấu hình hiện tại → baseline S3.
2. Mỗi thay đổi **một** tham số → chạy lại → ghi một dòng vào `docs/implement/eval_log.md` (ngày, thay đổi, chỉ số, quyết định giữ/bỏ).
3. Khi chỉ số tự động ổn định: xuất `grading.csv`, chuyên gia nghiệp vụ chấm, nhập lại (`app.eval grade`).
4. Đạt ngưỡng → commit `tests/eval/baselines/release_v1.json` + cấu hình chốt; cập nhật `app_config` seed.
5. PO ký biên bản `docs/implement/eval_signoff.md`.

## Tiêu chí xong

- [ ] `accuracy ≥ ngưỡng OQ-002`, `citation_precision ≥ MET-003`, `not_found_accuracy ≥ 0.9`, `uncited_informative_segments == 0`, `p90_first_token ≤ 4 s`.
- [ ] Bộ `injection` 100% đạt.
- [ ] Baseline phát hành được commit; CI nightly so sánh với baseline này.
- [ ] Biên bản ký của PO.

## Tham chiếu

ADR-013 · SADD §5.5.3 · US-12 · T-12-5
