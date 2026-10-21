# 4+1 Architecture Views — “Chat với tài liệu” (MVP)

Bộ sơ đồ kiến trúc 4+1 cho MVP, bổ sung cho sơ đồ use case đã có. Tất cả tệp nằm trong `docs/design/` và mở được bằng [draw.io](https://app.diagrams.net) hoặc draw.io Desktop.

| View | Tệp | Số trang | Nội dung chính |
|---|---|---|---|
| +1 Scenario | `usecase_diagram.drawio` | 1 | Actor, use case, quan hệ include/extend |
| Logical | `class_diagram.drawio` | 1 | Domain model: User, Document, DocumentChunk, Conversation, Message, Answer, AnswerSegment, Citation, Feedback, AppConfig + 6 enum |
| Process | `sequence_diagram.drawio` | 5 | SD-01…SD-05 (xem bảng dưới) |
| Development | `component_diagram.drawio` | 1 | SPA, DMZ/edge, dịch vụ ứng dụng, ports/adapters, hạ tầng dữ liệu, dịch vụ ngoài |
| Physical | `deployment_diagram.drawio` | 1 | Máy trạm → Internet → VPC (DMZ, Kubernetes, data subnet) → dịch vụ ngoài; phương án cloud/on-prem |

**Ảnh PNG:** `usecase_diagram.png`, `class_diagram.png`, `sequence_diagram.png` (SD-01), `sequence_diagram_sd02.png`…`sequence_diagram_sd05.png`, `component_diagram.png`, `deployment_diagram.png`. Toàn bộ ảnh đã được nhúng vào `SADD.md` (Hình 1–9) và được ghi chú là kiến trúc tham chiếu khi khác với monolith Streamlit.

## Các trang Process View

| Trang | Kịch bản | Nguồn yêu cầu |
|---|---|---|
| SD-01 | Tải tài liệu lên (đồng bộ, validate, lưu, enqueue) | US-01…US-03 · AC-01…AC-03 |
| SD-02 | Xử lý & lập chỉ mục bất đồng bộ (extract → chunk → embed → index → SSE) | US-04 · AC-04 · BR-004, BR-013 |
| SD-03 | Hỏi đáp streaming, trích dẫn, not-found, lỗi/hủy | US-07…US-14 · AC-07…AC-14 · BR-010, BR-011 |
| SD-04 | Kiểm chứng trích dẫn (mở đúng trang) và đánh giá 👍/👎 | US-10, US-13d, US-19 · AC-10, AC-16, AC-19 |
| SD-05 | Xóa tài liệu, vô hiệu trích dẫn, bù trừ khi lỗi một phần | US-06, US-23 · AC-06, AC-25 · BR-006, BR-025 |

## Quy ước trình bày

- **Sequence**: lifeline = thành phần tham gia; nét liền = lời gọi đồng bộ; nét đứt = trả về hoặc sự kiện async; khối `[alt]`, `[loop]`, `[opt]` = rẽ nhánh/lặp/tùy chọn; ghi chú vàng = quy tắc nghiệp vụ.
- **Class**: xanh dương = entity, xanh lá = aggregate root, tím = configuration, vàng = enumeration; `◆` = composition; bội số ghi theo dạng `1 .. *`.
- **Component**: xanh dương = SPA, cam = edge/DMZ, xanh lá = dịch vụ nghiệp vụ, tím = hạ tầng, vàng = dịch vụ ngoài.
- **Deployment**: nét đứt bao = trust boundary/subnet; mũi tên liền = kết nối mạng; mũi tên đứt = metrics/logs hoặc luồng egress.

## Ghi chú thiết kế

- Luồng hỏi đáp chỉ dùng tài liệu `READY`; không có chunk đạt ngưỡng ⇒ `NOT_FOUND` và 0 citation (BR-004, BR-011).
- Mọi đoạn trả lời có thông tin từ tài liệu phải có ≥ 1 citation; citation lưu snapshot tên tài liệu/trang/anchor để vẫn hiển thị sau khi tài liệu bị xóa (BR-010, BRU-006).
- Xóa tài liệu là soft-delete + purge chunk/vector; lỗi một phần dùng outbox để bù trừ (BR-025, AC-06.2).
- Các điểm chưa chốt giữ nguyên mã OQ trong sơ đồ: OQ-005 (giới hạn cấu hình), OQ-007 (cloud/on-prem, nhà cung cấp LLM), OQ-008 (tài liệu dùng chung/riêng), OQ-013 (SSO).
