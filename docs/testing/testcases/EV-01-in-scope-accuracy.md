# EV-01 — Eval 10 câu trong tài liệu (mục tiêu ≥ 8/10 đúng)

| Mục | Giá trị |
|---|---|
| Test case | **EV-01** |
| Nguồn | Test plan mục 4.6.5 (EV-01) · bộ eval 30 câu mục 6-B, nhóm (1) «Trong tài liệu» |
| Nhóm | Eval RAG |
| Chu kỳ | C3 → lặp lại C4 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/EV-01/` |
| Truy vết | QLT-01, FR-11 · US-08/AC-08.1 · Task S-24 |

## 1. Mục tiêu

Chạy qua UI bộ 10 câu hỏi có đáp án trong tài liệu; chấm từng câu theo đáp án chuẩn; mục tiêu ≥ 8/10 đúng, không bịa.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Kho có bộ tài liệu chuẩn A-01…A-03 **Sẵn sàng**.
5. Lấy đúng 10 câu nhóm (1) «Trong tài liệu» từ dataset eval (`tests/eval/`, Task S-24) + đáp án chuẩn kèm theo.

## 3. Dữ liệu thử nghiệm

- Dataset eval nhóm (1) «Trong tài liệu» — 10 câu + đáp án chuẩn.
- Tài liệu chuẩn A-01…A-03.

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Tạo bảng chấm trong report: câu • kỳ vọng • thực tế • đúng/sai • nguồn | Bảng có sẵn | V01 |
| 2 | Gửi câu 1 qua UI tại **http://localhost:8501/**; đối chiếu đáp án chuẩn; mở expander Nguồn | Ghi kết quả câu 1 vào bảng | V02 |
| 3 | Lặp tới câu 10 (mỗi câu một lượt hỏi) | 10 lượt hỏi, mỗi lượt một ảnh bằng chứng | V03–V12 |
| 4 | Tổng hợp: đếm số câu đúng | Tỷ lệ X/10 được tính đúng | V13 |
| 5 | Đối chiếu ngưỡng QLT-01 (≥ 8/10) | PASS nếu ≥ 8; nếu < 8 ghi chi tiết từng câu sai + nguyên nhân phân tích | V14 |

## 5. Kết quả mong đợi tổng thể

- ≥ 8/10 câu trả lời đúng nội dung, không bịa.
- Mọi câu có ảnh bằng chứng; bảng chấm hoàn chỉnh trong report.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/EV-01/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, trên khung hình thấy rõ URL **http://localhost:8501/**. Lưu `./test_reports/EV-01/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi câu hỏi (tối thiểu 10 ảnh)**, đặt tên `./test_reports/EV-01/screenshots/V02-cau-01.png`, …
4. Tạo `./test_reports/EV-01/report.md` theo mẫu mục 9: bảng chấm 10 câu (kết quả từng câu + nguồn), tỷ lệ đúng, ngưỡng QLT-01, phần ghi môi trường; link ảnh + video.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/EV-01/
├── video.webm
├── report.md
├── scoring.md                # (tuỳ chọn) bảng chấm 10 câu chi tiết
└── screenshots/
    ├── V02-cau-01.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: ≥ 8/10 câu chấm đúng; đủ report + ảnh + video trong `./test_reports/EV-01/`.
- **FAIL** khi: < 8/10 câu đúng, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đầy đủ report + bằng chứng, liệt cụ thể câu sai + phân tích nguyên nhân (prompt/SCORE_THRESHOLD/chunking) trong report.

## 8. Truy vết

- Yêu cầu: QLT-01 (độ chính xác nội dung), FR-11 (chỉ trả lời từ context đã index).
- Vị trí trong test plan: mục 4.6.5 (EV-01) · bộ eval mục 6-B nhóm (1).

## 9. Mẫu report.md (Agent điền vào ./test_reports/EV-01/report.md)

```markdown
# Test Report — EV-01: 10 câu trong tài liệu

- **Agent / người test:** … · **Ngày:** …
- **Môi trường:** OS: … · Python: … · Qdrant image: … · LLM: … · Embedding: … · Browser: …
- **App URL:** http://localhost:8501/
- **Kết quả tổng:** PASS / FAIL (X/10 đúng; ngưỡng ≥ 8)

| # | Câu hỏi | Kỳ vọng | Thực tế | Đúng/Sai | Nguồn | Ảnh |
|---|---|---|---|---|---|---|
| 1 | … | … | … | Đúng | hop-dong.pdf, trang … | screenshots/V02-cau-01.png |

- **Video:** ./video.webm
- **Bug phát hiện:**

| Bug ID | Mô tả | Mức (S1–S4) | Ảnh |
|---|---|---|---|
```
