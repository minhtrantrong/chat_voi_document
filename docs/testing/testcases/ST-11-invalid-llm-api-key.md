# ST-11 — Sai API key: thông báo thân thiện, không lộ key

| Mục | Giá trị |
|---|---|
| Test case | **ST-11** |
| Nguồn | Test plan mục 4.6.3 (biên 4.8.5) · checklist S-25 mục 4.8.5 |
| Nhóm | System/Manual (edge) |
| Chu kỳ | C3 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/ST-11/` |
| Truy vết | NFR-04 · SEC-01 · Tasks S-14, S-16 |

## 1. Mục tiêu

Khi key LLM/Embedding sai, app hiển thị thông báo thân thiện; không lộ API key và không lộ stack trace lên UI.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/**.
3. **Backup `.env` vào `.env.bak` và restore sau khi test xong (bắt buộc).**
4. Kho có ≥1 doc READY để hỏi được.

## 3. Dữ liệu thử nghiệm

- API key sai cho LLM hoặc Embedding, ví dụ `OPENAI_API_KEY=sk-wrong-key-test-12345`.

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Backup `.env`; sửa key thành giá trị sai; restart app | App khởi động bình thường, không hiện key trên UI | V01 |
| 2 | Hỏi 1 câu tại **http://localhost:8501/** | Thông báo thân thiện «Tạm thời không trả lời được, thử lại», không stack trace | V02 |
| 3 | DevTools Network + Elements + View Page Source, tìm chuỗi key sai hoặc `sk-` | Không thấy key hay dấu vết lỗi kỹ thuật nào trong DOM/Network/Page Source | V03 |
| 4 | Restore `.env.bak`; restart app; hỏi lại 1 câu | Hoạt động bình thường trở lại | V04 |

## 5. Kết quả mong đợi tổng thể

- Không lộ key/stack trace trên UI ở trạng thái key sai.
- Thông báo thân thiện, đúng danh mục mã lỗi (test plan mục 6-C).
- `.env` được khôi phục đúng sau test.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/ST-11/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc (bao gồm cả việc backup/restore `.env` trong terminal), khung hình phải thấy rõ **http://localhost:8501/** khi tương tác app. Lưu `./test_reports/ST-11/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx**, đặt tên `./test_reports/ST-11/screenshots/V01-....png`, …
4. Tạo `./test_reports/ST-11/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/ST-11/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-thiet-lap-key-sai.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/ST-11/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: NFR-04 (không lộ key, không stack trace), SEC-01.
- Vị trí trong test plan: mục 4.6.3 (biên 4.8.5) · checklist S-25 mục 4.8.5.

## 9. Mẫu report.md (Agent điền vào ./test_reports/ST-11/report.md)

```markdown
# Test Report — ST-11: Sai API key — thông báo thân thiện

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
