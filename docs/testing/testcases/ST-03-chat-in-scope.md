# ST-03 — Chat trong phạm vi tài liệu

| Mục | Giá trị |
|---|---|
| Test case | **ST-03** |
| Nguồn | Test plan mục 4.6.3 (ST-03) · checklist S-25 mục 4.4 |
| Nhóm | System/Manual |
| Chu kỳ | C3 (sau milestone M3) |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/ST-03/` |
| Truy vết | FR-09, FR-11, FR-14, FR-15 · US-07/AC-07.1, US-08/AC-08.1, US-10/AC-10.1, US-14 · Tasks S-16…S-20 |

## 1. Mục tiêu

Câu hỏi có đáp án trong tài liệu được trả lời đúng nội dung, có đánh số [S1], hiển thị nguồn (tên file + trang), giữ ngữ cảnh hội thoại đa lượt, streaming hiển thị mượt.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Kho có ≥1 tài liệu **Sẵn sàng** (đã chạy ST-01).

## 3. Dữ liệu thử nghiệm

- `hop-dong.pdf` (A-01) — đã READY.
- Bộ câu hỏi trong phạm vi thuộc dataset EV-01, ví dụ: «Hạn chót nộp hồ sơ là ngày nào?», «Bên A là công ty nào?».

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Mở **http://localhost:8501/**; xác nhận chat input enabled | Ô hỏi hoạt động; chip **Sẵn sàng** hiển thị | V01 |
| 2 | Hỏi «Hạn chót nộp hồ sơ là ngày nào?» | Trả lời đúng ngày trong tài liệu (30/11/2026), có đánh số [S1], không bịa | V02 |
| 3 | Mở expander **Nguồn** của câu trả lời | Đúng `hop-dong.pdf` + số trang + đoạn trích | V03 |
| 4 | Hỏi tiếp «Bên A là công ty nào?» | Trả lời đúng dựa trên ngữ cảnh hội thoại đa lượt | V04 |
| 5 | Hỏi một câu dài, tiếng Việt nhiều dấu | Không lỗi encoding, không méo chữ | V05 |
| 6 | Quan sát streaming khi trả lời | Chữ hiện dần; không treo; không trống đột ngột | V06 |

## 5. Kết quả mong đợi tổng thể

- Trả lời đúng nội dung + có [S1] + nguồn đúng file/trang.
- Chat đa lượt giữ ngữ cảnh; tiếng Việt hiển thị đúng.
- Streaming ổn định, không treo.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/ST-03/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, không cắt giữa chừng, trên khung hình thấy rõ URL **http://localhost:8501/** trên thanh địa chỉ. Lưu `./test_reports/ST-03/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx** (một mã = một ảnh), đặt tên `./test_reports/ST-03/screenshots/V01-....png`, …
4. Tạo `./test_reports/ST-03/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link tương đối tới ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/ST-03/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-trang-ban-dau.png
    ├── V02-cau-tra-loi-1.png
    ├── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/ST-03/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: FR-09 (streaming), FR-11 (trích nguồn), FR-14 (mục nguồn), FR-15 (hội thoại đa lượt).
- Vị trí trong test plan: mục 4.6.3 (ST-03) · checklist S-25 mục 4.4.
- Bản ghi kết quả có thể dùng cho **EV-01** (chất lượng trong phạm vi).

## 9. Mẫu report.md (Agent điền vào ./test_reports/ST-03/report.md)

```markdown
# Test Report — ST-03: Chat trong phạm vi tài liệu

- **Agent / người test:** … · **Ngày:** …
- **Môi trường:** OS: … · Python: … · Qdrant image: … · LLM: … · Embedding: … · Browser: …
- **App URL:** http://localhost:8501/
- **Kết quả tổng:** PASS / FAIL

| # | Bước | Kỳ vọng | Thực tế | Kết quả | Ảnh |
|---|---|---|---|---|---|
| 1 | … | … | … | PASS | screenshots/V01-…png |

- **Video:** ./video.webm
- **Bug phát hiện:**

| Bug ID | Mô tả | Mức (S1–S4) | Ảnh |
|---|---|---|---|
```
