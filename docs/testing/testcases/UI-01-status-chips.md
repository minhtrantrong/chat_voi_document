# UI-01 — Chip trạng thái tài liệu (biểu tượng + nhãn)

| Mục | Giá trị |
|---|---|
| Test case | **UI-01** |
| Nguồn | Test plan mục 4.6.8 (UI-01) |
| Nhóm | UI |
| Chu kỳ | C3 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/UI-01/` |
| Truy vết | FR-05 · US-04/AC-04.1–4.3 · Tasks S-12, S-14 |

## 1. Mục tiêu

Chip trạng thái tài liệu đủ 3 giá trị (Đang xử lý / Sẵn sàng / Lỗi), mỗi chip luôn có **biểu tượng + nhãn chữ**; không phân biệt trạng thái chỉ bằng màu.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Kho trống trước khi bắt đầu.

## 3. Dữ liệu thử nghiệm

- `hop-dong.pdf` (A-01 — sẽ READY).
- `scan.pdf` (A-04 — sẽ Lỗi `PDF_NO_TEXT`).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Mở **http://localhost:8501/** khi kho trống | Không có chip nào | V01 |
| 2 | Upload `hop-dong.pdf`; chụp ngay lúc đang xử lý | Chip **Đang xử lý** có icon + nhãn chữ | V02 |
| 3 | Chờ xử lý xong | Chip **Sẵn sàng** có icon + nhãn chữ | V03 |
| 4 | Upload `scan.pdf` | Chip **Lỗi** có icon + nhãn lý do | V04 |
| 5 | Kiểm nhận diện trạng thái khi bỏ màu (DevTools grayscale filter hoặc tắt màu) | Vẫn phân biệt được 3 trạng thái nhờ icon + nhãn | V05 |

## 5. Kết quả mong đợi tổng thể

- Đủ 3 chip đúng nghĩa; mỗi chip có icon + nhãn; phân biệt được trạng thái khi không nhìn màu (tiêu chuẩn accessibility).

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/UI-01/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, trên khung hình thấy rõ URL **http://localhost:8501/** trên thanh địa chỉ. Lưu `./test_reports/UI-01/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx** (một mã = một ảnh), đặt tên `./test_reports/UI-01/screenshots/V01-....png`, …
4. Tạo `./test_reports/UI-01/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/UI-01/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-trong-cho.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/UI-01/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: FR-05 (chip trạng thái tài liệu).
- Vị trí trong test plan: mục 4.6.8 (UI-01); trạng thái chip được test chức năng tại ST-01, ST-02, ST-15.

## 9. Mẫu report.md (Agent điền vào ./test_reports/UI-01/report.md)

```markdown
# Test Report — UI-01: Chip trạng thái

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
