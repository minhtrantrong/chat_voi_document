# ST-02 — Upload nhiều PDF + file lỗi + trùng tên

| Mục | Giá trị |
|---|---|
| Test case | **ST-02** |
| Nguồn | Test plan mục 4.6.3 (ST-02) · checklist S-25 mục 4.3 |
| Nhóm | System/Manual |
| Chu kỳ | C2 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/ST-02/` |
| Truy vết | FR-03, FR-04 · US-02/AC-02.2, US-03/AC-03.1 · Tasks S-13, S-14 |

## 1. Mục tiêu

Upload cùng lúc nhiều file có trộn file lỗi: file lỗi bị chặn đúng lý do, không chặn file hợp lệ còn lại; tải lại file trùng tên tạo bản ghi mới (không dedupe — đúng thiết kế).

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.

## 3. Dữ liệu thử nghiệm

- `hop-dong.pdf`, `bao-gia.pdf` — hợp lệ (A-01, A-02).
- `fake.docx` — sai định dạng (đuôi .docx).
- `scan.pdf` — PDF chỉ ảnh, không text layer (A-04).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Mở **http://localhost:8501/** với kho trống | Trang render bình thường | V01 |
| 2 | Chọn đồng thời `hop-dong.pdf` + `bao-gia.pdf` + `fake.docx` | `fake.docx` bị chặn với thông báo «chỉ hỗ trợ PDF» nêu tên file; 2 PDF tiếp tục xử lý | V02 |
| 3 | Chọn thêm `scan.pdf` | Row riêng trạng thái **Lỗi** — mã `PDF_NO_TEXT` | V03 |
| 4 | Bấm Xoá file lỗi | File lỗi biến mất khỏi danh sách | V04 |
| 5 | Tải lại `hop-dong.pdf` lần 2 (trùng tên) | Tạo bản ghi thứ hai cho hop-dong.pdf (không dedupe) | V05 |
| 6 | Xem lại tổng thể danh sách | 2 bản hop-dong + 1 bản bao-gia đều **Sẵn sàng** | V06 |

## 5. Kết quả mong đợi tổng thể

- File lỗi không chặn các file hợp lệ trong cùng một lô.
- Thông báo lỗi nêu tên file + lý do.
- Re-upload trùng tên tạo bản ghi mới (thiết kế chấp nhận).

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/ST-02/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, không cắt giữa chừng, trên khung hình thấy rõ URL **http://localhost:8501/** trên thanh địa chỉ. Lưu `./test_reports/ST-02/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx** (một mã = một ảnh), đặt tên `./test_reports/ST-02/screenshots/V01-....png`, …
4. Tạo `./test_reports/ST-02/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link tương đối tới ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/ST-02/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-trang-ban-dau.png
    ├── V02-thong-bao-file-sai.png
    ├── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/ST-02/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: FR-03 (báo lỗi file), FR-04 (hỗ trợ nhiều file), FR-08 (cho phép trùng tên).
- Vị trí trong test plan: mục 4.6.3 (ST-02) · checklist S-25 mục 4.3.

## 9. Mẫu report.md (Agent điền vào ./test_reports/ST-02/report.md)

```markdown
# Test Report — ST-02: Upload nhiều PDF + file lỗi + trùng tên

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
