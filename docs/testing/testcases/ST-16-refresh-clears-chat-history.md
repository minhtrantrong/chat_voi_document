# ST-16 — Refresh mất lịch sử chat (đúng thiết kế)

| Mục | Giá trị |
|---|---|
| Test case | **ST-16** |
| Nguồn | Test plan mục 4.6.3 (biên 4.8.10) · checklist S-25 mục 4.8.10 |
| Nhóm | System/Manual (edge) |
| Chu kỳ | C2 |
| Ưu tiên | Medium |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/ST-16/` |
| Truy vết | FR-15 · US-14 (rút gọn) · Task S-18 |

## 1. Mục tiêu

Lịch sử chat nằm trong `st.session_state`: refresh trình duyệt làm mất lịch sử chat (được thiết kế như vậy), nhưng danh sách tài liệu vẫn nguyên.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Kho có ≥1 doc **Sẵn sàng**.

## 3. Dữ liệu thử nghiệm

- `hop-dong.pdf` (A-01) đã READY.
- 2 câu hỏi trong phạm vi (dataset EV-01).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Hỏi 2 câu tại **http://localhost:8501/** để tạo lịch sử | Lịch sử hiển thị đầy đủ cả user và assistant | V01 |
| 2 | F5 trình duyệt | Lịch sử chat biến mất; danh sách tài liệu vẫn đủ | V02 |
| 3 | Hỏi lại câu đầu tiên | Hoạt động bình thường (lịch sử mới bắt đầu từ đầu) | V03 |

## 5. Kết quả mong đợi tổng thể

- Lịch sử chat mất sau refresh (ánh xạ đúng thiết kế).
- Danh sách tài liệu và points trong Qdrant không bị ảnh hưởng.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/ST-16/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, không cắt giữa chừng, trên khung hình thấy rõ URL **http://localhost:8501/** trên thanh địa chỉ. Lưu `./test_reports/ST-16/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/ST-16/screenshots/V01-....png`, …
4. Tạo `./test_reports/ST-16/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/ST-16/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-lich-su-truoc-refresh.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/ST-16/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: FR-15 (lịch sử chat theo phiên).
- Giới hạn: lịch sử chat chỉ được lưu trong `st.session_state`.
- Vị trí trong test plan: mục 4.6.3 (biên 4.8.10) · checklist S-25 mục 4.8.10.

## 9. Mẫu report.md (Agent điền vào ./test_reports/ST-16/report.md)

```markdown
# Test Report — ST-16: Refresh mất lịch sử chat

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
