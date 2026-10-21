# T-22-1 — Tài liệu luồng dữ liệu gửi cho Bảo mật/Pháp chế (gate G-01)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-22 — Xác nhận xử lý tài liệu tuân thủ chính sách (P0) — AC-22.1 |
| Sprint | S0 |
| Tầng | Tài liệu |
| Ước lượng | 1d |
| Owner gợi ý | Tech Lead/Architect |
| Phụ thuộc | Lựa chọn sơ bộ LLM/Embedding provider (Implement_plan §12 mục 2) |
| Chặn | Gate G-01 → dùng dữ liệu thật ở mọi môi trường; production |

## Bối cảnh

AC-22.1 là **điều kiện chặn bắt đầu phát triển với dữ liệu thật** (OQ-007, DEP-001). Bảo mật/Pháp chế cần một tài liệu ngắn, chính xác để ra quyết định bằng văn bản.

## Phạm vi

**Làm:** `docs/compliance/data_flow_ai.md` (hoặc nơi Security chỉ định nếu nhạy cảm), gửi review, theo dõi tới khi có văn bản phê duyệt.

## Đặc tả

Nội dung bắt buộc:

| Mục | Nội dung |
|---|---|
| 1. Dữ liệu gửi ra ngoài | Embedding: nội dung từng chunk (≤ 700 token) khi xử lý tài liệu; câu hỏi (hoặc câu hỏi + câu hỏi trước khi follow-up). LLM: tối đa 8 chunk (≤ 8.000 token), câu hỏi, tối đa 3 lượt hội thoại trước |
| 2. Dữ liệu **không** gửi | PDF gốc, tên/email người dùng, tên tệp (trừ khi nằm trong nội dung chunk — ghi rõ: nhãn `[S1] {file_name}` **có** được gửi trong prompt; cân nhắc thay bằng mã nếu Security yêu cầu) |
| 3. Nhà cung cấp | Tên, vùng xử lý dữ liệu, điều khoản retention / zero-retention, DPA, có dùng dữ liệu để huấn luyện không |
| 4. Kiểm soát kỹ thuật | TLS, egress allowlist (T-22-3), khoá an toàn `ALLOW_EXTERNAL_AI` (T-22-2), không log nội dung (F-12, T-22-4), xoá tài liệu có hiệu lực ngay (US-06), retention hội thoại 180 ngày |
| 5. Phương án thay thế | Self-host model (provider port ADR-009) nếu không được phép gửi ra ngoài; ảnh hưởng chi phí/chất lượng |
| 6. Quyết định cần | Được phép / không được phép / được phép có điều kiện; phân loại dữ liệu tối đa được nạp |

## Tiêu chí xong

- [ ] Tài liệu gửi Security/Legal trước giữa S0, có người nhận và hạn trả lời.
- [ ] Có văn bản phê duyệt (email/biên bản có chữ ký) lưu theo chỉ định của Security; Implement_plan §2 cập nhật trạng thái G-01.
- [ ] Nếu có điều kiện (ví dụ không gửi tên tệp), tạo ticket kỹ thuật tương ứng.

## Tham chiếu

US-22 · SADD §5.1 (luồng dữ liệu nhạy cảm), §5.8.6, RISK-06 · Implement_plan §2 G-01
