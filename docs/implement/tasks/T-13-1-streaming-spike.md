# T-13-1 — Spike: stream token qua Redis + `st.fragment` và nút Dừng

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13 — Thấy câu trả lời xuất hiện nhanh (P0) — AC-13.2; NFR-UX-01 |
| Sprint | S3 (ngày 1–3) — **ưu tiên cao nhất của sprint** |
| Tầng | INF / UI (code thử nghiệm) |
| Ước lượng | 2.5d |
| Owner gợi ý | Tech Lead |
| Phụ thuộc | PLT-04, PLT-07 |
| Chặn | Quyết định go/no-go cho T-13-2…T-13-7 |

## Bối cảnh

ADR-005 là điểm khác biệt rủi ro nhất của kiến trúc: `st.write_stream` chặn ScriptRunner nên nút Dừng không chạy; giải pháp là worker ghi Redis Stream, UI dùng fragment rerun mỗi 350–500 ms. Cần chứng minh trước khi đầu tư (IR-02).

## Phạm vi

**Làm:** thư mục `spikes/streaming/` (không merge vào `app/`): một worker giả phát token vào Redis, một trang Streamlit đọc bằng fragment, nút Dừng trong fragment; script đo.

**Không làm:** code production.

## Đặc tả

Kịch bản đo (ghi kết quả vào `spikes/streaming/RESULT.md`):

| # | Kiểm tra | Tiêu chí đạt |
|---|---|---|
| 1 | Độ mượt: 600 token, 30 ms/token, `run_every=0.4` | Văn bản tăng dần đều, không nhấp nháy toàn trang |
| 2 | Bấm Dừng giữa stream | Worker thấy cờ cancel và dừng ≤ 2 s; UI giữ phần đã nhận |
| 3 | Widget khác (checkbox tài liệu, cuộn) khi đang stream | Vẫn tương tác được |
| 4 | 10 tab/phiên đồng thời stream | CPU container web < 70% của 2 vCPU; không phiên nào treo |
| 5 | Độ trễ từ XADD token đầu tới khi hiện trên trình duyệt | p90 ≤ 500 ms |
| 6 | Đóng tab giữa stream, mở lại | Không lỗi phía server; worker hoàn tất bình thường |
| 7 | Fragment tự dừng khi `done` (`st.rerun()` toàn app) | Không còn request định kỳ sau khi xong |
| 8 | `run_every` 0.25 / 0.4 / 0.6 | Chọn giá trị cân bằng mượt/CPU, ghi lý do |

Chỉ dẫn kỹ thuật cho spike:
- Nút Dừng **phải** nằm bên trong hàm fragment (SADD §5.7.1).
- Đọc stream bằng `XREAD COUNT 200 STREAMS answer:{id} <last_id>` không block.
- Trong fragment không gọi `time.sleep`.

## Tiêu chí xong

- [ ] `RESULT.md` có số liệu 8 kịch bản, video ngắn (≤ 1 phút) và kết luận **GO / NO-GO**.
- [ ] Nếu NO-GO: đề xuất phương án B (endpoint streaming mỏng FastAPI + component nhúng), ước lượng ảnh hưởng, ghi ADR nháp; báo PO trong ngày (Implement_plan §10).

## Tham chiếu

ADR-005 · SADD §5.3.4 (Vì sao không dùng `st.write_stream`) · Implement_plan §4 S3 mục 3.1, §8 IR-02
