# PF-03 — Độ trễ tìm kiếm Qdrant

| Mục | Giá trị |
|---|---|
| Test case | **PF-03** |
| Nguồn | Test plan mục 4.6.6 (PF-03) |
| Nhóm | Performance |
| Chu kỳ | C3 |
| Ưu tiên | Medium |
| URL ứng dụng | **http://localhost:8501/** (App chat dùng chung theo dõi total; đo detail Qdrant phía bên dưới) |
| Thư mục artifact | `./test_reports/PF-03/` |
| Truy vết | BR-07 (`TOP_K=8`, `SCORE_THRESHOLD=0.25`) · Tasks S-05, S-15 |

## 1. Mục tiêu

Đo độ trễ của khối search Qdrant (không tính thời gian LLM) ở quy mô demo: p90 < 1 s cho mỗi truy vấn.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/**.
4. Kho có ≥2 docs **Sẵn sàng**; points đầy đủ.
5. Chuẩn bị script/curl để: (a) embed câu hỏi bằng chính embedding endpoint, (b) gọi API search Qdrant.

## 3. Dữ liệu thử nghiệm

- 5 câu hỏi trong phạm vi (dataset EV-01).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Embed câu hỏi bằng embedding endpoint (script/curl) | Vector câu hỏi sẵn sàng | V01 |
| 2 | Gọi `POST http://localhost:6333/collections/document_chunks/points/search`, `limit=8`, `score_threshold=0.25` | Response có kết quả | V02 |
| 3 | Đo thời gian mỗi call (curl `time_total`); 5 câu × 2 lần | 10 datapoint độ trễ | V03 |
| 4 | Tính trung bình/p90 | Ghi số liệu vào report | V04 |
| 5 | Hỏi 1 câu trong UI tại **http://localhost:8501/** để so sánh độ trễ tổng (bao gồm cả LLM) như tham chiếu | App hoạt động bình thường | V05 |

## 5. Kết quả mong đợi tổng thể

- 10 datapoint độ trễ được ghi rõ; p90 < 1 s (nếu không đạt: ghi outlier + nguyên nhân).

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/PF-03/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, khung hình phải thấy rõ terminal (curl) và **http://localhost:8501/** (bước 5). Lưu `./test_reports/PF-03/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx** (gồm ảnh terminal/DevTools), đặt tên `./test_reports/PF-03/screenshots/V01-....png`, …
4. Tạo `./test_reports/PF-03/report.md` theo mẫu mục 9: điền bảng 10 datapoint độ trễ, p50/p90, phần ghi môi trường; link ảnh + video.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/PF-03/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-embed-query.png
    └── ...
    ├── V05-app-tham-chieu.png
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: 10 datapoint đủ + p90 < 1 s; report + ảnh + video đầy đủ trong `./test_reports/PF-03/`.
- **FAIL** khi: đo không đủ datapoint, p90 ≥ 1 s không được ghi outlier + nguyên nhân, hoặc thiếu artifact.

## 8. Truy vết

- Yêu cầu: BR-07 (tham số search), NFR quy mô demo.
- Vị trí trong test plan: mục 4.6.6 (PF-03).

## 9. Mẫu report.md (Agent điền vào ./test_reports/PF-03/report.md)

```markdown
# Test Report — PF-03: Độ trễ tìm kiếm Qdrant

- **Agent / người test:** … · **Ngày:** …
- **Môi trường:** OS: … · Python: … · Qdrant image: … · LLM: … · Embedding: … · Browser: …
- **App URL:** http://localhost:8501/
- **Kết quả tổng:** PASS / FAIL

| # | Câu hỏi | Độ trễ (s) | Ảnh |
|---|---|---|---|
| 1 | … | … | screenshots/V03-…png |
| … | | | |

**p50:** … s · **p90:** … s · **Ngưỡng:** p90 < 1 s

- **Video:** ./video.webm
- **Bug phát hiện:**

| Bug ID | Mô tả | Mức (S1–S4) | Ảnh |
|---|---|---|---|
```
