# T-24-4 — Load harness cho hỏi đáp và tải lên

| Thuộc tính | Giá trị |
|---|---|
| Story | US-24 (P0) — AC-24.1; US-13 — AC-13.1 |
| Sprint | S5 (khung có thể dựng ở S4) |
| Tầng | TEST |
| Ước lượng | 2d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | T-07-2, T-13-3, T-13-2, T-01-4, T-09-2 (seed dữ liệu) |
| Chặn | T-24-5 |

## Bối cảnh

Locust không điều khiển websocket Streamlit thuận tiện; harness gọi trực tiếp `QaService`/`DocumentService` (cùng image, cùng DB/Redis/worker như staging) để đo backend, kèm Playwright nhỏ đo phần UI (Implement_plan §22).

## Phạm vi

**Làm:** `tests/load/harness.py`, `tests/load/ui_probe.py`, script seed người dùng ảo.

## Đặc tả

```
python -m tests.load.harness --users 10 --rate 50/h --duration 30m \
    --dataset tests/eval/golden_v1.yaml --uploads "5x20MB@10m" --report reports/load/<date>.json
```

Mỗi người dùng ảo (thread):
1. Actor riêng (user seed `load-user-01…10`, có tài liệu READY của bộ eval chia sẻ SHARED).
2. Vòng lặp: chờ theo phân phối Poisson để tổng hệ thống ≈ 50 câu/giờ; chọn câu ngẫu nhiên trong dataset (bỏ loại injection).
3. `t_submit` → `ask()` → đọc Redis stream (cùng `TokenStreamPort`) mỗi 50 ms tới token đầu (`t_first`) và `done` (`t_done`); ghi outcome, error_code.
4. Uploads: tại phút 10, một người dùng ảo tải 5 tệp 20 MB qua `DocumentService.upload` và đo thời gian ack.

Song song: `ui_probe.py` (Playwright, 2 người dùng thật qua trình duyệt) gửi 1 câu/2 phút, đo từ khi bấm gửi tới khi chữ đầu tiên xuất hiện trong DOM → ước lượng phần cộng thêm của UI.

Báo cáo JSON + Markdown: p50/p90/p99 first-token (backend và UI), tổng thời gian, tỉ lệ lỗi theo mã, upload ack p95, queue age p95 (đọc từ Prometheus), CPU/RAM từng container (`docker stats` mẫu mỗi 10 s).

- Rate limit: user tải được miễn qua `RATE_LIMIT_EXEMPT_SUBJECTS` (staging).
- Dùng LLM thật nếu G-01 cho phép; nếu không, `FakeLLM` với `LLM_FAKE_TOKEN_MS` mô phỏng độ trễ provider (ghi rõ trong báo cáo).

## Tiêu chí xong

- [ ] Harness chạy 5 phút trên compose local không lỗi và ra báo cáo đủ các chỉ số.

## Tham chiếu

SADD §5.5.3 (Load), §7.2 QA-03/QA-09 · US-24 · Implement_plan §22
