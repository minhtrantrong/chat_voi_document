# ST-06 — Xoá tài liệu (cascade + hiệu lực với chat)

| Mục | Giá trị |
|---|---|
| Test case | **ST-06** |
| Nguồn | Test plan mục 4.6.3 (ST-06) · checklist S-25 mục 4.7 |
| Nhóm | System/Manual |
| Chu kỳ | C3 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/ST-06/` |
| Truy vết | FR-07, FR-08, FR-10 · US-06/AC-06.1, AC-06.2 · Tasks S-05, S-12, S-18 |

## 1. Mục tiêu

Xoá một tài liệu làm sạch đủ 3 kho (SQLite, Qdrant points, file disk) và có hiệu lực ngay với chat: các câu hỏi sau đó không còn dùng hay trích dẫn tài liệu đã xoá.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Kho có ≥2 tài liệu **Sẵn sàng**; đã hỏi ≥1 câu có nguồn từ tài liệu sẽ xoá.

## 3. Dữ liệu thử nghiệm

- `hop-dong.pdf`, `bao-gia.pdf` (A-01, A-02) đã READY.
- Một câu hỏi trong phạm vi, có nguồn từ `hop-dong.pdf`.

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Bấm Xoá trên `hop-dong.pdf` tại **http://localhost:8501/** | Hộp thoại xác nhận nêu đúng tên file | V01 |
| 2 | Bấm Huỷ | Tài liệu vẫn còn nguyên trong danh sách | V02 |
| 3 | Bấm Xoá → Xác nhận | Tài liệu biến mất ngay khỏi danh sách | V03 |
| 4 | Mở Qdrant dashboard, lọc points theo doc_id cũ | 0 point còn lại cho doc đã xoá | V04 |
| 5 | Terminal: `ls data/uploads/` | Không còn file của doc đã xoá | V05 |
| 6 | Hỏi lại câu cũ (có nguồn từ doc vừa xoá) | Câu trả lời mới không còn nguồn/tên file đã xoá; lịch sử chat trong phiên bị xoá | V06 |
| 7 | Xoá tiếp cho đến khi 0 doc READY | Chat input disabled + hướng dẫn tải PDF | V07 |

## 5. Kết quả mong đợi tổng thể

- Xoá cascade sạch cả 3 kho: SQLite + Qdrant + disk.
- Chat sau xoá không còn dùng tài liệu đã xoá.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/ST-06/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, không cắt giữa chừng, trên khung hình thấy rõ URL **http://localhost:8501/** trên thanh địa chỉ. Lưu `./test_reports/ST-06/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/ST-06/screenshots/V01-....png`, …
4. Tạo `./test_reports/ST-06/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/ST-06/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-hop-xac-nhan.png
    ├── V02-sau-huy.png
    ├── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; kết quả tổng thể đạt mục 5; đủ `report.md` + ảnh + video trong `./test_reports/ST-06/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: FR-07 (nút xoá + xác nhận), FR-08 (xoá file + chunks Qdrant), FR-10 (chat chỉ dùng khi READY).
- Vị trí trong test plan: mục 4.6.3 (ST-06) · checklist S-25 mục 4.7.

## 9. Mẫu report.md (Agent điền vào ./test_reports/ST-06/report.md)

```markdown
# Test Report — ST-06: Xoá tài liệu

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
