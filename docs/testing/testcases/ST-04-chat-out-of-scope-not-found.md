# ST-04 — Chat ngoài phạm vi → NOT_FOUND

| Mục | Giá trị |
|---|---|
| Test case | **ST-04** |
| Nguồn | Test plan mục 4.6.3 (ST-04) · checklist S-25 mục 4.5 |
| Nhóm | System/Manual |
| Chu kỳ | C3 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/ST-04/` |
| Truy vết | FR-12 · BR-07 · US-11 (PRD) · Task S-17 |

## 1. Mục tiêu

Câu hỏi không có thông tin trong tài liệu luôn được trả thông báo cố định «Không tìm thấy thông tin này trong các tài liệu đã tải lên.» — không bịa, không có nguồn, không gọi LLM.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Kho có ≥1 tài liệu **Sẵn sàng**.

## 3. Dữ liệu thử nghiệm

- Bộ câu hỏi ngoài phạm vi thuộc dataset EV-03, ví dụ:
  - «Giá cổ phiếu VNM hôm nay?» (tin tức thời sự)
  - «Thủ đô nước Pháp là gì?» (kiến thức phổ thông)
  - Một câu nửa trong nửa ngoài (xem dataset EV-03).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Hỏi «Giá cổ phiếu VNM hôm nay?» tại **http://localhost:8501/** | Trả đúng chuỗi NOT_FOUND nguyên văn | V01 |
| 2 | Xác minh thông báo đó có mục Nguồn không | **Không** hiển thị mục Nguồn / trích dẫn nào | V02 |
| 3 | Hỏi «Thủ đô nước Pháp là gì?» | NOT_FOUND; **không** trả lời bằng kiến thức phổ thông | V03 |
| 4 | Hỏi một câu nửa đúng nửa ngoài (từ dataset EV-03) | Phần ngoài không bịa; nếu toàn câu thiếu ngữ cảnh → NOT_FOUND | V04 |
| 5 | Ghi nhận thời gian phản hồi NOT_FOUND | Phản hồi nhanh (vì không chờ LLM) | V05 |

## 5. Kết quả mong đợi tổng thể

- Chuỗi NOT_FOUND nguyên văn cho cả 3 nhóm câu hỏi.
- Không nguồn, không bịa kiến thức ngoài.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/ST-04/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, không cắt giữa chừng, trên khung hình thấy rõ URL **http://localhost:8501/** trên thanh địa chỉ. Lưu `./test_reports/ST-04/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/ST-04/screenshots/V01-....png`, …
4. Tạo `./test_reports/ST-04/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/ST-04/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-not-found-tin-tuc.png
    ├── V02-nguon-trong.png
    ├── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/ST-04/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: FR-12 (thông báo NOT_FOUND), BR-07 (chỉ dùng context đã index).
- Vị trí trong test plan: mục 4.6.3 (ST-04) · checklist S-25 mục 4.5.
- Bản ghi kết quả có thể dùng cho **EV-03** (chất lượng NOT_FOUND).

## 9. Mẫu report.md (Agent điền vào ./test_reports/ST-04/report.md)

```markdown
# Test Report — ST-04: Chat ngoài phạm vi → NOT_FOUND

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
