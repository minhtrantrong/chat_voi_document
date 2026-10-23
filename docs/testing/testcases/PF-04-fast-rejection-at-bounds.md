# PF-04 — Từ chối nhanh tại biên (25,1 MB / 401 trang)

| Mục | Giá trị |
|---|---|
| Test case | **PF-04** |
| Nguồn | Test plan mục 4.6.6 (PF-04) |
| Nhóm | Performance |
| Chu kỳ | C3 |
| Ưu tiên | Medium |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/PF-04/` |
| Truy vết | FR-02 · Task S-06 |

## 1. Mục tiêu

File vượt biên (quá 25 MB, quá 400 trang) bị từ chối **trước khi xử lý**, trong ≤ 5 giây; không treo UI; không ghi dữ liệu.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Chuẩn bị đồng hồ/bấm giờ.

## 3. Dữ liệu thử nghiệm

- `big-25mb.pdf` — ~25,1 MB (A-09).
- `long-401p.pdf` — ~401 trang (A-10).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Bấm giờ; upload `big-25mb.pdf` tại **http://localhost:8501/**; dừng đồng hồ khi thông báo xuất hiện | Từ chối ≤ 5 giây; không treo UI | V01 |
| 2 | Bấm giờ; upload `long-401p.pdf`; dừng khi bị từ chối | Từ chối ≤ 5 giây | V02 |
| 3 | Terminal: `ls -l data/uploads/` + kiểm danh sách | Không có file/row mới nào | V03 |
| 4 | Tổng hợp 2 lần đo vào report | Bảng biên dung lượng/trang với thời gian rõ ràng | V04 |

## 5. Kết quả mong đợi tổng thể

- Cả hai trường hợp biên sẽ từ chối nhanh (≤ 5 s), không ghi dữ liệu.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/PF-04/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, khung hình phải thấy rõ **http://localhost:8501/** và đồng hồ/đo thời gian. Lưu `./test_reports/PF-04/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/PF-04/screenshots/V01-....png`, …
4. Tạo `./test_reports/PF-04/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, bảng số liệu đo, link ảnh + video, bảng bug nếu có.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/PF-04/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-hop-bien-dung-luong.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/PF-04/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: FR-02 (kiểm tra biên trước khi xử lý).
- Vị trí trong test plan: mục 4.6.6 (PF-04); test chức năng chi tiết tại ST-12, ST-13.

## 9. Mẫu report.md (Agent điền vào ./test_reports/PF-04/report.md)

```markdown
# Test Report — PF-04: Từ chối nhanh tại biên

- **Agent / người test:** … · **Ngày:** …
- **Môi trường:** OS: … · Python: … · Qdrant image: … · LLM: … · Embedding: … · Browser: …
- **App URL:** http://localhost:8501/
- **Kết quả tổng:** PASS / FAIL

| Biên | Thời gian từ chối (s) | ≤ 5 s? | Ảnh |
|---|---|---|---|
| 25,1 MB | … | … | screenshots/V01-…png |
| 401 trang | … | … | screenshots/V02-…png |

- **Video:** ./video.webm
- **Bug phát hiện:**

| Bug ID | Mô tả | Mức (S1–S4) | Ảnh |
|---|---|---|---|
```
