# SEC-04 — Triển khai an toàn no-auth: localhost + cảnh báo README

| Mục | Giá trị |
|---|---|
| Test case | **SEC-04** |
| Nguồn | Test plan mục 4.6.7 (SEC-04) |
| Nhóm | Security |
| Chu kỳ | C3 |
| Ưu tiên | High |
| URL ứng dụng | **http://localhost:8501/** |
| Thư mục artifact | `./test_reports/SEC-04/` |
| Truy vết | NFR-08 · UAT-11 · Tasks S-01, S-26 |

## 1. Mục tiêu

Xác minh cấu hình triển khai an toàn: app lắng nghe mạng nội bộ (localhost), README có cảnh báo no-auth + hướng dẫn bảo vệ (VPN/reverse proxy); không expose ra Internet ngoài ý muốn.

## 2. Tiền điều kiện

1. `streamlit run app/main.py` đang chạy — mở được **http://localhost:8501/**.
2. Qdrant container healthy — `http://localhost:6333/dashboard`.
3. Không bắt buộc có tài liệu trong kho; app có thể trống.

## 3. Dữ liệu thử nghiệm

- `README.md` (output Task S-26 — chứa mục «Cảnh báo bảo mật»).
- Terminal để chạy lệnh kiểm tra port.

## 4. Các bước thực hiện

| # | Bước | Kỳ vọng | Bằng chứng |
|---|---|---|---|
| 1 | Terminal: `ss -ltnp \| grep -E '8501\|6333'` (hoặc `netstat -ltnp`) | App 8501 + Qdrant 6333 lắng nghe; ghi nhận địa chỉ bind; **ghi chú nếu bind 0.0.0.0 trên mạng chia sẻ** | V01 |
| 2 | Xem `README.md`; xác minh có mục «Cảnh báo bảo mật» no-auth + hướng dẫn VPN/reverse proxy | Cảnh báo rõ ràng: chạy nội bộ/VPN; không expose Internet; thêm auth ở tầng hạ tầng nếu cần | V02 |
| 3 | Mở `http://localhost:6333/dashboard`; ghi nhận trạng thái (không auth) | Dashboard truy cập nội bộ; kèm khuyến nghị không dùng public | V03 |
| 4 | Ghi nhận cấu hình port/firewall vào report | State binds + khuyến nghị bảo vệ được mô tả | V04 |

## 5. Kết quả mong đợi tổng thể

- Port bind + README cung cấp bằng chứng đủ: phạm vi nội bộ, không expose Internet.
- Report ghi lại cấu hình hiện tại để review bảo mật.

## 6. Nhiệm vụ bắt buộc của Agent — Bằng chứng & Artifact

1. Tạo thư mục `./test_reports/SEC-04/` ngay trước khi bắt đầu — tất cả artifact của case này chỉ nằm trong thư mục này.
2. Quay **video toàn bộ quá trình test**: quay liên tục từ trước bước 1 đến khi kết thúc, khung hình phải thấy rõ terminal (port check) và trình duyệt tại **http://localhost:8501/**. Lưu `./test_reports/SEC-04/video.webm` (hoặc `.mp4`).
3. **Chụp screenshot làm bằng chứng cho mỗi bước có mã Vxx** (kể cả ảnh terminal và README), đặt tên `./test_reports/SEC-04/screenshots/V01-....png`, …
4. Tạo `./test_reports/SEC-04/report.md` theo mẫu mục 9: điền Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước, link ảnh + video, bảng bug nếu có, phần ghi môi trường.
5. Nếu một bước FAIL: vẫn chụp bằng chứng, ghi rõ vào report và bảng bug; **không tự sửa code ứng dụng** trong lúc test.

```text
test_reports/SEC-04/
├── video.webm
├── report.md
└── screenshots/
    ├── V01-port-bind.png
    └── ...
```

## 7. Tiêu chí Pass / Fail

- **PASS** khi: mọi bước có mã Vxx đều PASS; đạt kết quả mong đợi mục 5; đủ `report.md` + ảnh + video trong `./test_reports/SEC-04/`.
- **FAIL** khi: bất kỳ bước bắt buộc nào không đạt, hoặc thiếu artifact. Khi FAIL vẫn phải tạo đủ report + bằng chứng và ghi bug vào bảng bug của report.

## 8. Truy vết

- Yêu cầu: NFR-08 (triển khai no-auth có cảnh báo).
- Vị trí trong test plan: mục 4.6.7 (SEC-04).

## 9. Mẫu report.md (Agent điền vào ./test_reports/SEC-04/report.md)

```markdown
# Test Report — SEC-04: Triển khai no-auth an toàn

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
