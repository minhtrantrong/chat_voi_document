# ST-05 — Chat tổng hợp đa tài liệu

| Mục | Giá trị |
|---|---|
| Test case | **ST-05** |
| Nguồn | Test plan mục 4.6.3 (ST-05) · checklist S-25 mục 4.6 |
| Nhóm | System/Manual |
| Chu kỳ | C3 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/ST-05/` |
| Truy vết | FR-13, FR-14 · US-09/AC-09.1 · Tasks S-15, S-21 |

## 1. Mục tiêu

Câu hỏi cần thông tin từ ≥2 tài liệu được trả lời tổng hợp đầy đủ, nguồn từ cả hai tài liệu; không một tài liệu nào chiếm hết toàn bộ nguồn.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. `hop-dong.pdf` đã READY (từ ST-01).

## 3. Dữ liệu thử nghiệm

- `bao-gia.pdf` (A-02), `quy-dinh.pdf` (A-03).
- Câu hỏi đa tài liệu từ dataset EV-02 (ví dụ: so sánh điều khoản trong hop-dong với nội dung bao-gia).
- Câu hỏi đơn phạm vi cho `quy-dinh.pdf` (từ dataset EV-01).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Upload `bao-gia.pdf` + `quy-dinh.pdf` tại **http://localhost:8501/** | Cả hai chuyển **Sẵn sàng** | V01 |
| 2 | Hỏi câu cần cả hai tài liệu (so sánh nội dung) | Trả lời tổng hợp; nguồn bao gồm cả hai tên file | V02 |
| 3 | Mở expander **Nguồn** | ≥2 tài liệu khác nhau, mỗi mục nêu tên file + trang + đoạn trích | V03 |
| 4 | Hỏi câu chỉ liên quan `quy-dinh.pdf` | Nguồn đúng file duy nhất, không lẫn file khác | V04 |
| 5 | Đếm mục nguồn theo file | Không tài liệu nào trên 4 mục (giới hạn `MAX_CHUNKS_PER_DOC=4`) | V05 |

## 5. Kết quả mong đợi tổng thể

- Trả lời tổng hợp đúng nội dung từ cả hai tài liệu.
- Nguồn đủ ≥2 file, đa dạng, không tài liệu nào chiếm hết context.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/ST-05/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, không cắt giữa chừng, trên khung hình thấy rõ URL **http://localhost:8501/** trên thanh địa chỉ. Lưu `./test_reports/ST-05/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/ST-05/screenshots/V01-....png`, …
4. Tạo `./test_reports/ST-05/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/ST-05/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-danh-sach-3-doc.png
    ├── V02-cau-tra-loi-da-tai-lieu.png
    ├── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/ST-05/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: FR-13 (chat đa tài liệu), FR-14 (hiển thị nguồn).
- Vị trí trong test plan: mục 4.6.3 (ST-05) · checklist S-25 mục 4.6.
- Bản ghi kết quả có thể dùng cho **EV-02** (tổng hợp đa tài liệu).

## 9. Mẫu report.md (Agent điền vào ./test_reports/ST-05/report.md)

```markdown
# Test Report — ST-05: Chat tổng hợp đa tài liệu

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
