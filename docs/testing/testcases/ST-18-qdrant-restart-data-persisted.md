# ST-18 — Qdrant restart: dữ liệu vẫn còn (volume)

| Mục | Giá trị |
|---|---|
| Test case | **ST-18** |
| Nguồn | Test plan mục 4.6.3 (biên 4.8.12) · checklist S-25 mục 4.8.12 |
| Nhóm | System/Manual (edge) |
| Chu kỳ | C3 → xác nhận lại ở C4 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/ST-18/` |
| Truy vết | NFR-02 · UAT-10 · Task S-02 |

## 1. Mục tiêu

Restart container Qdrant không mất dữ liệu vector nhờ Docker volume: danh sách tài liệu còn, search/chat hoạt động như trước.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Kho có ≥2 doc **Sẵn sàng**; đã chạy được 1 câu hỏi có nguồn.

## 3. Dữ liệu thử nghiệm

- 2 câu hỏi trong phạm vi (dataset EV-01), ví dụ một câu trước restart và hỏi lại sau restart.

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Ghi lại baseline: hỏi 1 câu tại **http://localhost:8501/** (trước restart) | Trả lời + nguồn bình thường | V01 |
| 2 | Terminal: `docker compose restart qdrant`, chờ healthy | Container chạy lại; dashboard vẫn có collection `document_chunks` | V02 |
| 3 | F5 trình duyệt | Danh sách docs vẫn đủ (SQLite không phụ thuộc Qdrant) | V03 |
| 4 | Hỏi lại câu cũ | Trả lời + nguồn vẫn đúng như trước restart | V04 |
| 5 | So sánh số point trước vs sau restart (Qdrant dashboard) | Số point khớp nhau | V05 |

## 5. Kết quả mong đợi tổng thể

- Dữ liệu vector còn sau restart nhờ Docker volume.
- Chat + search hoạt động như trước; không mất points.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/ST-18/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, khung hình phải thấy rõ **http://localhost:8501/**, terminal (docker restart) và Qdrant dashboard. Lưu `./test_reports/ST-18/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/ST-18/screenshots/V01-....png`, …
4. Tạo `./test_reports/ST-18/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/ST-18/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-baseline-truoc-restart.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/ST-18/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: NFR-02 (dữ liệu bền vững qua restart), UAT-10.
- Vị trí trong test plan: mục 4.6.3 (biên 4.8.12) · checklist S-25 mục 4.8.12.

## 9. Mẫu report.md (Agent điền vào ./test_reports/ST-18/report.md)

```markdown
# Test Report — ST-18: Qdrant restart — dữ liệu vẫn còn

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
