# UI-03 — Thông báo lỗi tiếng Việt theo danh mục mã lỗi

| Mục | Giá trị |
|---|---|
| Test case | **UI-03** |
| Nguồn | Test plan mục 4.6.8 (UI-03) · bảng mã lỗi mục 6-C |
| Nhóm | UI |
| Chu kỳ | C3 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/UI-03/` |
| Truy vết | FR-03, NFR-04 · US-03/AC-03.1–3.3 · Task S-14 |

## 1. Mục tiêu

Đi qua từng loại lỗi trong danh mục mã lỗi (test plan mục 6-C): mỗi thông báo đúng nội dung quy định, nêu tên file + hành động tiếp theo, không dùng thuật ngữ kỹ thuật.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.

## 3. Dữ liệu thử nghiệm (fixtures A-04…A-10)

- `fake.docx` (sai định dạng), `disguised.pdf` (text đổi đuôi .pdf), `encrypted.pdf` (mã hoá), `corrupt.pdf` (hỏng), `big-25mb.pdf` (>25 MB), `long-401p.pdf` (>400 trang), `scan.pdf` (scan không text).
- Bảng mã lỗi mục 6-C trong test plan (mở song song để đối chiếu).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Upload `fake.docx` tại **http://localhost:8501/** | «Chỉ hỗ trợ PDF: <tên file>» | V01 |
| 2 | Upload `disguised.pdf` (text file đổi đuôi .pdf) | Lỗi không phải PDF (magic bytes), đúng danh mục 6-C | V02 |
| 3 | Upload `encrypted.pdf` | «được bảo vệ bằng mật khẩu, không thể đọc» | V03 |
| 4 | Upload `corrupt.pdf` | «tệp bị hỏng, không đọc được» | V04 |
| 5 | Upload `big-25mb.pdf` | «vượt giới hạn 25 MB» (+ dung lượng thực tế) | V05 |
| 6 | Upload `long-401p.pdf` | «vượt giới hạn 400 trang» (+ số trang thực tế) | V06 |
| 7 | Upload `scan.pdf` | «không có văn bản trích xuất được (PDF dạng ảnh scan chưa được hỗ trợ)» | V07 |
| 8 | Đặt các thông báo cạnh bảng 6-C, đối chiếu từng mã | Tất cả khớp mã lỗi + có tên file + hành động tiếp theo | V08 |

## 5. Kết quả mong đợi tổng thể

- Mỗi loại lỗi có đúng thông báo theo danh mục 6-C; nêu tên file; có hành động tiếp theo; không thuật ngữ kỹ thuật.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/UI-03/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, trên khung hình thấy rõ URL **http://localhost:8501/** trên thanh địa chỉ. Lưu `./test_reports/UI-03/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx** (mỗi loại thông báo lỗi một ảnh, tổng ~8 ảnh), đặt tên `./test_reports/UI-03/screenshots/V01-....png`, …
4. Tạo `./test_reports/UI-03/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/UI-03/
├── video.webm
├── report.md
├── 6C-doi-chieu.md        # bảng đối chiếu thông báo vs mã lỗi 6-C (tự tạo)
└── screenshots/
    ├── V01-thong-bao-docx.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/UI-03/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: FR-03 (báo lỗi thân thiện tiếng Việt), NFR-04 (không hiển thị lỗi kỹ thuật).
- Vị trí trong test plan: mục 4.6.8 (UI-03) · bảng mã lỗi mục 6-C.
- Tham chiếu test chức năng: ST-12, ST-13, ST-14, ST-15.

## 9. Mẫu report.md (Agent điền vào ./test_reports/UI-03/report.md)

```markdown
# Test Report — UI-03: Thông báo lỗi tiếng Việt

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
