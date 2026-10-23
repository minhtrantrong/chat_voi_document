# UI-06 — Layout với tên file dài/Unicode

| Mục | Giá trị |
|---|---|
| Test case | **UI-06** |
| Nguồn | Test plan mục 4.6.8 (UI-06) |
| Nhóm | UI |
| Chu kỳ | C3 |
| Ưu tiên | Medium |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/UI-06/` |
| Truy vết | NFR-07 · Task S-12 |

## 1. Mục tiêu

Tên file dài + Unicode không làm vỡ layout: truncate đúng phép, không tràn ngang, các khối UI khác giữ ổn định; chữ có dấu hiển thị đúng.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.

## 3. Dữ liệu thử nghiệm

- PDF có tên dài >150 ký tự + tiếng Việt có dấu + ký tự Unicode đặc biệt.
- `hop-dong.pdf` (A-01) làm tham chiếu tên ngắn.

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Chụp layout chuẩn với tên ngắn tại **http://localhost:8501/** | Layout bình thường | V01 |
| 2 | Upload tên dài + Unicode | Row/danh sách truncate hợp lý; không tràn ngang; chữ có dấu hiển thị đúng | V02 |
| 3 | Thu nhỏ cửa sổ trình duyệt (viewport hẹp hơn) | Layout vẫn không tràn ngang; truncate vẫn hoạt động | V03 |

## 5. Kết quả mong đợi tổng thể

- Layout ổn định ở mọi kích thước tên file; Unicode hiển thị đúng.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/UI-06/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, trên khung hình thấy rõ URL **http://localhost:8501/** trên thanh địa chỉ. Lưu `./test_reports/UI-06/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/UI-06/screenshots/V01-....png`, …
4. Tạo `./test_reports/UI-06/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/UI-06/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-layout-chuan.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/UI-06/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: NFR-07 (tên file dài/Unicode).
- Vị trí trong test plan: mục 4.6.8 (UI-06); test chức năng tên dài chi tiết tại ST-17.

## 9. Mẫu report.md (Agent điền vào ./test_reports/UI-06/report.md)

```markdown
# Test Report — UI-06: Layout với tên file dài/Unicode

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
