# ST-01 — Upload 1 PDF hợp lệ

| Mục | Giá trị |
|---|---|
| Test case | **ST-01** |
| Nguồn | Test plan [`TestPlan_Simple_Qdrant.md`](../TestPlan_Simple_Qdrant.md) mục 4.6.3 (ST-01) · checklist S-25 mục 4.2 |
| Nhóm | System/Manual |
| Chu kỳ | C2 (sau milestone M2) |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/ST-01/` |
| Truy vết | FR-01, FR-05, FR-06 · US-01/AC-01.1 · Tasks S-11, S-12 |

## 1. Mục tiêu

Upload một PDF hợp lệ và xác minh trọn chuỗi: chip **Đang xử lý → Sẵn sàng**, file gốc lưu trên disk, points tạo trong Qdrant, bản ghi SQLite còn sau refresh.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.

## 3. Dữ liệu thử nghiệm

- `hop-dong.pdf` — 32 trang, có text tiếng Việt (fixture A-01, tại `tests/eval/fixtures/`).
- Kho `data/` trống (chưa có tài liệu nào).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Mở **http://localhost:8501/** khi kho trống | Trang render không exception; sidebar TÀI LIỆU rỗng; chat disabled | V01 |
| 2 | Kéo-thả `hop-dong.pdf` vào uploader | Xuất hiện chip **Đang xử lý** (icon + nhãn) | V02 |
| 3 | Chờ xử lý xong | Chip chuyển **Sẵn sàng**; hiển thị đúng số trang 32 | V03 |
| 4 | Terminal: `ls -l data/uploads/` | Có file mới dạng `{doc_id}.pdf` | V04 |
| 5 | Mở `http://localhost:6333/dashboard` → collection `document_chunks` | Có points mới; payload có `doc_id, file_name, page, chunk_index, text` | V05 |
| 6 | Refresh trình duyệt tại **http://localhost:8501/** | Tài liệu vẫn còn trong danh sách (đọc từ SQLite) | V06 |

## 5. Kết quả mong đợi tổng thể

- Upload → READY đúng trạng thái; page_count đúng.
- Đồng bộ cả 3 kho: SQLite (danh sách) + Qdrant (points) + disk (file).
- Danh sách còn nguyên sau refresh.
- Không có traceback nào xuất hiện trên UI.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/ST-01/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, không cắt giữa chừng, trên khung hình thấy rõ URL **http://localhost:8501/** trên thanh địa chỉ. Lưu `./test_reports/ST-01/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx** (một mã = một ảnh), đặt tên `./test_reports/ST-01/screenshots/V01-trang-ban-dau.png`, `V02-...`, … Ảnh của bước terminal/DevTools/Qdrant dashboard chụp chính cửa sổ đó.
4. Tạo `./test_reports/ST-01/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link tương đối tới ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/ST-01/
├── video.webm        # hoặc video.mp4
├── report.md
└── screenshots/
    ├── V01-trang-ban-dau.png
    ├── V02-chip-dang-xu-ly.png
    ├── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/ST-01/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: FR-01 (upload PDF), FR-05 (hiển thị trạng thái), FR-06 (index Qdrant).
- Vị trí trong test plan: mục 4.6.3 (ST-01) · checklist S-25 mục 4.2.

## 9. Mẫu report.md (Agent điền vào ./test_reports/ST-01/report.md)

```markdown
# Test Report — ST-01: Upload 1 PDF hợp lệ

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
