# T-24-5 — Chạy kiểm thử tải và báo cáo SLO

| Thuộc tính | Giá trị |
|---|---|
| Story | US-24 (P0) — AC-24.1; US-13 — AC-13.1 |
| Sprint | S5 |
| Tầng | TEST |
| Ước lượng | 1d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | T-24-4, T-09-2, PLT-17 (dashboard để quan sát) |
| Chặn | M5 |

## Bối cảnh

AC-24.1: với số tài liệu và người dùng đồng thời theo OQ-005 (mặc định 1.000 tài liệu, 10 đồng thời), ngưỡng p90 của US-13 vẫn đạt (mặc định 4 s, OQ-011).

## Phạm vi

**Làm:** chạy kịch bản trên staging cấu hình gần production (16 vCPU/32 GB hoặc theo G-06), phân tích, tối ưu nếu cần, báo cáo.

## Đặc tả

Kịch bản chính: dữ liệu nền 1.000 tài liệu (T-09-2 seed), 10 người dùng ảo, 50 câu/giờ, 30 phút, 5 upload 20 MB ở phút 10.

| Tiêu chí | Ngưỡng |
|---|---|
| p90 first-token (backend + overhead UI đo được) | ≤ 4 s (OQ-011) |
| Tỉ lệ lỗi (ERROR + timeout) | < 2% |
| Upload ack p95 | ≤ 2 s |
| Queue age p95 | ≤ 60 s |
| CPU web | < 70% |
| Không job nào DEAD | 0 |

Kịch bản phụ (stress, để biết giới hạn): tăng lên 20 người dùng đồng thời trong 10 phút; ghi điểm gãy (không phải tiêu chí đạt).

Nếu không đạt: phân tích theo ngân sách độ trễ (Implement_plan §17 US-13) — claim, embed, retrieval, LLM TTFT, poll — tối ưu phần vượt (ví dụ tăng thread worker-answer, giảm `MAX_CONTEXT_TOKENS`, đổi model); mỗi thay đổi về prompt/model phải qua eval gate.

Báo cáo `docs/implement/load_test_report_<date>.md`: cấu hình máy, phiên bản, provider, kết quả bảng trên, biểu đồ (ảnh Grafana), kết luận đạt/không đạt, việc cần làm.

## Tiêu chí xong

- [ ] Báo cáo có kết luận **đạt** cho kịch bản chính, đính kèm M5.

## Tham chiếu

US-24 AC-24.1 · US-13 AC-13.1 · SADD §5.9.1, §7.2 QA-03/QA-09
