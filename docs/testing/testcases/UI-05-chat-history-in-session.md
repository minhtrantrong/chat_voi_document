# UI-05 — Lịch sử chat đa lượt trong phiên

| Mục | Giá trị |
|---|---|
| Test case | **UI-05** |
| Nguồn | Test plan mục 4.6.8 (UI-05) |
| Nhóm | UI |
| Chu kỳ | C3 |
| Ưu tiên | Medium |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/UI-05/` |
| Truy vết | FR-15 · US-14 (rút gọn) · Task S-18 |

## 1. Mục tiêu

Lịch sử user/assistant hiển thị đầy đủ, đúng thứ tự, trong một phiên chat; có scroll; câu hỏi tham chiếu lượt trước được xử lý đúng với ngữ cảnh hội thoại.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Kho có ≥1 doc **Sẵn sàng**.

## 3. Dữ liệu thử nghiệm

- `hop-dong.pdf` (A-01) đã READY.
- 3 câu hỏi trong phạm vi (dataset EV-01), trong đó 1 câu rất dài (kiểm layout) và 1 câu tham chiếu lượt trước.

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Hỏi tuần tự 3 câu tại **http://localhost:8501/** (một câu rất dài) | Mỗi lượt thêm message; đúng thứ tự user → assistant | V01 |
| 2 | Scroll lên/xuống khung chat | Mọi tin nhắn hiển thị đầy đủ; không message mất/giới hạn khung | V02 |
| 3 | Hỏi câu tham chiếu lượt trước («còn hạn chót của nó là bao giờ?») | Trả lời dựa trên ngữ cảnh hội thoại (không cần nhắc lại chủ đề) | V03 |

## 5. Kết quả mong đợi tổng thể

- History đa lượt hiển thị đầy đủ, đúng trật tự scroll được; ngữ cảnh hội thoại được giữ.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/UI-05/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, trên khung hình thấy rõ URL **http://localhost:8501/** trên thanh địa chỉ. Lưu `./test_reports/UI-05/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/UI-05/screenshots/V01-....png`, …
4. Tạo `./test_reports/UI-05/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/UI-05/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-lich-su-3-luot.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/UI-05/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: FR-15 (lịch sử chat).
- Vị trí trong test plan: mục 4.6.8 (UI-05); trường hợp mất lịch sử sau refresh chi tiết tại ST-16.

## 9. Mẫu report.md (Agent điền vào ./test_reports/UI-05/report.md)

```markdown
# Test Report — UI-05: Lịch sử chat đa lượt

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
