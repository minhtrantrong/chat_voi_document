# ST-13 — Upload PDF > 400 trang bị từ chối

| Mục | Giá trị |
|---|---|
| Test case | **ST-13** |
| Nguồn | Test plan mục 4.6.3 (biên 4.8.7) · checklist S-25 mục 4.8.7 |
| Nhóm | System/Manual (edge) |
| Chu kỳ | C2 |
| Ưu tiên | Medium |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/ST-13/` |
| Truy vết | BR-03 (`MAX_PAGES=400`), FR-02 · US-01/AC-01.2 · Task S-06 |

## 1. Mục tiêu

PDF vượt giới hạn 400 trang bị từ chối ngay khi kiểm tra metadata; không tạo bản ghi; không treo UI.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.

## 3. Dữ liệu thử nghiệm

- `long-401p.pdf` — khoảng 401 trang (fixture A-10).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Upload `long-401p.pdf` tại **http://localhost:8501/** | Bị từ chối với thông báo nêu tên file + giới hạn 400 trang + số trang thực tế | V01 |
| 2 | Kiểm tra danh sách tài liệu + `ls data/uploads/` | Không có row mới và không có file mới | V02 |
| 3 | Đo thời gian từ upload đến bị từ chối | < 5 giây; không treo UI | V03 |

## 5. Kết quả mong đợi tổng thể

- Từ chối nhanh (< 5 s), đúng lý do, không lưu bất kỳ dữ liệu nào.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/ST-13/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, khung hình phải thấy rõ **http://localhost:8501/** (và terminal nếu lẫn bước terminal). Lưu `./test_reports/ST-13/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/ST-13/screenshots/V01-....png`, …
4. Tạo `./test_reports/ST-13/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/ST-13/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-thong-bao-vuot-trang.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/ST-13/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: BR-03 (giới hạn 400 trang), FR-02.
- Vị trí trong test plan: mục 4.6.3 (biên 4.8.7) · checklist S-25 mục 4.8.7.
- Ghi số liệu đo thời gian dùng cho **PF-04**.

## 9. Mẫu report.md (Agent điền vào ./test_reports/ST-13/report.md)

```markdown
# Test Report — ST-13: Upload PDF > 400 trang bị từ chối

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
