# SEC-01 — Không lộ API key / stack trace trong UI

| Mục | Giá trị |
|---|---|
| Test case | **SEC-01** |
| Nguồn | Test plan mục 4.6.7 (SEC-01) |
| Nhóm | Security |
| Chu kỳ | C3 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/SEC-01/` |
| Truy vết | NFR-04 · Tasks S-14, S-16 |

## 1. Mục tiêu

Xác minh các lỗi kỹ thuật được che hoàn toàn: không lộ API key, không lộ stack trace, không exception trong DOM/UI ở mọi trạng thái lỗi.

## 2. Tiền điều kiện

1. `docker compose up -d` — Qdrant healthy, mở được `http://localhost:6333/dashboard`.
2. `streamlit run app/main.py` chạy thành công — mở được **http://localhost:8501/**.
3. Kho có ≥1 doc READY (để có thể sửa lỗi chat do key sai).
4. **Backup `.env` vào `.env.bak` và restore sau khi test xong (bắt buộc).**

## 3. Dữ liệu thử nghiệm

- API key sai, ví dụ `OPENAI_API_KEY=sk-wrong-key-test-12345`.

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Backup `.env`; set key sai; restart app | App khởi động bình thường, không hiện key | V01 |
| 2 | Hỏi 1 câu tại **http://localhost:8501/**; chụp thông báo lỗi | Thông báo thân thiện «Tạm thời không trả lời được…», không stack trace | V02 |
| 3 | View Page Source; tìm `sk-`, `OPENAI_API_KEY`, `api_key` | 0 kết quả khớp | V03 |
| 4 | DevTools **Network**: kiểm tra các response sau thất bại | Không có payload chứa key/exception | V04 |
| 5 | DevTools **Elements**: tìm từ «Error»/exception text trên DOM | Chỉ có thông báo thân thiện; không stack trace | V05 |
| 6 | Restore `.env.bak`; restart app; hỏi lại 1 câu | Hoạt động bình thường trở lại | V06 |

## 5. Kết quả mong đợi tổng thể

- Không key, không stack trace xuất hiện trong DOM, Network hay Page Source khi app lỗi.
- `.env` được khôi phục sau test; app hoạt động bình thường trở lại.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/SEC-01/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc (bao gồm cả backup/restore `.env` trong terminal), khung hình phải thấy rõ **http://localhost:8501/** khi tương tác app. Lưu `./test_reports/SEC-01/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx** (kể cả DevTools/Page Source ảnh), đặt tên `./test_reports/SEC-01/screenshots/V01-....png`, …
4. Tạo `./test_reports/SEC-01/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/SEC-01/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-thiet-lap-key-sai.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/SEC-01/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: NFR-04 (không lộ key, không stack trace).
- Vị trí trong test plan: mục 4.6.7 (SEC-01); bản một phần của ST-11, mở rộng kiểm toàn bộ trạng thái lỗi.

## 9. Mẫu report.md (Agent điền vào ./test_reports/SEC-01/report.md)

```markdown
# Test Report — SEC-01: Không lộ API key / stack trace

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
