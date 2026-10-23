# Test Report — ST-02: Upload nhiều PDF + file lỗi + trùng tên

- **Agent / người test:** Claude Code (Opus 5.5), chạy cho Minh Tran · **Ngày:** 2026-10-23 (21:23:03–21:24:20, giờ máy)
- **Môi trường:** OS: Ubuntu 26.04 LTS (Linux 7.0.0-38) · Python: 3.14.4 · Streamlit 1.66.1 · Qdrant image: `qdrant/qdrant:v1.20.0` (healthy) · LLM: `qwen3:1.7b` (Ollama) · Embedding: `nomic-embed-text` (768 chiều, Ollama) · Browser: Chrome for Testing 155 headless, điều khiển bằng `agent-browser` 0.39.2, viewport 1280×900
- **App URL:** http://localhost:8501/
- **Kết quả tổng:** **FAIL**. Có 2 lý do: (1) bước 1 không đúng tiền điều kiện vì kho không trống; (2) bước 2 chặn đúng `fake.docx` nhưng thông báo là chữ tiếng Anh mặc định của Streamlit ("…files are not allowed"), không phải «chỉ hỗ trợ PDF». Thông báo này cũng mất ngay sau khi lô được xử lý xong. Các ý chính còn lại đều đạt: file lỗi không chặn các PDF hợp lệ, `scan.pdf` báo `PDF_NO_TEXT`, xoá được file lỗi, tải lại trùng tên tạo bản ghi mới.

## Sai lệch so với tiền điều kiện / dữ liệu thử nghiệm

| Mục | Yêu cầu trong test case | Thực tế |
|---|---|---|
| Kho `data/` | Trống | Còn 4 tài liệu READY từ ST-01: `hop-dong.pdf` ×2, `bao-gia.pdf` ×1, `quy-dinh.pdf` ×1. Người phụ trách chọn **giữ nguyên dữ liệu**. Bước 6 vì vậy đánh giá trên các bản ghi **mới tạo trong ST-02**. |
| `hop-dong.pdf`, `bao-gia.pdf` (A-01, A-02) | Fixture hợp lệ | Copy từ `tests/eval/fixtures/` sang `test-data/`. Mỗi file 1 trang (xem BUG-ST01-01 ở ST-01). |
| `fake.docx` | Sai định dạng | Tự tạo: file OOXML (zip) tối giản, đuôi `.docx`, 578 byte (`test-data/fake.docx`). |
| `scan.pdf` (A-04) | PDF chỉ có ảnh | Tự tạo bằng PyMuPDF: 1 trang chỉ có ảnh raster, `get_text()` trả về chuỗi rỗng, 2,8 MB (`test-data/scan.pdf`). |
| Thao tác "chọn file" | Chọn qua hộp thoại | Dùng `agent-browser upload` để gán file vào `input[type=file]` của uploader. Bước 2 gán cả 3 file trong một lần. |
| URL trên khung hình | Thấy thanh địa chỉ | `agent-browser record` chỉ quay vùng nội dung trang, không quay thanh địa chỉ. Vì vậy tôi gắn một nhãn cố định ở góc phải dưới, hiển thị `location.href` (cập nhật mỗi 0,5 giây). Nhãn được thêm bằng JS phía trình duyệt, không sửa code app. Nhãn có trong video và trong mọi ảnh. |
| Ảnh V06 | Toàn bộ danh sách | Danh sách dài hơn màn hình, nên tôi đặt tạm `zoom: 0.42` cho sidebar để chụp đủ 7 card trong một ảnh, rồi trả lại như cũ. |

## Kết quả từng bước

