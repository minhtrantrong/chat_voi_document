# Test Report — ST-01: Upload 1 PDF hợp lệ

- **Agent / người test:** Claude Code (Opus 5.5), chạy cho Minh Tran · **Ngày:** 2026-10-23 (21:03:28–21:03:53, giờ máy)
- **Môi trường:** OS: Ubuntu 26.04.1 LTS (Linux 7.0.0-38, Wayland/XWayland) · Python: 3.14.4 · Streamlit 1.66.1 · Qdrant image: `qdrant/qdrant:v1.20.0` (healthy) · LLM: `qwen3:1.7b` (Ollama) · Embedding: `nomic-embed-text` (768 chiều, Ollama) · Browser: Google Chrome 155.0.8059.84 (headed, điều khiển qua Playwright)
- **App URL:** http://localhost:8501/
- **Kết quả tổng:** **FAIL** — bước 1 không đúng tiền điều kiện (kho không trống) và bước 3 không đạt kỳ vọng "32 trang" vì fixture chỉ có 1 trang. Luồng upload → READY và đồng bộ 3 kho (SQLite + Qdrant + disk) hoạt động đúng.

## Sai lệch so với tiền điều kiện / dữ liệu thử nghiệm

| Mục | Yêu cầu trong test case | Thực tế |
|---|---|---|
| Kho `data/` | Trống | Đã có 3 tài liệu READY (`hop-dong.pdf`, `bao-gia.pdf`, `quy-dinh.pdf`), 3 file trong `data/uploads/`, 3 points trong Qdrant. Người phụ trách chọn **giữ nguyên dữ liệu** và test tiếp. |
| `hop-dong.pdf` (fixture A-01) | 32 trang, text tiếng Việt | **1 trang**, text tiếng Việt (kiểm tra bằng PyMuPDF: `page_count = 1`) |
| Thao tác "kéo-thả" | Kéo-thả bằng tay | Mô phỏng bằng sự kiện `dragenter/dragover/drop` (DataTransfer) trên vùng `stFileUploaderDropzone`; uploader nhận file như khi kéo-thả thật. |
| Ảnh bước 4 (terminal) | Chụp cửa sổ terminal | Lệnh `ls -l data/uploads/` chạy thật trong thư mục project; output được hiển thị trong một tab Chrome dạng terminal rồi chụp (môi trường Wayland không chụp được cửa sổ terminal riêng). |

## Kết quả từng bước

| # | Bước | Kỳ vọng | Thực tế | Kết quả | Ảnh |
|---|---|---|---|---|---|
| 1 | Mở http://localhost:8501/ khi kho trống | Trang render không exception; sidebar TÀI LIỆU rỗng; chat disabled | Trang render, không có exception/traceback. Sidebar có **3** tài liệu cũ, ô chat **enabled** (vì đã có tài liệu READY). Đúng với trạng thái dữ liệu thực tế, nhưng không đạt kỳ vọng "kho trống". | **FAIL** (tiền điều kiện không thoả) | [V01](screenshots/V01-trang-ban-dau.png) |
| 2 | Kéo-thả `hop-dong.pdf` vào uploader | Xuất hiện chip **Đang xử lý** (icon + nhãn) | Hiện khối trạng thái có spinner + nhãn **"Đang xử lý 1 tệp…"** ngay sau khi thả file. SQLite ghi bản ghi `2bebffb5…` với `status = PROCESSING` lúc 21:03:36. Card riêng của tài liệu với chip "⏳ Đang xử lý" không xuất hiện trên UI (xem BUG-ST01-02). | **PASS** (kèm ghi chú) | [V02](screenshots/V02-chip-dang-xu-ly.png) |
| 3 | Chờ xử lý xong | Chip chuyển **Sẵn sàng**; hiển thị đúng số trang 32 | Sau ~2 giây: thông báo "hop-dong.pdf: xử lý xong.", card mới hiện **"✅ Sẵn sàng"**, meta **"1 trang · 38 KB"**. SQLite: `status = READY`, `page_count = 1`. App đếm đúng số trang thật của file, nhưng không khớp kỳ vọng 32 trang (lỗi dữ liệu test, BUG-ST01-01). | **FAIL** (sai fixture; app đúng) | [V03](screenshots/V03-chip-san-sang.png) |
| 4 | Terminal: `ls -l data/uploads/` | Có file mới dạng `{doc_id}.pdf` | Có file mới `2bebffb5d7064dffbd44a17507c87433.pdf` (38626 byte, 21:03), khớp `doc_id` mới trong SQLite. | **PASS** | [V04](screenshots/V04-ls-data-uploads.png) |
| 5 | Qdrant dashboard → collection `document_chunks` | Có points mới; payload có `doc_id, file_name, page, chunk_index, text` | Tổng points 3 → **4**; có 1 point mới với `doc_id = 2bebffb5…`. Payload có `doc_id, file_name="hop-dong.pdf", page=1, chunk_index=0, text`, kèm `char_start`, `char_end`. Vector dài 768. | **PASS** | [V05](screenshots/V05-qdrant-points.png) |
| 6 | Refresh trình duyệt tại http://localhost:8501/ | Tài liệu vẫn còn trong danh sách (đọc từ SQLite) | Sau reload, sidebar vẫn có `hop-dong.pdf` mới (đầu danh sách, "✅ Sẵn sàng", "1 trang") cùng 3 tài liệu cũ. Không có traceback. | **PASS** | [V06](screenshots/V06-sau-refresh.png) |

