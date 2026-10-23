# UI-04 — Expander Nguồn: tên file + trang + đoạn trích

| Mục | Giá trị |
|---|---|
| Test case | **UI-04** |
| Nguồn | Test plan mục 4.6.8 (UI-04) |
| Nhóm | UI |
| Chu kỳ | C3 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/UI-04/` |
| Truy vết | FR-14 · US-10/AC-10.1 · Tasks S-20, S-21 |

## 1. Mục tiêu

Expander **Nguồn sau mỗi câu trả lời có nguồn**: hiển thị tên file + số trang + đoạn trích; loại trừ mục trùng; tối đa `MAX_CHUNKS_PER_DOC=4` mỗi tài liệu; NOT_FOUND không có nguồn.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Kho có ≥2 docs **Sẵn sàng** (đã chạy ST-05) + PDF gốc để đối chiếu trích dẫn.

## 3. Dữ liệu thử nghiệm

- `hop-dong.pdf`, `bao-gia.pdf` (A-01, A-02) đã READY.
- Câu hỏi đơn tài liệu, câu hỏi đa tài liệu (dataset EV-01/EV-02), câu hỏi ngoài phạm vi (dataset EV-03).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Hỏi 1 câu trong phạm vi tại **http://localhost:8501/** | Expander **Nguồn** có mục: tên file + trang + đoạn trích | V01 |
| 2 | Mở từng mục nguồn; đối chiếu với PDF gốc | Đoạn trích nằm đúng vị trí trong PDF gốc | V02 |
| 3 | Hỏi câu đa tài liệu | Nguồn ≥2 file khác nhau; không mục trùng | V03 |
| 4 | Hỏi câu ngoài phạm vi | Thông báo NOT_FOUND **không** có mục Nguồn | V04 |
| 5 | Đếm mục nguồn theo từng file | Không file nào vượt 4 mục (`MAX_CHUNKS_PER_DOC`) | V05 |

## 5. Kết quả mong đợi tổng thể

- Nguồn đủ thông tin (file + trang + trích) và kiểm chứng được với PDF gốc.
- Quy tắc lọc trùng + giới hạn mỗi doc áp dụng đúng.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/UI-04/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, trên khung hình thấy rõ URL **http://localhost:8501/** trên thanh địa chỉ. Lưu `./test_reports/UI-04/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/UI-04/screenshots/V01-....png`, …
4. Tạo `./test_reports/UI-04/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/UI-04/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-nguon-don.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/UI-04/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: FR-14 (hiển thị trích dẫn nguồn).
- Vị trí trong test plan: mục 4.6.8 (UI-04); kiểm tốc độ/độ chính xác nguồn chi tiết tại EV-04.

## 9. Mẫu report.md (Agent điền vào ./test_reports/UI-04/report.md)

```markdown
# Test Report — UI-04: Expander Nguồn

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
