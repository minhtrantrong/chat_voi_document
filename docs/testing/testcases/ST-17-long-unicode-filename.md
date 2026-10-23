# ST-17 — Tên file dài/Unicode không vỡ layout

| Mục | Giá trị |
|---|---|
| Test case | **ST-17** |
| Nguồn | Test plan mục 4.6.3 (biên 4.8.11) · checklist S-25 mục 4.8.11 |
| Nhóm | System/Manual (edge) |
| Chu kỳ | C2 |
| Ưu tiên | Medium |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/ST-17/` |
| Truy vết | NFR-07, SEC-03 · Tasks S-07, S-12 |

## 1. Mục tiêu

Tên file dài (>150 ký tự) và có dấu/Unicode vẫn upload thành công, hiển thị gọn (truncate hợp lý), không vỡ layout, không gây lỗi.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.

## 3. Dữ liệu thử nghiệm

- PDF có tên dài >150 ký tự, chứa tiếng Việt có dấu và ký tự Unicode đặc biệt (ví dụ `üñî`).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Upload tên file dài + Unicode tại **http://localhost:8501/** | Upload thành công; hiển thị truncate an toàn; không vỡ layout | V01 |
| 2 | Hỏi 1 câu có nguồn từ file này | Nguồn hiển thị tên dài chính xác (escape đúng, chữ có dấu hiển thị đúng) | V02 |
| 3 | Xoá file này | Xoá được; chỉ đúng file này biến mất; app không lỗi | V03 |

## 5. Kết quả mong đợi tổng thể

- Tên dài/Unicode hiển thị an toàn: không vỡ layout, không XSS, không lỗi quy trình xoá.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/ST-17/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, trên khung hình thấy rõ URL **http://localhost:8501/** trên thanh địa chỉ. Lưu `./test_reports/ST-17/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/ST-17/screenshots/V01-....png`, …
4. Tạo `./test_reports/ST-17/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/ST-17/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-row-ten-dai.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/ST-17/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: NFR-07 (tên file dài/Unicode), SEC-03 (escape).
- Vị trí trong test plan: mục 4.6.3 (biên 4.8.11) · checklist S-25 mục 4.8.11.
- Test chi tiết layout xem thêm **UI-06**; chi tiết XSS xem **SEC-03**.

## 9. Mẫu report.md (Agent điền vào ./test_reports/ST-17/report.md)

```markdown
# Test Report — ST-17: Tên file dài/Unicode

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
