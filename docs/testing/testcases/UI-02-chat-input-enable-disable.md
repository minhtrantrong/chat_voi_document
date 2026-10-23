# UI-02 — Chat input bật/tắt theo trạng thái READY

| Mục | Giá trị |
|---|---|
| Test case | **UI-02** |
| Nguồn | Test plan mục 4.6.8 (UI-02) |
| Nhóm | UI |
| Chu kỳ | C3 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/UI-02/` |
| Truy vết | FR-10 · US-07/AC-07.2 · Task S-19 |

## 1. Mục tiêu

Ô nhập chat chỉ enabled khi có ≥1 tài liệu **Sẵn sàng**; disabled khi 0 READY (kho trống, chỉ có doc Lỗi, hoặc toàn bộ doc đang xử lý).

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `.env` hợp lệ theo `.env.example` (model LLM + Embedding đã cấu hình, API key đúng).
3. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/** không exception.
4. Kho trống trước khi bắt đầu.

## 3. Dữ liệu thử nghiệm

- `hop-dong.pdf` (A-01 — sẽ READY).
- `scan.pdf` (A-04 — sẽ Lỗi).

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Mở **http://localhost:8501/** khi 0 docs | Chat disabled | V01 |
| 2 | Upload `scan.pdf` (chỉ doc lỗi) | Vẫn disabled | V02 |
| 3 | Upload `hop-dong.pdf`; quan sát trong lúc **Đang xử lý** | Vẫn disabled (chỉ bật khi READY) | V03 |
| 4 | Doc chuyển **Sẵn sàng** | Chat input tự bật; nhập được câu hỏi | V04 |
| 5 | Xoá doc cuối cùng | Trở lại disabled + hướng dẫn tải PDF | V05 |

## 5. Kết quả mong đợi tổng thể

- Toggle chat input theo đúng điều kiện READY; mọi chuyển đổi có bằng chứng.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/UI-02/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, trên khung hình thấy rõ URL **http://localhost:8501/** trên thanh địa chỉ. Lưu `./test_reports/UI-02/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx** (một mã = một ảnh), đặt tên `./test_reports/UI-02/screenshots/V01-....png`, …
4. Tạo `./test_reports/UI-02/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/UI-02/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-0-docs-disabled.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/UI-02/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: FR-10 (disable chat khi không có doc READY).
- Vị trí trong test plan: mục 4.6.8 (UI-02); trạng thái rỗng chi tiết tại ST-07, chỉ-doc-lỗi tại ST-08.

## 9. Mẫu report.md (Agent điền vào ./test_reports/UI-02/report.md)

```markdown
# Test Report — UI-02: Chat input bật/tắt theo READY

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
