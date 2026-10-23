# UI-07 — Dòng nhắc «AI có thể sai…» luôn hiển thị

| Mục | Giá trị |
|---|---|
| Test case | **UI-07** |
| Nguồn | Test plan mục 4.6.8 (UI-07) |
| Nhóm | UI |
| Chu kỳ | C3 |
| Ưu tiên | Medium |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/UI-07/` |
| Truy vết | Trụ cột Evidence-first (IMP mục 0) · ASM-005 · Tasks S-12, S-18 |

## 1. Mục tiêu

Dòng nhắc «AI có thể sai. Kiểm tra lại với tài liệu gốc trước khi dùng cho quyết định quan trọng.» luôn hiển thị ở mọi trạng thái chính: khi mở app, khi streaming, sau NOT_FOUND, khi có lịch sử.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Kho có ≥1 doc **Sẵn sàng**.

## 3. Dữ liệu thử nghiệm

- `hop-dong.pdf` (A-01) đã READY.
- 1 câu hỏi trong phạm vi (dataset EV-01) + 1 câu hỏi ngoài phạm vi (dataset EV-03).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Mở **http://localhost:8501/** ở trạng thái có docs (chưa chat) | Dòng nhắc hiển thị | V01 |
| 2 | Quan sát trong lúc streaming câu trả lời | Dòng nhắc vẫn hiển thị | V02 |
| 3 | Sau khi nhận NOT_FOUND | Dòng nhắc vẫn hiển thị | V03 |
| 4 | Khi lịch sử chat nhiều lượt hiển thị | Dòng nhắc vẫn hiển thị | V04 |

## 5. Kết quả mong đợi tổng thể

- Dòng nhắc luôn hiển thị ở mọi trạng thái chính; không bị ẩn bởi layout hay tình trạng app.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/UI-07/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, trên khung hình thấy rõ URL **http://localhost:8501/** trên thanh địa chỉ. Lưu `./test_reports/UI-07/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/UI-07/screenshots/V01-....png`, …
4. Tạo `./test_reports/UI-07/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/UI-07/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-khi-mo-app.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/UI-07/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Trụ cột: Evidence-first (hiển thị rõ giới hạn của AI).
- Vị trí trong test plan: mục 4.6.8 (UI-07).

## 9. Mẫu report.md (Agent điền vào ./test_reports/UI-07/report.md)

```markdown
# Test Report — UI-07: Dòng nhắc «AI có thể sai…»

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
