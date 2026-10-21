# PLT-15 — Kiểm thử chịu lỗi (chaos) cho worker, Redis, LLM

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S5, mục 5.5) |
| Sprint | S5 |
| Tầng | TEST |
| Ước lượng | 1.5d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | T-13-3, T-13-8, T-04-5, F-08 |
| Chặn | M5 |

## Bối cảnh

QA-05, QA-08, NFR-REL-02/03: hệ thống phải kết thúc rõ ràng (không treo UI, không mất job) khi worker chết, Redis mất, LLM lỗi.

## Phạm vi

**Làm:** script chaos trên compose staging, cơ chế tiêm lỗi cho LLM giả, báo cáo kết quả.

**Không làm:** chaos ở production.

## Đặc tả

Tiêm lỗi: `FakeLLM` (T-08-3) đọc env `LLM_FAULT` = `none | timeout_first_token | http_503 | slow_stream:200ms | drop_midstream`. Có thể bật cho từng lần chạy compose.

| # | Kịch bản | Cách tạo | Kết quả mong đợi |
|---|---|---|---|
| 1 | Worker-ingest bị kill giữa ingest | `docker kill` khi tài liệu 300 trang đang xử lý | Job được reclaim ≤ 15 phút (đặt `visibility_timeout` 60 s khi test); tài liệu READY, số chunk đúng, không trùng |
| 2 | Worker-answer bị kill giữa stream | kill khi đang stream | Reaper đưa answer về `ERROR`, message `INTERRUPTED`; UI hiện "Chưa hoàn tất" + Tạo lại trong ≤ 2 phút |
| 3 | Redis dừng trước khi hỏi | `docker stop redis` | `ask` trả `ERR-REDIS-UNAVAILABLE`, không tạo answer/job; danh sách tài liệu và lịch sử vẫn xem được |
| 4 | Redis dừng giữa stream | stop khi đang stream | Fallback DB: UI kết thúc ở trạng thái lỗi rõ ràng, không quay vô hạn |
| 5 | LLM 503 | `LLM_FAULT=http_503` | `ERR-LLM-UNAVAILABLE`, breaker mở 60 s, câu hỏi vẫn nằm trong hội thoại, bấm Thử lại được |
| 6 | LLM không trả token đầu | `timeout_first_token` | `ERR-LLM-TIMEOUT` sau ~10 s |
| 7 | Postgres restart | `docker restart postgres` | Web hiện lỗi thân thiện trong lúc restart; sau đó tự phục hồi nhờ pool `pre_ping` |
| 8 | Đầy đĩa tạm của worker | mount tmpfs 50 MB cho `/tmp` của worker-ingest | Ingest ERROR `EXTRACT_FAILED`, worker không chết |

Script `tests/chaos/run_chaos.py` chạy tuần tự, mỗi kịch bản có hàm kiểm tra trạng thái DB/UI, xuất `reports/chaos/<date>.md`.

## Tiêu chí xong

- [ ] 8/8 kịch bản đạt kết quả mong đợi; kịch bản nào không đạt có bug và fix trước M5.
- [ ] Báo cáo lưu trong `reports/chaos/`.

## Tham chiếu

SADD §5.3.4 (Hủy và phục hồi), §5.3.10, §7.2 QA-05/QA-08, §7.3
