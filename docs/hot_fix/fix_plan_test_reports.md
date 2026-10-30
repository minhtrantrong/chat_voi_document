# Fix plan từ các test report FAIL

Nguồn: `test_reports/ST-01/report.md`, `test_reports/ST-02/report.md` (chạy 2026-10-23, LLM Ollama).
Lập kế hoạch: 2026-10-28. Chưa sửa code; đây là kế hoạch.

## 1. Điểm danh

Có 2 test report, cả hai đều **FAIL** ở mức tổng. Không có report nào khác trong `test_reports/`.

| Test | Bước FAIL | Nguyên nhân | Lỗi app? |
|---|---|---|---|
| ST-01 | Bước 1 | Tiền điều kiện "kho trống" không thoả (đã có 3 tài liệu) | Không |
| ST-01 | Bước 3 | Fixture `hop-dong.pdf` 1 trang, test case kỳ vọng 32 trang | Không (lỗi dữ liệu test) |
| ST-02 | Bước 1 | Tiền điều kiện "kho trống" không thoả (đã có 4 tài liệu) | Không |
| ST-02 | Bước 2 | `fake.docx` bị chặn nhưng thông báo là tiếng Anh theo MIME, không phải «chỉ hỗ trợ PDF» | **Có** (BUG-ST02-01, S3) |

Các bước còn lại PASS. Bug đã ghi nhận, kể cả bug không làm bước nào fail:

| Bug | Mức | Loại | Mô tả ngắn |
|---|---|---|---|
| BUG-ST01-01 | S3 | Dữ liệu test | Fixture 1 trang so với kỳ vọng 32 trang |
| BUG-ST02-01 | S3 | App | Thông báo file sai định dạng bằng tiếng Anh, không nêu lý do |
| BUG-ST02-02 | S3 | App | Chip lỗi của file bị loại mất sau reset uploader |
| BUG-ST01-02 | S4 | App | Không có card/chip "Đang xử lý" theo từng tài liệu |
| BUG-ST02-03 | S4 | App | Banner lỗi cũ vẫn hiện sau khi xoá tài liệu lỗi |
| OBS-ST01-03 | S4 | App | Uploader ghi "200MB per file", cấu hình là 25 MB |

Hai nhóm FAIL có cách xử lý khác nhau: nhóm môi trường/dữ liệu test (mục 2) và nhóm lỗi app (mục 3).

## 2. Nhóm A: dữ liệu và môi trường test (không sửa code app)

### A1. Fixture `hop-dong.pdf` (BUG-ST01-01, S3)

- **Gốc:** `tests/eval/generate_fixtures.py` gọi `doc.new_page()` một lần trong `_write_pdf`, nên mọi fixture là 1 trang. Test plan (`TestPlan_Simple_Qdrant.md` mục A-01/A-02) mô tả 32 và 12 trang. `PF-01` cũng dựa vào 32 trang.
- **Phương án khuyến nghị:** thêm tham số số trang cho generator để `hop-dong.pdf` ra 32 trang, `bao-gia.pdf` 12 trang. Giữ trang 1 như hiện tại để dataset eval (`tests/eval/dataset.json`) vẫn đúng, các trang sau là nội dung đệm tiếng Việt, không chứa số/ngày có thể gây nhiễu câu hỏi eval.
- **Phương án thay thế:** sửa kỳ vọng trong test plan và test case thành 1 trang. Nhanh hơn nhưng làm PF-01 (đo độ trễ ingest) mất ý nghĩa.
- **Kiểm tra:** `python tests/eval/generate_fixtures.py`, rồi PyMuPDF `page_count == 32`. Chạy lại eval để xác nhận không lệch điểm.

### A2. Tiền điều kiện "kho trống" (ST-01 bước 1, ST-02 bước 1)

- **Gốc:** không có bước dọn môi trường trước khi chạy test; các lần chạy trước để lại dữ liệu (kho hiện có 7 tài liệu READY).
- **Cách xử lý:** thêm bước reset trước mỗi lần chạy ST: xoá `data/` (SQLite + uploads) và collection Qdrant `document_chunks`, hoặc dùng `DATA_DIR` và `QDRANT_COLLECTION` riêng cho test. Ghi lệnh reset vào test case (mục tiền điều kiện) và vào skill `test-report-run`.
- **Lưu ý:** `docker compose down -v` xoá toàn bộ vector (xem README); chỉ dùng khi chắc chắn không cần dữ liệu cũ.

