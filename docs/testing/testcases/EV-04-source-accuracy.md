# EV-04 — Eval nguồn đúng tài liệu/trang (mục tiêu ≥ 9/10 tức ≥ 90%)

| Mục | Giá trị |
|---|---|
| Test case | **EV-04** |
| Nguồn | Test plan mục 4.6.5 (EV-04) · bộ eval 30 câu mục 6-B, hàng «Nguồn» |
| Nhóm | Eval RAG |
| Chu kỳ | C3 → lặp lại C4 (chạy sau EV-01…EV-03) |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/EV-04/` |
| Truy vết | QLT-04, FR-14 · US-10/AC-10.2 · Tasks S-20, S-24 |

## 1. Mục tiêu

Trên toàn bộ các câu trả lời có nguồn từ EV-01…EV-03 (30 câu): đối chiếu từng nguồn (tên file + trang) với PDF gốc; mục tiêu ≥ 90% nguồn đúng file, đúng trang, nội dung khớp.

## 2. Tiền điều kiện

1. Đã hoàn thành **EV-01, EV-02, EV-03** (có 30 lượt hỏi + phản hồi + nguồn).
2. PDF gốc A-01…A-03 mở bên cạnh để đối chiếu.
3. Kết quả EV-01…EV-03 có sẵn (bảng chấm + screenshot) — tái sử dụng, không cần hỏi lại (trừ câu thiếu nguồn).

## 3. Dữ liệu thử nghiệm

- Dữ liệu đánh giá từ EV-01…EV-03.
- PDF gốc A-01…A-03.

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Tập hợp tất cả nguồn từ 3 lần eval (30 câu) | Danh sách nguồn đầy đủ | V01 |
| 2 | Với mỗi nguồn: mở PDF gốc ở trang được nêu; tìm đoạn thông tin | Đối chiếu từng nguồn | V02 |
| 3 | Chấm mỗi nguồn: đúng file? đúng trang? nội dung khớp? | Kết quả từng nguồn | V03 |
| 4 | Tổng hợp X/30 đúng | Tỷ lệ được tính | V04 |
| 5 | Đối chiếu ngưỡng QLT-04 (≥ 90%) | PASS nếu đạt; nguồn đúng file/trang nhưng nội dung không khớp trang cũng tính FAIL cho câu đó | V05 |

## 5. Kết quả mong đợi tổng thể

- ≥ 90% nguồn đúng file + trang; các case sai được liệt kê cụ thể.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/EV-04/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, khung hình thể hiện việc mở PDF gốc để đối chiếu nguồn (kèm **http://localhost:8501/** khi cần xem lại nguồn). Lưu `./test_reports/EV-04/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho các nguồn được kiểm (ít nhất 10 ảnh: nguồn trong app + trang PDF gốc đối chiếu)**, đặt tên `./test_reports/EV-04/screenshots/V02-nguon-01.png`, …
4. Tạo `./test_reports/EV-04/report.md` theo mẫu mục 9: bảng kết quả từng nguồn, tỷ lệ, ngưỡng QLT-04, phần ghi môi trường; link ảnh + video.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/EV-04/
├── video.webm
├── report.md
├── scoring.md
└── screenshots/
    ├── V02-nguon-01.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: ≥ 90% nguồn đúng file + trang; đủ report + ảnh + video trong `./test_reports/EV-04/`.
- **FAIL** khi: < 90% nguồn đúng, hoặc thiếu artifact. Nguồn sai được liệt cụ thể câu + trang thực tế trong report.

## 8. Truy vết

- Yêu cầu: QLT-04 (nguồn chính xác), FR-14.
- Vị trí trong test plan: mục 4.6.5 (EV-04) · bộ eval mục 6-B.
- Phụ thuộc: EV-01, EV-02, EV-03.

## 9. Mẫu report.md (Agent điền vào ./test_reports/EV-04/report.md)

```markdown
# Test Report — EV-04: Kiểm tra nguồn tài liệu/trang

- **Agent / người test:** … · **Ngày:** …
- **Môi trường:** OS: … · Python: … · Qdrant image: … · LLM: … · Embedding: … · Browser: …
- **App URL:** http://localhost:8501/
- **Kết quả tổng:** PASS / FAIL (X/30 nguồn đúng; ngưỡng ≥ 90%)

| # | Câu | Nguồn trong app | Đúng file? | Đúng trang? | Nội dung khớp? | Ảnh |
|---|---|---|---|---|---|---|
| 1 | … | hop-dong.pdf, trang 12 | Có | Có | Có | screenshots/V02-nguon-01.png |

- **Video:** ./video.webm
- **Bug phát hiện:**

| Bug ID | Mô tả | Mức (S1–S4) | Ảnh |
|---|---|---|---|
```
