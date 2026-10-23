# EV-02 — Eval 10 câu đa tài liệu (mục tiêu ≥ 8/10 nguồn ≥ 2 tài liệu)

| Mục | Giá trị |
|---|---|
| Test case | **EV-02** |
| Nguồn | Test plan mục 4.6.5 (EV-02) · bộ eval 30 câu mục 6-B, nhóm (2) «Đa tài liệu» |
| Nhóm | Eval RAG |
| Chu kỳ | C3 → lặp lại C4 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/EV-02/` |
| Truy vết | QLT-02, FR-13 · US-09/AC-09.1 · Task S-24 |

## 1. Mục tiêu

Chạy bộ 10 câu cần thông tin từ ≥2 tài liệu qua UI; chấm rubric: tổng hợp đúng nội dung VÀ nguồn từ ≥2 tài liệu; mục tiêu ≥ 8/10 đạt.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Kho có bộ tài liệu chuẩn A-01…A-03 **Sẵn sàng**.
5. Dataset eval nhóm (2) «Đa tài liệu» — 10 câu từ `tests/eval/` (Task S-24).

## 3. Dữ liệu thử nghiệm

- Dataset eval nhóm (2) — 10 câu đa tài liệu.
- Tài liệu chuẩn A-01…A-03.

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Tạo bảng chấm (cột thêm: số tài liệu xuất hiện trong nguồn) | Bảng có sẵn | V01 |
| 2 | Gửi tuần tự 10 câu qua UI tại **http://localhost:8501/**; mỗi câu mở expander Nguồn | 10 lượt hỏi; nguồn được đếm | V02–V11 |
| 3 | Chấm rubric từng câu: tổng hợp đúng VÀ nguồn ≥2 tài liệu | Kết quả từng câu | V12 |
| 4 | Tổng hợp đếm | X/10 câu đạt rubric | V13 |
| 5 | Đối chiếu ngưỡng QLT-02 (≥ 8/10) | PASS nếu ≥ 8; nếu < 8 phân tích phân bổ chunk (`MAX_CHUNKS_PER_DOC`, `TOP_K`) | V14 |

## 5. Kết quả mong đợi tổng thể

- ≥ 8/10 câu đạt rubric (đúng nội dung, nguồn ≥2 tài liệu).
- Bảng + ảnh đầy đủ trong report.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/EV-02/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, trên khung hình thấy rõ URL **http://localhost:8501/** (và mục Nguồn được mở). Lưu `./test_reports/EV-02/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi câu (kèm nguồn)**, đặt tên `./test_reports/EV-02/screenshots/V02-cau-01.png`, …
4. Tạo `./test_reports/EV-02/report.md` theo mẫu mục 9: bảng chấm 10 câu, tỷ lệ đạt rubric, ngưỡng QLT-02, phần ghi môi trường; link ảnh + video.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/EV-02/
├── video.webm
├── report.md
├── scoring.md
└── screenshots/
    ├── V02-cau-01.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: ≥ 8/10 câu đạt rubric; đủ report + ảnh + video trong `./test_reports/EV-02/`.
- **FAIL** khi: < 8/10 câu đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo report + bằng chứng và phân tích nguyên nhân trong report.

## 8. Truy vết

- Yêu cầu: QLT-02 (đa tài liệu tổng hợp chính), FR-13.
- Vị trí trong test plan: mục 4.6.5 (EV-02) · bộ eval mục 6-B nhóm (2).

## 9. Mẫu report.md (Agent điền vào ./test_reports/EV-02/report.md)

```markdown
# Test Report — EV-02: 10 câu đa tài liệu

- **Agent / người test:** … · **Ngày:** …
- **Môi trường:** OS: … · Python: … · Qdrant image: … · LLM: … · Embedding: … · Browser: …
- **App URL:** http://localhost:8501/
- **Kết quả tổng:** PASS / FAIL (X/10 đạt; ngưỡng ≥ 8)

| # | Câu hỏi | Tổng hợp đúng? | Số tài liệu nguồn | Nguồn | Đạt rubric? | Ảnh |
|---|---|---|---|---|---|---|
| 1 | … | … | 2 | hop-dong, bao-gia | Đạt | screenshots/V02-cau-01.png |

- **Video:** ./video.webm
- **Bug phát hiện:**

| Bug ID | Mô tả | Mức (S1–S4) | Ảnh |
|---|---|---|---|
```