## 3. Nhóm B: lỗi app

Các thay đổi đều ở `app/main.py` trừ B4. Ưu tiên theo mức nghiêm trọng, B1 và B2 nên làm cùng nhau.

### B1. Thông báo file sai định dạng bằng tiếng Việt (BUG-ST02-01, S3)

- **Gốc:** `st.file_uploader(..., type=["pdf"])` ([main.py:100-106](../../app/main.py#L100-L106)) lọc ở phía trình duyệt/Streamlit, nên người dùng chỉ thấy chuỗi tiếng Anh mặc định theo MIME type. App không thấy file bị loại.
- **Cách sửa:** bỏ tham số `type` để mọi file vào được `ingest_many`. Đã có sẵn `validate_filename` ([pdf.py:37](../../app/pdf.py#L37)) raise `PDF_NOT_PDF`, và `errors.py` đã có thông báo tiếng Việt cho mã này. Cân nhắc đổi `ERROR_MESSAGES["PDF_NOT_PDF"]` để nêu rõ "Ứng dụng chỉ hỗ trợ PDF".
- **Tác động:** `ingest_pdf` gọi `validate_filename` trước khi tạo bản ghi, nên file sai định dạng không tạo document row và không ghi disk. Cần kiểm tra thông báo có kèm tên file (hiện `error_message` chỉ thêm tên file cho nhóm `PDF_`; xác nhận bằng test).
- **Rủi ro:** mất lọc loại file ngay ở hộp thoại chọn file của trình duyệt. Chấp nhận được vì thông báo rõ hơn là yêu cầu của FR/AC.

### B2. Giữ dấu vết file bị loại sau khi reset uploader (BUG-ST02-02, S3)

- **Gốc:** sau xử lý, `uploader_nonce += 1` và `st.rerun()` ([main.py:139-140](../../app/main.py#L139-L140)) xoá chip lỗi. Với B1, file sai định dạng sẽ nằm trong `results` và `last_ingest`, nên bug này tự được giải quyết cho trường hợp `fake.docx`: banner lỗi hiển thị qua `_render_last_ingest`.
- **Cần xác nhận lại:** chạy lại ST-02 bước 2 sau B1. Nếu banner có tên file + lý do và còn hiển thị sau rerun thì đóng BUG-ST02-02 cùng B1, không cần sửa riêng.

### B3. Banner lỗi cũ sau khi xoá tài liệu (BUG-ST02-03, S4)

- **Gốc:** `last_ingest` trong session state chỉ bị ghi đè ở lần upload kế tiếp.
- **Cách sửa:** trong nhánh xoá thành công ([main.py:166-172](../../app/main.py#L166-L172)), loại các mục `last_ingest` có `file_name` trùng tài liệu vừa xoá (hoặc xoá cả `last_ingest`). Phương án đơn giản: `st.session_state.last_ingest = []` khi xoá bất kỳ tài liệu nào.
- **Lưu ý:** vì có thể có nhiều bản trùng tên, lọc theo tên file có thể xoá nhầm banner của bản khác; xoá toàn bộ `last_ingest` là an toàn hơn.

### B4. Gợi ý "200MB per file" (OBS-ST01-03, S4)

- **Gốc:** dòng "Limit 200MB per file" do Streamlit tự sinh từ `server.maxUploadSize`, mặc định 200; repo chưa có `.streamlit/config.toml`. `help=` của app chỉ là tooltip.
- **Cách sửa:** tạo `.streamlit/config.toml` với `[server] maxUploadSize = 25`. Giá trị này phải đồng bộ với `MAX_UPLOAD_MB` (config app đọc từ env, còn Streamlit đọc từ file), nên ghi chú trong README/`.env.example` rằng đổi một nơi phải đổi nơi kia.
- **Hệ quả:** Streamlit sẽ chặn file > 25 MB ở phía client với thông báo mặc định (tiếng Anh). Đây là lỗi cùng loại với B1 nhưng hiếm hơn; chấp nhận hoặc đặt `maxUploadSize` cao hơn một chút và để app báo `PDF_TOO_LARGE` bằng tiếng Việt. Cần chốt trước khi làm.

### B5. Chip "Đang xử lý" theo từng tài liệu (BUG-ST01-02, S4)

- **Gốc:** sidebar chỉ được vẽ lại sau `ingest_many` + `st.rerun()`; trong lúc xử lý chỉ có khối `st.status` chung. Bản ghi `PROCESSING` có trong SQLite nhưng UI không thấy.
- **Cách sửa (nếu giữ yêu cầu):** trong `progress_factory`, hiển thị một dòng trạng thái theo tên file (vd. `st.empty()` cho mỗi file, cập nhật bằng nhãn giai đoạn `validating/extracting/chunking/embedding/indexing`). Không cần đổi pipeline: `ProgressFn` đã nhận tên giai đoạn, hiện bị bỏ qua (`_stage`).
- **Khuyến nghị:** làm sau cùng, hoặc đóng với lý do "chấp nhận" nếu yêu cầu không đòi chip theo từng tài liệu. Cần đối chiếu FR-05 trước khi làm: tôi không tìm thấy FR-05 hay "chip" trong `docs/requirements/` bằng tìm kiếm văn bản.

## 4. Thứ tự thực hiện

| # | Việc | Mức | File | Phụ thuộc |
|---|---|---|---|---|
| 1 | A1 fixture 32/12 trang | S3 | `tests/eval/generate_fixtures.py` | — |
| 2 | A2 quy trình reset kho trước test | — | test case, skill `test-report-run` | — |
| 3 | B1 bỏ lọc `type=["pdf"]`, thông báo tiếng Việt | S3 | `app/main.py`, `app/errors.py` | — |
| 4 | B2 xác nhận sau B1 (có thể không cần sửa) | S3 | `app/main.py` | B1 |
| 5 | B3 xoá banner cũ khi xoá tài liệu | S4 | `app/main.py` | — |
| 6 | B4 `.streamlit/config.toml` | S4 | mới | quyết định về thông báo > 25 MB |
| 7 | B5 chip theo từng tài liệu | S4 | `app/main.py` | đối chiếu FR-05 |

## 5. Kiểm thử và đóng bug

- Thêm unit test: `ingest_pdf` với tên file không phải `.pdf` raise `PdfError` mã `PDF_NOT_PDF` và không tạo document row hay file trong `uploads/` (kiểm tra thêm trong `tests/test_ingest.py`).
- `tests/test_app_smoke.py` / `tests/test_ui_state.py`: thêm ca xoá tài liệu thì `last_ingest` bị dọn (B3).
- Chạy `pytest -q -m "not integration"`, `ruff check .`, `mypy app` sau mỗi nhóm thay đổi.
- Chạy lại ST-01 và ST-02 trên kho đã reset (A2) với fixture mới (A1), sinh report mới bằng skill `test-report-run`, kiểm bằng `test-report-check`. Đóng BUG-ST01-01, BUG-ST02-01/02/03 khi bước tương ứng PASS.
- Report cũ giữ nguyên làm bản ghi lịch sử; lưu report chạy lại vào thư mục mới hoặc ghi rõ ngày để phân biệt.

## 6. Việc cần người quyết định

1. A1: sinh fixture 32 trang (khuyến nghị) hay sửa kỳ vọng thành 1 trang?
2. B4: chặn cứng ở 25 MB phía Streamlit (thông báo tiếng Anh) hay để app tự báo `PDF_TOO_LARGE`?
3. B5: có cần chip theo từng tài liệu không, hay đóng BUG-ST01-02 là chấp nhận được?

## 7. Giới hạn của kế hoạch này

- Dựa trên đọc 2 report, `app/main.py`, `app/pdf.py` và cấu trúc repo; chưa chạy lại app hay test.
- Các report chạy với Ollama (`qwen3:1.7b`); các lỗi ở trên không phụ thuộc backend LLM nên việc đổi mặc định sang LM Studio không ảnh hưởng.
- Chưa kiểm tra hành vi Streamlit khi bỏ `type=["pdf"]` (B1) hay khi đặt `maxUploadSize` (B4) bằng cách chạy thật; cần xác nhận khi thực hiện.