| # | Bước | Kỳ vọng | Thực tế | Kết quả | Ảnh |
|---|---|---|---|---|---|
| 1 | Mở http://localhost:8501/ với kho trống | Trang render bình thường | Trang render, không có `stException` hay "Traceback". Sidebar có 4 tài liệu cũ đều "✅ Sẵn sàng", tức kho **không trống**. | **FAIL** (tiền điều kiện không thoả; app render đúng) | [V01](screenshots/V01-trang-ban-dau.png) |
| 2 | Chọn đồng thời `hop-dong.pdf` + `bao-gia.pdf` + `fake.docx` | `fake.docx` bị chặn với thông báo «chỉ hỗ trợ PDF», nêu tên file; 2 PDF tiếp tục xử lý | Uploader đánh dấu `fake.docx` màu đỏ, có icon lỗi. Nội dung lỗi trong DOM là `Error: application/vnd.openxmlformats-officedocument.wordprocessingml.document files are not allowed.`: tiếng Anh, chỉ nêu MIME type. Trên ảnh chỉ thấy chip đỏ và icon, không thấy dòng chữ này. App bỏ qua file docx và hiện "Đang xử lý **2** tệp…". Hai PDF xử lý xong ("hop-dong.pdf: xử lý xong.", "bao-gia.pdf: xử lý xong.") và đều READY (`f2a84f28…`, `532b68fe…`, mỗi bản 1 point trong Qdrant). Sau khi xử lý, uploader được reset, nên chỗ báo lỗi của `fake.docx` **biến mất** và không có thông báo nào còn lại (ảnh V02b). | **FAIL** (chặn đúng và không chặn file hợp lệ, nhưng thông báo sai ngôn ngữ/nội dung và không còn lại sau xử lý) | [V02](screenshots/V02-thong-bao-file-sai.png), [V02b](screenshots/V02b-sau-xu-ly-2-pdf.png) |
| 3 | Chọn thêm `scan.pdf` | Row riêng với trạng thái **Lỗi**, mã `PDF_NO_TEXT` | Có card riêng `scan.pdf` ("2.8 MB · tạo 2026-10-23", **❌ Lỗi**) với thông điệp "PDF không có văn bản để tìm kiếm (có thể là PDF scan). Ứng dụng chưa hỗ trợ OCR.". Banner phía trên ghi tên file + lý do. SQLite: `status = ERROR`, `error_code = PDF_NO_TEXT` (`6f5d3191…`). UI hiển thị thông điệp ứng với mã, không hiện chuỗi mã. | **PASS** | [V03](screenshots/V03-scan-loi-pdf-no-text.png) |
| 4 | Bấm Xoá trên file lỗi | File lỗi biến mất khỏi danh sách | Bấm "Xoá" rồi "Xác nhận": card `scan.pdf` biến mất. SQLite còn 0 bản ghi `scan.pdf`, `data/uploads/` không còn file, Qdrant 0 point. Banner lỗi "scan.pdf: PDF không có văn bản…" của lần upload trước **vẫn hiển thị** dù tài liệu đã bị xoá (BUG-ST02-03). | **PASS** (kèm ghi chú) | [V04](screenshots/V04-xoa-file-loi.png) |
| 5 | Tải lại `hop-dong.pdf` lần 2 (trùng tên) | Tạo bản ghi thứ hai cho hop-dong.pdf (không dedupe) | "hop-dong.pdf: xử lý xong." App tạo bản ghi mới `98069519…` (READY, 1 point Qdrant, file `data/uploads/98069519….pdf`), tách biệt với `f2a84f28…` ở bước 2. Không có cảnh báo trùng tên, không ghi đè. | **PASS** | [V05](screenshots/V05-hop-dong-lan-2.png) |
| 6 | Xem lại tổng thể danh sách | 2 bản hop-dong + 1 bản bao-gia đều **Sẵn sàng** | Các bản ghi mới của ST-02 gồm `hop-dong.pdf` ×2 (`f2a84f28…`, `98069519…`) và `bao-gia.pdf` ×1 (`532b68fe…`), tất cả "✅ Sẵn sàng". Cả danh sách có 7 card (gồm 4 bản cũ: hop-dong ×4, bao-gia ×2, quy-dinh ×1), tất cả Sẵn sàng. Không có traceback. | **PASS** (đánh giá trên bản ghi mới, vì kho ban đầu không trống) | [V06](screenshots/V06-tong-the-danh-sach.png) |

## Kết quả mong đợi tổng thể (mục 5)

| Tiêu chí | Kết quả |
|---|---|
| File lỗi không chặn các file hợp lệ trong cùng một lô | **Đạt**: `fake.docx` bị loại, 2 PDF cùng lô vẫn READY. `scan.pdf` lỗi không ảnh hưởng các tài liệu khác. |
| Thông báo lỗi nêu tên file + lý do | **Đạt một phần**: `scan.pdf` đạt (tên file + lý do tiếng Việt). `fake.docx` không đạt: chỉ có chip đỏ, lý do là chữ tiếng Anh theo MIME type, và mất sau khi lô xử lý xong. |
| Re-upload trùng tên tạo bản ghi mới | **Đạt** |

- **Video:** [./video.webm](video.webm): 79,4 giây, 1280×900, 15 fps, VP8. Quay liên tục từ lúc mở http://localhost:8501/ (trước bước 1) đến sau bước 6. URL hiển thị bằng nhãn ở góc phải dưới.
- **Bug phát hiện:**

| Bug ID | Mô tả | Mức (S1–S4) | Ảnh |
|---|---|---|---|
| BUG-ST02-01 | File sai định dạng (`fake.docx`) bị chặn bởi bộ lọc `type=["pdf"]` của `st.file_uploader` (`app/main.py`). Người dùng chỉ thấy thông báo mặc định của Streamlit bằng tiếng Anh, theo MIME type (`application/vnd.openxmlformats-officedocument.wordprocessingml.document files are not allowed.`), thay vì thông báo tiếng Việt «chỉ hỗ trợ PDF» như AC-02.2/FR-03. Trên màn hình chỉ thấy chip đỏ, không thấy lý do. | S3 | [V02](screenshots/V02-thong-bao-file-sai.png) |
| BUG-ST02-02 | Khi lô có cả file hợp lệ, uploader được reset sau xử lý (`uploader_nonce += 1` + `st.rerun()`). Chip lỗi của `fake.docx` biến mất, và `last_ingest` chỉ chứa kết quả của 2 PDF. Người dùng không còn dấu vết nào cho biết file docx đã bị bỏ qua. | S3 | [V02b](screenshots/V02b-sau-xu-ly-2-pdf.png) |
| BUG-ST02-03 | Sau khi xoá tài liệu lỗi `scan.pdf`, banner lỗi của lần upload trước (`st.session_state.last_ingest`) vẫn hiển thị. Banner này chỉ mất ở lần upload tiếp theo. | S4 | [V04](screenshots/V04-xoa-file-loi.png) |
| OBS-ST01-03 (lặp lại) | Dòng gợi ý của uploader ghi "200MB per file", trong khi giới hạn cấu hình là 25 MB. | S4 | [V01](screenshots/V01-trang-ban-dau.png) |

## Ghi chú

- Không sửa code ứng dụng trong lúc test.
- Dữ liệu test nằm trong [test-data/](test-data/) để chạy lại được.
- Dữ liệu phát sinh sau test, vẫn còn trong SQLite + Qdrant + `data/uploads/`: `f2a84f28…` (hop-dong.pdf), `532b68fe…` (bao-gia.pdf), `98069519…` (hop-dong.pdf). Kho hiện có 7 tài liệu READY, 7 point trong `document_chunks`. Bản `scan.pdf` đã được xoá ở bước 4.
- Muốn chạy lại đúng tiền điều kiện thì cần làm trống kho trước (xoá các tài liệu qua nút "Xoá").