## Kết quả mong đợi tổng thể (mục 5)

| Tiêu chí | Kết quả |
|---|---|
| Upload → READY đúng trạng thái; page_count đúng | Trạng thái PROCESSING → READY đúng. `page_count = 1` đúng với file thật, **không khớp** kỳ vọng 32 trong test case. |
| Đồng bộ 3 kho: SQLite + Qdrant + disk | **Đạt**: cùng `doc_id = 2bebffb5d7064dffbd44a17507c87433` có ở SQLite (`READY`), Qdrant (1 point) và disk (`data/uploads/2bebffb5….pdf`). |
| Danh sách còn sau refresh | **Đạt** |
| Không có traceback trên UI | **Đạt** (kiểm tra `stException` và chữ "Traceback" ở bước 1, 3, 6) |

- **Video:** [./video.mp4](video.mp4) — 22,7 giây, 1280×900, 10 fps. Quay liên tục cả cửa sổ Chrome (có thanh địa chỉ `localhost:8501`) từ trước bước 1 tới sau bước 6; bước 4–5 mở ở tab khác trong cùng cửa sổ.
- **Bug phát hiện:**

| Bug ID | Mô tả | Mức (S1–S4) | Ảnh |
|---|---|---|---|
| BUG-ST01-01 | Dữ liệu test sai: fixture `tests/eval/fixtures/hop-dong.pdf` chỉ có 1 trang, nhưng test case ST-01 (fixture A-01) mô tả 32 trang. Không kiểm được tiêu chí "hiển thị đúng 32 trang". Cần sửa fixture hoặc sửa kỳ vọng trong test case. | S3 | [V03](screenshots/V03-chip-san-sang.png) |
| BUG-ST01-02 | Trong lúc xử lý, UI chỉ hiện khối trạng thái chung "Đang xử lý 1 tệp…" (spinner). Card của tài liệu với chip "⏳ Đang xử lý" không bao giờ hiện, vì danh sách sidebar chỉ được vẽ lại sau khi ingest xong (`app/main.py` render danh sách sau `ingest_many` + `st.rerun()`). Dù vậy SQLite vẫn có bản ghi `PROCESSING`. Ảnh hưởng nhẹ tới FR-05 nếu yêu cầu chip theo từng tài liệu. | S4 | [V02](screenshots/V02-chip-dang-xu-ly.png) |
| OBS-ST01-03 | (Quan sát, ngoài phạm vi ST-01) Dòng gợi ý của uploader ghi "200MB per file", trong khi cấu hình `MAX_UPLOAD_MB=25` (tooltip "?" ghi đúng 25 MB). Dễ gây hiểu nhầm cho người dùng. | S4 | [V03](screenshots/V03-chip-san-sang.png) |

## Ghi chú

- Không sửa code ứng dụng trong lúc test.
- Dữ liệu phát sinh sau test: tài liệu mới `2bebffb5d7064dffbd44a17507c87433` (`hop-dong.pdf`) vẫn còn trong SQLite, Qdrant và `data/uploads/`. Kho hiện có 4 tài liệu, trong đó `hop-dong.pdf` có 2 bản.
- Để chạy lại đúng tiền điều kiện cần làm trống kho trước (xoá 4 tài liệu qua nút "Xoá" trên UI) và thay fixture bằng file 32 trang.
