# SEC-02 — Không log nội dung câu hỏi/trả lời/PDF

| Mục | Giá trị |
|---|---|
| Test case | **SEC-02** |
| Nguồn | Test plan mục 4.6.7 (SEC-02) |
| Nhóm | Security |
| Chu kỳ | C3 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/SEC-02/` |
| Truy vết | NFR-05 · DoD chung (Task breakdown mục 5) |

## 1. Mục tiêu

Logs (terminal + DevTools) chỉ chứa metadata (doc_id, số trang, độ dài), không chứa nội dung câu hỏi, câu trả lời hay nội dung file PDF.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` đang chạy trong cửa sổ terminal có thể quan sát output.
4. Kho có ≥1 doc **Sẵn sàng**.

## 3. Dữ liệu thử nghiệm

- Một PDF với tên file chứa từ nhạy cảm (ví dụ «luong-mat-khau.pdf» hoặc tương tự).
- 2 câu hỏi chứa thông tin nhạy cảm (ví dụ «mức lương là bao nhiêu?», «mật khẩu trong hợp đồng là gì?»).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Đặt cửa sổ terminal hiển thị log của app, sẵn sàng quan sát | Log đang stream | V01 |
| 2 | Upload PDF (tên file chứa từ nhạy cảm); hỏi 2 câu hỏi nhạy cảm tại **http://localhost:8501/** | Hoạt động bình thường | V02 |
| 3 | Chụp ảnh terminal sau các thao tác | Terminal chỉ có ID/độ dài/số trang; **không** chứa nội dung file, câu hỏi hay câu trả lời | V03 |
| 4 | DevTools **Network**: inspect payload request/response | Không chứa nội dung trao đổi | V04 |
| 5 | DevTools **Console**: tìm lỗi/cảnh báo liên quan đến nội dung | Không log nội dung; thông báo lỗi chỉ chứa metadata | V05 |

## 5. Kết quả mong đợi tổng thể

- Log chỉ chứa metadata, không rò rỉ nội dung câu hỏi/trả lời/PDF.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/SEC-02/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, khung hình phải thấy rõ **http://localhost:8501/** khi tương tác app và cửa sổ terminal khi chụp log. Lưu `./test_reports/SEC-02/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx** (kể cả ảnh terminal/DevTools), đặt tên `./test_reports/SEC-02/screenshots/V01-....png`, …
4. Tạo `./test_reports/SEC-02/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/SEC-02/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-terminal-san-sang.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/SEC-02/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: NFR-05 (không log nội dung file/câu hỏi).
- Vị trí trong test plan: mục 4.6.7 (SEC-02).

## 9. Mẫu report.md (Agent điền vào ./test_reports/SEC-02/report.md)

```markdown
# Test Report — SEC-02: Không log nội dung

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
