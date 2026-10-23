# ST-10 — Qdrant bật lại: hoạt động bình thường

| Mục | Giá trị |
|---|---|
| Test case | **ST-10** |
| Nguồn | Test plan mục 4.6.3 (biên 4.8.4) · checklist S-25 mục 4.8.4 |
| Nhóm | System/Manual (edge) |
| Chu kỳ | C3 |
| Ưu tiên | Medium |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/ST-10/` |
| Truy vết | NFR-03 · Task S-05 |

## 1. Mục tiêu

Sau khi bật lại Qdrant, app trở về trạng thái hoạt động bình thường mà không cần restart app.

## 2. Tiền điều kiện

1. Qdrant containers healthy — mở được `http://localhost:6333/dashboard` sau khi bật lại.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` đang chạy — mở được **http://localhost:8501/**.
4. Tiếp nối **ST-09** (Qdrant đang ở trạng thái dừng).

## 3. Dữ liệu thử nghiệm

- `hop-dong.pdf` (A-01) để upload sau khi phục hồi.

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Terminal: `docker compose start qdrant`, chờ healthy | Dashboard mở được; collection `document_chunks` nguyên vẹn | V01 |
| 2 | F5 trình duyệt tại **http://localhost:8501/** | App trở về trạng thái bình thường; không còn banner lỗi | V02 |
| 3 | Upload `hop-dong.pdf` | Chuyển chip **Sẵn sàng** bình thường | V03 |
| 4 | Hỏi 1 câu trong phạm vi | Trả lời + nguồn hoạt động trở lại | V04 |

## 5. Kết quả mong đợi tổng thể

- App tự khôi phục sau khi Qdrant online; không cần restart app; dữ liệu cũ nguyên vẹn.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/ST-10/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, không cắt giữa chừng, khung hình phải thấy rõ **http://localhost:8501/** và cửa sổ terminal khi chạy lệnh docker. Lưu `./test_reports/ST-10/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/ST-10/screenshots/V01-....png`, …
4. Tạo `./test_reports/ST-10/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/ST-10/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-qdrant-healthy.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/ST-10/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: NFR-03 (khôi phục sau lỗi Qdrant).
- Vị trí trong test plan: mục 4.6.3 (biên 4.8.4) · checklist S-25 mục 4.8.4.
- Tiếp nối: **ST-09**.

## 9. Mẫu report.md (Agent điền vào ./test_reports/ST-10/report.md)

```markdown
# Test Report — ST-10: Qdrant bật lại — hoạt động bình thường

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
