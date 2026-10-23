# ST-15 — Upload PDF scan (không text) bị từ chối

| Mục | Giá trị |
|---|---|
| Test case | **ST-15** |
| Nguồn | Test plan mục 4.6.3 (biên 4.8.9) · checklist S-25 mục 4.8.9 |
| Nhóm | System/Manual (edge) |
| Chu kỳ | C2 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/ST-15/` |
| Truy vết | BR-05 (`PDF_NO_TEXT`), FR-03 · US-03/AC-03.3 · Tasks S-07, S-11 |

## 1. Mục tiêu

PDF chỉ có ảnh (không text layer) nhận lỗi `PDF_NO_TEXT` với thông báo thân thiện; không bao giờ READY; giao diện không bị ảnh hưởng.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.

## 3. Dữ liệu thử nghiệm

- `scan.pdf` — PDF chỉ ảnh (fixture A-04).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Upload `scan.pdf` tại **http://localhost:8501/** | Row **Lỗi** + thông báo «không có văn bản trích xuất được (PDF dạng ảnh scan chưa được hỗ trợ)» | V01 |
| 2 | Chờ xử lý hoàn tất | Không chuyển READY; không point trong Qdrant dashboard | V02 |
| 3 | Xoá file lỗi bằng nút Xoá | Biến mất khỏi danh sách; app vẫn hoạt động bình thường | V03 |

## 5. Kết quả mong đợi tổng thể

- Báo lỗi đúng vì PDF scan (chưa có OCR); không READY; không index; xoá file lỗi sạch.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/ST-15/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, khung hình phải thấy rõ **http://localhost:8501/**. Lưu `./test_reports/ST-15/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/ST-15/screenshots/V01-....png`, …
4. Tạo `./test_reports/ST-15/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/ST-15/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-thong-bao-pdf-scan.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/ST-15/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: BR-05 (PDF_NO_TEXT), FR-03, FR-08 (xoá tài liệu lỗi).
- Vị trí trong test plan: mục 4.6.3 (biên 4.8.9) · checklist S-25 mục 4.8.9.

## 9. Mẫu report.md (Agent điền vào ./test_reports/ST-15/report.md)

```markdown
# Test Report — ST-15: Upload PDF scan bị từ chối

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
