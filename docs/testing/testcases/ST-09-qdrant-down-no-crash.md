# ST-09 — Qdrant dừng: ứng dụng không crash

| Mục | Giá trị |
|---|---|
| Test case | **ST-09** |
| Nguồn | Test plan mục 4.6.3 (biên 4.8.3) · checklist S-25 mục 4.8.3 |
| Nhóm | System/Manual (edge) |
| Chu kỳ | C3 |
| Ưu tiên | Medium |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/ST-09/` |
| Truy vết | NFR-03 · Task S-05 |

## 1. Mục tiêu

Khi Qdrant không sẵn sàng, ứng dụng hiển thị thông báo thân thiện, không crash, không lộ stack trace.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Kho có dữ liệu (để biết trạng thái bình thường trước khi dừng Qdrant).

## 3. Dữ liệu thử nghiệm

- Một `hop-dong.pdf` (A-01) để thử upload khi Qdrant đang dừng.

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Mở **http://localhost:8501/**; chụp trạng thái bình thường (kho có dữ liệu) | App hoạt động bình thường | V01 |
| 2 | Terminal: `docker compose stop qdrant` | Qdrant container dừng | V02 |
| 3 | F5 trình duyệt | Hiện banner/thông báo thân thiện «chưa sẵn sàng»; không stack trace; UI vẫn render | V03 |
| 4 | Thử upload 1 PDF | Bị chặn với thông báo thân thiện; không lưu file | V04 |

## 5. Kết quả mong đợi tổng thể

- Không traceback/crash; thông báo thân thiện; UI vẫn render.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/ST-09/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, không cắt giữa chừng, khung hình phải thấy rõ **http://localhost:8501/** (trình duyệt) và cửa sổ terminal khi chạy lệnh docker. Lưu `./test_reports/ST-09/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/ST-09/screenshots/V01-....png`, …
4. Tạo `./test_reports/ST-09/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/ST-09/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-trang-thai-binh-thuong.png
    ├── V02-stop-qdrant.png
    ├── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/ST-09/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: NFR-03 (không crash khi Qdrant lỗi, hiển thị thông báo).
- Vị trí trong test plan: mục 4.6.3 (biên 4.8.3) · checklist S-25 mục 4.8.3.
- Tiếp nối: **ST-10** (bật lại Qdrant).

## 9. Mẫu report.md (Agent điền vào ./test_reports/ST-09/report.md)

```markdown
# Test Report — ST-09: Qdrant dừng — ứng dụng không crash

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
