# T-22-4 — Test "canary": không có nội dung trong log, telemetry, audit

| Thuộc tính | Giá trị |
|---|---|
| Story | US-22 (P0); NFR-SEC-02 |
| Sprint | S3 (khi đã có luồng ask), chạy lại ở S5 |
| Tầng | TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | F-05, F-06, F-12, T-07-2, T-13-3, T-01-4 |
| Chặn | PLT-14 |

## Bối cảnh

US-22 ghi rõ: UI không chứa khoá API, không ghi nội dung hội thoại vào telemetry/log/URL. Cần bằng chứng tự động.

## Phạm vi

**Làm:** test end-to-end mức service (không cần trình duyệt) bơm chuỗi canary vào mọi đầu vào rồi quét mọi đầu ra không được chứa nội dung.

## Đặc tả

Canary: `CANARY-7f3a9c` (và biến thể có dấu tiếng Việt `CANARY-đặc-biệt`).

Bơm vào:
1. Tên tệp `CANARY-7f3a9c.pdf`, nội dung PDF chứa canary ở trang 1.
2. Câu hỏi chứa canary.
3. Lý do feedback chứa canary.

Chạy: upload → ingest (worker thật, embedding/LLM giả, FakeLLM trả câu có canary và marker `[S1]`) → ask → stream → feedback → delete.

Quét:
- Toàn bộ log (stdout) của web giả lập và worker, bắt bằng `capture_logs` hoặc đọc tệp log.
- `SELECT props::text FROM telemetry_events`, `SELECT metadata::text FROM audit_log`, `SELECT last_error, payload::text FROM jobs`.
- Metric text (`/metrics`).

Khẳng định: không chuỗi nào chứa `CANARY` (không phân biệt hoa thường). Ngoại lệ hợp lệ: các bảng nghiệp vụ được phép chứa nội dung (`documents.file_name`, `messages.content`, `document_chunks.text`, `answer_segments.text`, `citations.quote`, `feedback.reason`, `conversations.title`) — **không** quét các bảng này.

## Tiêu chí xong

- [ ] Test xanh; nếu đỏ thì sửa nguồn rò rỉ (không thêm ngoại lệ vào test nếu chưa được Security đồng ý).
- [ ] Chạy trong job `integration` CI.

## Test

`tests/security/test_no_content_leak.py`.

## Tham chiếu

US-22 · SADD §5.8.6, §5.9.3, NFR-SEC-02 · F-12
