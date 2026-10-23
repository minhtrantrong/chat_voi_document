# SEC-03 — Tên file độc hại: không XSS, không path traversal

| Mục | Giá trị |
|---|---|
| Test case | **SEC-03** |
| Nguồn | Test plan mục 4.6.7 (SEC-03) |
| Nhóm | Security |
| Chu kỳ | C3 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/SEC-03/` |
| Truy vết | NFR-07 · Tasks S-07, S-12 |

## 1. Mục tiêu

Tên file chứa thẻ `<script>`/ký tự đặc biệt không thực thi script (được escape đúng); file lưu dưới dạng `{doc_id}.pdf` nên không có path traversal qua tên người dùng.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.

## 3. Dữ liệu thử nghiệm

- PDF có tên chứa `<script>alert(1)</script>` (nếu hệ điều hành cho phép ký tự `<`, `>`; nếu không, dùng tên gần tương tự nhưng đầy đủ dấu `<`).
- Một file hợp lệ làm vệ tinh (`hop-dong.pdf`) — để kiểm không bị xoá nhầm.

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Upload tên file chứa `<script>alert(1)</script>` tại **http://localhost:8501/** | Hoặc upload bình thường, hoặc bị từ chối đúng quy trình (nếu quy ước mã lỗi quy định việc tự chặn tên độc hại); không pop-up alert; không script thực thi | V01 |
| 2 | DevTools **Elements**: xem DOM node hiển thị tên file | Tên là text node được escape; không có element `<script>` thật | V02 |
| 3 | Terminal: `ls data/uploads/` sau khi upload | Chỉ có file dạng `{doc_id}.pdf` — tên gốc không đi vào đường dẫn lưu | V03 |
| 4 | Hỏi 1 câu lấy nguồn từ file này | Nguồn hiển thị tên file escape đúng; không thực thi | V04 |
| 5 | Xoá file độc hại | Chỉ đúng file đó bị xoá; file khác (db, bins, vệ tinh) không bị ảnh hưởng | V05 |

## 5. Kết quả mong đợi tổng thể

- Không XSS thực thi; escape đúng; lưu trữ không phụ thuộc tên người dùng; xoá an toàn.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/SEC-03/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, khung hình phải thấy rõ **http://localhost:8501/** khi tương tác và terminal ở bước 3. Lưu `./test_reports/SEC-03/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/SEC-03/screenshots/V01-....png`, …
4. Tạo `./test_reports/SEC-03/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/SEC-03/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-upload-ten-xss.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/SEC-03/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: NFR-07 (tên file độc hại).
- Vị trí trong test plan: mục 4.6.7 (SEC-03); chi tiết layout tên dài tại ST-17, UI-06.

## 9. Mẫu report.md (Agent điền vào ./test_reports/SEC-03/report.md)

```markdown
# Test Report — SEC-03: Tên file độc hại

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
