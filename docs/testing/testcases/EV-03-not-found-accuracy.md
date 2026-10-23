# EV-03 — Eval 10 câu ngoài phạm vi (mục tiêu ≥ 9/10 NOT_FOUND đúng)

| Mục | Giá trị |
|---|---|
| Test case | **EV-03** |
| Nguồn | Test plan mục 4.6.5 (EV-03) · bộ eval 30 câu mục 6-B, nhóm (3) «Ngoài phạm vi» |
| Nhóm | Eval RAG |
| Chu kỳ | C3 → lặp lại C4 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/EV-03/` |
| Truy vết | QLT-03, FR-12 · US-11 (PRD) · Task S-24 |

## 1. Mục tiêu

Chạy 10 câu ngoài phạm vi (tin tức thời sự, kiến thức phổ thông, câu nửa nửa) qua UI; mục tiêu ≥ 9/10 trả thông báo NOT_FOUND cố định nguyên văn, không bịa, không nguồn.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Kho có ≥1 doc **Sẵn sàng**.
5. Dataset eval nhóm (3) «Ngoài phạm vi» — 10 câu từ `tests/eval/` (Task S-24).

## 3. Dữ liệu thử nghiệm

- Dataset eval nhóm (3) — 10 câu ngoài phạm vi.

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Tạo bảng chấm: câu • loại (tin tức / phổ thông / nửa nửa) • phản hồi thực tế • NOT_FOUND? • bịa? • nguồn? | Bảng có sẵn | V01 |
| 2 | Gửi từng câu qua UI tại **http://localhost:8501/**; chụp mỗi phản hồi | 10 lượt hỏi, mỗi lượt một ảnh | V02–V11 |
| 3 | Chấm từng câu: chuỗi NOT_FOUND nguyên văn + không nguồn + không bịa | Kết quả từng câu | V12 |
| 4 | Tổng hợp đếm | X/10 NOT_FOUND đúng | V13 |
| 5 | Đối chiếu ngưỡng QLT-03 (≥ 9/10) | PASS nếu ≥ 9; bất kỳ câu nào bịa kiến thức ngoài = hallucination, bug mức ưu tiên cao | V14 |

## 5. Kết quả mong đợi tổng thể

- ≥ 9/10 câu trả NOT_FOUND đúng nguyên văn.
- 0 trường hợp bịa kiến thức ngoài tài liệu.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/EV-03/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, trên khung hình thấy rõ URL **http://localhost:8501/**. Lưu `./test_reports/EV-03/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi câu (tối thiểu 10 ảnh)**, đặt tên `./test_reports/EV-03/screenshots/V02-cau-01.png`, …
4. Tạo `./test_reports/EV-03/report.md` theo mẫu mục 9: bảng chấm 10 câu, tỷ lệ NOT_FOUND đúng, ngưỡng QLT-03, phần ghi môi trường; link ảnh + video.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/EV-03/
├── video.webm
├── report.md
├── scoring.md
└── screenshots/
    ├── V02-cau-01.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: ≥ 9/10 câu NOT_FOUND đúng; đủ report + ảnh + video trong `./test_reports/EV-03/`.
- **FAIL** khi: < 9/10 câu đúng, hoặc thiếu artifact. Mọi trường hợp bịa (hallucination) được ghi riêng và ưu tiên bug cao.

## 8. Truy vết

- Yêu cầu: QLT-03 (không trả lời ngoài tài liệu), FR-12.
- Vị trí trong test plan: mục 4.6.5 (EV-03) · bộ eval mục 6-B nhóm (3).

## 9. Mẫu report.md (Agent điền vào ./test_reports/EV-03/report.md)

```markdown
# Test Report — EV-03: 10 câu ngoài phạm vi

- **Agent / người test:** … · **Ngày:** …
- **Môi trường:** OS: … · Python: … · Qdrant image: … · LLM: … · Embedding: … · Browser: …
- **App URL:** http://localhost:8501/
- **Kết quả tổng:** PASS / FAIL (X/10 đúng; ngưỡng ≥ 9)

| # | Câu hỏi | Loại | Phản hồi thực tế | NOT_FOUND? | Bịa? | Ảnh |
|---|---|---|---|---|---|---|
| 1 | … | tin tức | … | Đúng | Không | screenshots/V02-cau-01.png |

- **Video:** ./video.webm
- **Bug phát hiện:**

| Bug ID | Mô tả | Mức (S1–S4) | Ảnh |
|---|---|---|---|
```
