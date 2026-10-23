# PF-01 — Thời gian ingest đến READY

| Mục | Giá trị |
|---|---|
| Test case | **PF-01** |
| Nguồn | Test plan mục 4.6.6 (PF-01) |
| Nhóm | Performance |
| Chu kỳ | C3 |
| Ưu tiên | Medium |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/PF-01/` |
| Truy vết | NFR-06 · Tasks S-09, S-11 |

## 1. Mục tiêu

Đo và ghi nhận thời gian từ upload đến chip **Sẵn sàng** cho các PDF kích thước khác nhau; không timeout; tạo baseline ghi trong report (KPI cuối sẽ chốt ở cycle C2).

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Đảm bảo đồng bộ đo thời gian: chuẩn bị đồng hồ/bấm giờ + DevTools Network (trace upload request).

## 3. Dữ liệu thử nghiệm

- `bao-gia.pdf` — 12 trang (A-02).
- `hop-dong.pdf` — 32 trang (A-01).
- PDF ~100 trang (tự tạo, hoặc tạo bằng cách gộp nội dung từ A-01).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Chuẩn bị bảng đo trong report: cỡ PDF | t0 → READY | V01 |
| 2 | Upload `bao-gia.pdf` tại **http://localhost:8501/**; bấm giờ; đo t0 → chip **Sẵn sàng** | Hoàn tất; ghi số liệu vào bảng | V02 |
| 3 | Upload `hop-dong.pdf`; đo t0 → READY | Hoàn tất; ghi số liệu | V03 |
| 4 | Upload PDF ~100 trang; đo t0 → READY | Hoàn tất, không timeout; ghi số liệu | V04 |
| 5 | Tổng hợp baseline vào report | Bảng t0 → READY theo 3 cỡ PDF | V05 |

## 5. Kết quả mong đợi tổng thể

- Cả 3 kịch bản hoàn tất, không timeout.
- Bảng baseline được ghi chi tiết trong report (KPI cuối chốt sau cycle C2 theo OQ-011).

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/PF-01/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, trên khung hình phải thấy rõ **http://localhost:8501/** và số liệu đo thời gian. Lưu `./test_reports/PF-01/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx** (đồng hồ/bấm giờ + trạng thái chip), đặt tên `./test_reports/PF-01/screenshots/V01-....png`, …
4. Tạo `./test_reports/PF-01/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng baseline t0 → READY, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/PF-01/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-bang-do.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/PF-01/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: NFR-06 (baseline thời gian index).
- Vị trí trong test plan: mục 4.6.6 (PF-01).

## 9. Mẫu report.md (Agent điền vào ./test_reports/PF-01/report.md)

```markdown
# Test Report — PF-01: Thời gian ingest đến READY

- **Agent / người test:** … · **Ngày:** …
- **Môi trường:** OS: … · Python: … · Qdrant image: … · LLM: … · Embedding: … · Browser: …
- **App URL:** http://localhost:8501/
- **Kết quả tổng:** PASS / FAIL

| Cỡ PDF | t0 → READY (s) | PASS/FAIL | Ảnh |
|---|---|---|---|
| 12 trang | … | … | … |
| 32 trang | … | … | … |
| ~100 trang | … | … | … |

| # | Bước | Kỳ vọng | Thực tế | Kết quả | Ảnh |
|---|---|---|---|---|---|
| 1 | … | … | … | PASS | screenshots/V01-…png |

- **Video:** ./video.webm
- **Bug phát hiện:**

| Bug ID | Mô tả | Mức (S1–S4) | Ảnh |
|---|---|---|---|
```
