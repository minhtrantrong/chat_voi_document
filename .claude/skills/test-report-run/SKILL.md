---
name: test-report-run
description: Thực thi một test case trình duyệt (ST/UI/SEC/PF/EV/REG) trong docs/testing/testcases/ và sinh bộ artifact test_reports/<ID>/ gồm report.md, screenshots/Vxx-*.png, video. Dùng khi người dùng nói "chạy test ST-03", "test case UI-02", "làm report cho SEC-01", "retest BUG-ST02-01", hoặc yêu cầu chạy một test case và ghi kết quả.
---

# test-report-run — Chạy 1 test case và lập test report

Đầu vào: một mã test case (vd `ST-03`), hoặc một bug ID cần retest (vd `BUG-ST02-01`, tức chạy lại case `ST-02`).
Đầu ra: thư mục `test_reports/<ID>/` đúng quy ước tại [docs/testing/testcases/README.md](../../../docs/testing/testcases/README.md) §1, qua được `test-report-check`.

## Nguyên tắc không được vi phạm

1. **Không sửa code ứng dụng trong lúc test.** Thấy bug thì ghi nhận, chụp bằng chứng, rồi chạy tiếp.
2. **Không bịa kết quả.** Cột "Thực tế" chỉ ghi điều đã quan sát được: chữ hiển thị trên UI, output lệnh, giá trị trong SQLite/Qdrant. Bước nào không chạy được thì ghi `BLOCKED` kèm lý do, không ghi PASS.
3. **Không tự xoá dữ liệu có sẵn** (`data/`, collection Qdrant) để thoả tiền điều kiện "kho trống". Phải hỏi người dùng trước: làm trống kho, hay giữ nguyên dữ liệu và ghi sai lệch.
4. Mọi artifact chỉ nằm trong `test_reports/<ID>/`. Dữ liệu test tự tạo thì để ở `test_reports/<ID>/test-data/`.

## Quy trình

### 1. Đọc test case
- Mở `docs/testing/testcases/<ID>-*.md`. Ghi lại: tiền điều kiện (§2), dữ liệu (§3), bảng bước + mã Vxx (§4), kết quả mong đợi tổng thể (§5), tiêu chí Pass/Fail (§7), mẫu report (§9).
- Nếu chạy retest: đọc `test_reports/<ID>/report.md` cũ và bảng bug. Đổi tên thư mục cũ thành `test_reports/<ID>/_run-<ngày cũ>/` trước khi ghi lần chạy mới (hỏi người dùng nếu họ muốn ghi đè).

### 2. Kiểm tra môi trường (không đạt thì dừng, không đoán)
- Qdrant: `curl -s http://localhost:6333/healthz` (hoặc `docker compose ps`).
- App: `curl -s -o /dev/null -w "%{http_code}" http://localhost:8501/` phải trả về 200.
- LLM/Embedding endpoint phản hồi (cần cho ST-03…05, EV, PF-02).
- Fixtures cần dùng có trong `tests/eval/fixtures/`. Kiểm tra thuộc tính mà test case dựa vào (số trang, dung lượng, có text hay không), ví dụ bằng PyMuPDF. Fixture sai thì ghi sai lệch + bug dữ liệu test (tham khảo BUG-ST01-01).
- Thu thập thông tin cho dòng Môi trường: OS, Python, Streamlit, image Qdrant, model LLM, model Embedding (+ số chiều), trình duyệt + công cụ điều khiển, viewport.
- Gặp điều kiện tạm dừng ở test plan §8.0 (Qdrant không healthy, endpoint chết, đổi model giữa chừng, bug S1 chặn luồng chính): dừng lại, báo người dùng, report ghi `BLOCKED`.

### 3. Chuẩn bị ghi hình
- Tạo `test_reports/<ID>/screenshots/`.
- Bắt đầu quay video **trước** bước 1 và quay liên tục tới hết bước cuối. Lưu `video.webm` hoặc `video.mp4`.
- Khung hình phải thấy URL `http://localhost:8501/`. Nếu công cụ chỉ quay vùng nội dung trang (headless, `agent-browser record`, Playwright `recordVideo`), gắn nhãn cố định hiển thị `location.href` bằng JS phía trình duyệt, không sửa app. Đoạn mẫu có trong [references/report-conventions.md](references/report-conventions.md). Ghi việc này vào bảng sai lệch.
- Công cụ: dùng thứ đang có sẵn (Playwright, `agent-browser`, Claude in Chrome, trình duyệt có sẵn…). Các bước terminal/Qdrant dashboard/DevTools cũng phải có ảnh chụp chính cửa sổ đó, hoặc output thật hiển thị trong một tab rồi chụp, kèm ghi chú.

### 4. Thực hiện từng bước
Với mỗi dòng trong bảng bước:
1. Làm đúng thao tác mô tả. Nếu phải mô phỏng (kéo-thả bằng sự kiện DataTransfer, gán `input[type=file]`), ghi vào bảng sai lệch.
2. Chụp ảnh **ngay khi trạng thái kỳ vọng xuất hiện**. Trạng thái thoáng qua như "Đang xử lý" phải chụp trước khi biến mất. Đặt tên `V<nn>-<mo-ta-khong-dau>.png`, mỗi mã một ảnh, ảnh phụ dùng hậu tố chữ (`V02b-…`).
3. Đối chiếu thêm ở tầng dữ liệu khi có thể: bản ghi SQLite (`status`, `error_code`, `page_count`), số point và payload trong Qdrant, file trong `data/uploads/`. Ghi lại ID cụ thể (`doc_id` rút gọn `2bebffb5…`).
4. Kiểm tra UI không có `stException` và không có chữ "Traceback".
5. Ghi ngay vào nháp: Thực tế, PASS/FAIL, ảnh. Đừng để tới cuối mới nhớ lại.

### 5. Viết report.md
Theo mẫu chuẩn ở [references/report-template.md](references/report-template.md). Mẫu này mở rộng §9 của test case với các phần: sai lệch, kết quả mong đợi tổng thể, ghi chú dữ liệu phát sinh. Riêng EV dùng bảng chấm theo câu của §9 trong file EV.

Quy tắc phán định, mức bug và cách đặt Bug ID: [references/report-conventions.md](references/report-conventions.md).

### 6. Tự kiểm tra rồi bàn giao
- Chạy `python .claude/skills/test-report-check/scripts/report_lint.py <ID>`, sửa cho tới khi hết `ERROR`.
- Mở xem lại ít nhất các ảnh của bước FAIL, xác nhận ảnh thể hiện đúng điều report mô tả.
- Báo người dùng: kết quả tổng, số bước PASS/FAIL, danh sách bug theo mức, sai lệch quan trọng, dữ liệu còn lại trong kho sau khi test, và link tới `test_reports/<ID>/report.md`.
