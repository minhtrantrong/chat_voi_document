# ST-07 — Trạng thái rỗng: chat vô hiệu

| Mục | Giá trị |
|---|---|
| Test case | **ST-07** |
| Nguồn | Test plan mục 4.6.3 (biên 4.8.1) · checklist S-25 mục 4.8.1 |
| Nhóm | System/Manual (edge) |
| Chu kỳ | C2 |
| Ưu tiên | Medium |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/ST-07/` |
| Truy vết | FR-10 · US-07/AC-07.2 · Task S-19 |

## 1. Mục tiêu

Khi chưa có tài liệu nào, chat input bị vô hiệu và hiển thị hướng dẫn «Tải PDF đầu tiên».

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Kho `data/` trống (chưa có tài liệu nào).

## 3. Dữ liệu thử nghiệm

- Không cần file; môi trường sạch.

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Mở **http://localhost:8501/** khi 0 tài liệu | Chat input disabled + thông báo «Tải PDF đầu tiên để bắt đầu» | V01 |
| 2 | F5 trình duyệt | Trạng thái giữ nguyên | V02 |
| 3 | Thử gửi câu bằng Enter/click vào ô disabled | Không gửi được; không tạo message | V03 |

## 5. Kết quả mong đợi tổng thể

- Chat chắc chắn vô hiệu; hướng dẫn hiển thị rõ; không còn cách nào gửi câu hỏi.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/ST-07/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, không cắt giữa chừng, trên khung hình thấy rõ URL **http://localhost:8501/** trên thanh địa chỉ. Lưu `./test_reports/ST-07/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/ST-07/screenshots/V01-....png`, …
4. Tạo `./test_reports/ST-07/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/ST-07/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-trang-thai-rong.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/ST-07/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: FR-10 (disable chat khi không có doc READY).
- Vị trí trong test plan: mục 4.6.3 (biên 4.8.1) · checklist S-25 mục 4.8.1.

## 9. Mẫu report.md (Agent điền vào ./test_reports/ST-07/report.md)

```markdown
# Test Report — ST-07: Trạng thái rỗng — chat vô hiệu

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
