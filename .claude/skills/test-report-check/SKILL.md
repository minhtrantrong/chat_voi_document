---
name: test-report-check
description: Kiểm tra chất lượng test report trong test_reports/<ID>/ — đủ artifact (report.md, video, ảnh cho mọi mã Vxx), link không hỏng, kết quả tổng khớp từng bước, bảng bug đúng định dạng S1–S4, và nội dung có căn cứ từ ảnh. Dùng khi người dùng nói "kiểm tra report ST-02", "review test report", "report đã đủ chưa", hoặc trước khi tổng hợp cycle.
---

# test-report-check — Rà soát test report

Đầu vào: một hoặc nhiều mã case (`ST-01 ST-02`), hoặc không truyền gì để kiểm tra toàn bộ `test_reports/`.
Đầu ra: danh sách phát hiện theo case, chia ERROR / WARN / NỘI DUNG, kèm đề xuất sửa. Chỉ sửa report khi người dùng đồng ý, và không bao giờ sửa code app.

## Bước 1 — Kiểm tra máy

```bash
python .claude/skills/test-report-check/scripts/report_lint.py <ID…>      # hoặc --all
```

Script kiểm tra:
- Có `report.md`, `video.webm|mp4`, `screenshots/`.
- Mỗi mã Vxx trong bảng bước của test case (`docs/testing/testcases/<ID>-*.md`, kể cả dải `V03–V12`) đều có ảnh `Vxx-*.png`.
- Mọi link tương đối trong report trỏ tới file có thật.
- `**Kết quả tổng:**` đã điền và bắt đầu bằng PASS/FAIL/BLOCKED. Nếu tổng là PASS mà có bước FAIL thì báo lỗi (trừ EV, vì EV xét theo ngưỡng).
- Bảng bug: mọi dòng có mức S1–S4, có ảnh, ID theo dạng `BUG-/OBS-<CASE>-NN`.
- Tên ảnh theo mẫu, dòng Môi trường và Ngày đã điền.

## Bước 2 — Kiểm tra nội dung (script không làm được)

Đọc `report.md` song song với file test case, lần lượt từng mục:

1. **Độ phủ bước**: report có đủ mọi bước của §4 test case không, có bước nào bị gộp hay bỏ sót không.
2. **Thực tế có căn cứ**: cột Thực tế phải là quan sát cụ thể (chữ UI, giá trị DB/Qdrant, ID), không chép lại câu Kỳ vọng. Các câu kiểu "Hoạt động bình thường", "Như kỳ vọng" là dấu hiệu chưa quan sát thật.
3. **Ảnh khớp lời**: dùng Read mở ảnh của mọi bước FAIL và ít nhất 2 bước PASS chọn ngẫu nhiên. Ảnh phải thể hiện đúng điều cột Thực tế mô tả và thấy được URL hoặc nhãn URL.
4. **Phán định hợp lý**: PASS/FAIL theo quy tắc ở [../test-report-run/references/report-conventions.md](../test-report-run/references/report-conventions.md). Bước sai tiền điều kiện phải là FAIL hoặc BLOCKED có lý do, không được là PASS. Phải phân biệt "app sai" với "dữ liệu test sai".
5. **Mức bug hợp lý**: đối chiếu bảng S1–S4 trong conventions. Đặc biệt chú ý bug bị hạ mức: lộ key/stack trace, mất dữ liệu, trả lời không có nguồn thì không thể là S3/S4.
6. **Bug trùng giữa các case**: bug đã có ở case khác phải dùng lại ID cũ, ghi "(lặp lại)". Khi kiểm tra nhiều case, gom các mô tả giống nhau lại để phát hiện.
7. **Sai lệch được khai báo**: mọi mô phỏng thao tác, nhãn URL, zoom, fixture tự tạo, dữ liệu kho không trống phải nằm trong bảng sai lệch.
8. **EV/PF**: EV có tỷ lệ X/N + ngưỡng QLT + nguồn từng câu + phân tích câu sai. PF có số đo, cách đo, phần cứng.

## Bước 3 — Báo cáo

Trình bày ngắn gọn theo từng case:

```
ST-02 — FAIL · 4/6 bước PASS · 4 bug (S3×2, S4×2)
  ERROR  …(từ script)
  WARN   …
  NỘI DUNG  Bước 4: ảnh V04 không thấy banner lỗi mà report nhắc tới …
  → Đề xuất: …
```

Cuối cùng đưa ra kết luận: report nào đủ điều kiện đưa vào summary cycle, report nào cần sửa hoặc chạy lại.
Nếu người dùng đồng ý sửa: chỉ sửa phần trình bày (link, định dạng, mức bug có giải thích). Muốn đổi phán định PASS/FAIL hoặc nội dung Thực tế thì phải có bằng chứng và người dùng xác nhận. Thiếu ảnh hoặc video thì không dựng lại được, phải đề xuất chạy lại bằng `test-report-run`.
