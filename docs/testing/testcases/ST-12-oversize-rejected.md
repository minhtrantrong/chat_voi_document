# ST-12 — Upload file > 25 MB bị từ chối

| Mục | Giá trị |
|---|---|
| Test case | **ST-12** |
| Nguồn | Test plan mục 4.6.3 (biên 4.8.6) · checklist S-25 mục 4.8.6 |
| Nhóm | System/Manual (edge) |
| Chu kỳ | C2 |
| Ưu tiên | Medium |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/ST-12/` |
| Truy vết | BR-02 (`MAX_UPLOAD_MB=25`), FR-02 · US-01/AC-01.2 · Task S-06 |

## 1. Mục tiêu

File vượt giới hạn 25 MB bị từ chối ngay tại biên với thông báo đủ thông tin; không lưu file/bản ghi; không treo UI.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.

## 3. Dữ liệu thử nghiệm

- `big-25mb.pdf` — khoảng 25,1 MB (fixture A-09).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Upload `big-25mb.pdf` tại **http://localhost:8501/** | Bị từ chối với thông báo nêu tên file + giới hạn 25 MB + dung lượng thực tế | V01 |
| 2 | Kiểm tra danh sách tài liệu | Không tạo row/bản ghi mới | V02 |
| 3 | Terminal: `ls -l data/uploads/` | Không có file mới của lần upload này | V03 |
| 4 | Đo thời gian từ upload đến thông báo từ chối | < 5 giây; không treo UI | V04 |

## 5. Kết quả mong đợi tổng thể

- Từ chối nhanh (< 5 s), thông báo đủ thông tin, không ghi file hay bản ghi nào.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/ST-12/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, khung hình phải thấy rõ **http://localhost:8501/** (và terminal ở bước 3). Lưu `./test_reports/ST-12/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/ST-12/screenshots/V01-....png`, …
4. Tạo `./test_reports/ST-12/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/ST-12/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-thong-bao-vuot-dung-luong.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/ST-12/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: BR-02 (giới hạn 25 MB), FR-02 (từ chối biên).
- Vị trí trong test plan: mục 4.6.3 (biên 4.8.6) · checklist S-25 mục 4.8.6.
- Ghi số liệu đo thời gian dùng cho **PF-04**.

## 9. Mẫu report.md (Agent điền vào ./test_reports/ST-12/report.md)

```markdown
# Test Report — ST-12: Upload file > 25 MB bị từ chối

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
