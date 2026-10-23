# PF-02 — p50/p90 từ gửi câu hỏi đến chữ đầu tiên

| Mục | Giá trị |
|---|---|
| Test case | **PF-02** |
| Nguồn | Test plan mục 4.6.6 (PF-02) |
| Nhóm | Performance |
| Chu kỳ | C3 |
| Ưu tiên | Medium |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/PF-02/` |
| Truy vết | FR-09 · OQ-011 (đề xuất QA: p90 ≤ 10 s cho model local) · Task S-16 |

## 1. Mục tiêu

Đo p50/p90 thời gian từ khi gửi câu hỏi đến ký tự đầu tiên hiển thị trên UI; ghi baseline vào report.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Kho có ≥1 doc **Sẵn sàng**.

## 3. Dữ liệu thử nghiệm

- `hop-dong.pdf` (A-01) đã READY.
- 10 câu hỏi trong phạm vi (dataset EV-01).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Chuẩn bị bảng đo trong report: câu • t gửi • t chữ đầu • Δ | Bảng sẵn sàng | V01 |
| 2 | Gửi tuần tự 10 câu tại **http://localhost:8501/**; đo bằng đồng hồ/timestamp của DevTools Network; mỗi câu chụp một ảnh | 10 datapoint đầy đủ | V02–V11 |
| 3 | Từ bảng, tính p50/p90 | p50/p90 được tính, ghi vào report | V12 |
| 4 | Đối chiếu với ngưỡng (nếu OQ-011 đã chốt; nếu chưa, ghi giá trị tham khảo đề xuất p90 ≤ 10 s) | Ghi PASS/FAIL hoặc ghi «chờ chốt ngưỡng» | V13 |

## 5. Kết quả mong đợi tổng thể

- 10 datapoint có bằng chứng; p50/p90 được tính và ghi rõ trong report.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/PF-02/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, khung hình phải thấy rõ **http://localhost:8501/** và đồng hồ/timestamp khi đo. Lưu `./test_reports/PF-02/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi câu (10 ảnh, V02…V11) + 1 ảnh kết quả tính p50/p90**, đặt tên `./test_reports/PF-02/screenshots/V02-cau-01.png`, …
4. Tạo `./test_reports/PF-02/report.md` theo mẫu mục 9: điền bảng đo thời gian, p50/p90, ngưỡng đối chiếu, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/PF-02/
├── video.webm
├── report.md
└── screenshots/
    ├── V02-cau-01.png
    ├── V03-cau-02.png
    ├── ...
    └── V13-p50-p90.png
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi datapoint có bằng chứng; p50/p90 được tính; đủ `report.md` + ảnh + video trong `./test_reports/PF-02/`.
- **FAIL** khi: datapoint thiếu, không tính được p50/p90, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng.

## 8. Truy vết

- Yêu cầu: FR-09 (streaming), OQ-011.
- Vị trí trong test plan: mục 4.6.6 (PF-02).

## 9. Mẫu report.md (Agent điền vào ./test_reports/PF-02/report.md)

```markdown
# Test Report — PF-02: p50/p90 thời gian chữ đầu tiên

- **Agent / người test:** … · **Ngày:** …
- **Môi trường:** OS: … · Python: … · Qdrant image: … · LLM: … · Embedding: … · Browser: …
- **App URL:** http://localhost:8501/
- **Kết quả tổng:** PASS / FAIL

| Câu | t gửi | t chữ đầu | Δ (s) | Ảnh |
|---|---|---|---|---|
| 1 | … | … | … | screenshots/V02-cau-01.png |
| … | | | | |

**p50:** … s · **p90:** … s · **Ngưỡng:** … (OQ-011)
**Video:** ./video.webm
- **Bug phát hiện:**

| Bug ID | Mô tả | Mức (S1–S4) | Ảnh |
|---|---|---|---|
```
