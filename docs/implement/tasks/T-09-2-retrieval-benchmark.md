# T-09-2 — Benchmark truy hồi ở quy mô 1.000 tài liệu

| Thuộc tính | Giá trị |
|---|---|
| Story | US-09 (P0); NFR-PERF-02; US-24 |
| Sprint | S5 (chuẩn bị script ở S3) |
| Tầng | TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-09-1, staging có tài nguyên gần production |
| Chặn | T-24-5 |

## Bối cảnh

NFR-PERF-02: truy hồi ≤ 300 ms p95 ở 2 triệu chunk (ASM-006: ≤ 1.000 tài liệu).

## Phạm vi

**Làm:** `tests/perf/seed_chunks.py` và `tests/perf/bench_retrieval.py`.

## Đặc tả

- Seed: 1.000 tài liệu READY (300 user giả, 30% SHARED), tổng 2.000.000 chunk, vector ngẫu nhiên chuẩn hoá (dim 1536), `embedding_model` đúng. Dùng `COPY` binary để seed nhanh; build HNSW sau khi seed (`maintenance_work_mem=512MB`).
- Benchmark: 1.000 truy vấn với vector ngẫu nhiên, actor ngẫu nhiên, 20% có scope 1–3 tài liệu; chạy với 10 luồng đồng thời; đo thời gian **câu SQL** và thời gian **Retriever.search** (gồm neighbors).
- Ghi kết quả p50/p95/p99 và recall@8 so với tìm chính xác (`SET enable_indexscan=off` trên mẫu 50 truy vấn).
- Xuất `reports/perf/retrieval_<date>.md`.

## Tiêu chí xong

- [ ] p95 `Retriever.search` ≤ 300 ms ở 10 luồng.
- [ ] recall@8 ≥ 0.9 (nếu thấp: tăng `ef_search`, ghi lại trong báo cáo và ADR nếu đổi mặc định).

## Tham chiếu

SADD §5.4.3, §7.3 NFR-PERF-02, RISK-08
