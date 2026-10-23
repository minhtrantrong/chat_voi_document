# Checklist kiểm thử thủ công

**Môi trường**

- OS/browser: ................................
- Python: ....................................
- Model LLM/Embedding: .......................
- Qdrant image: ..............................
- Ngày/người test: ...........................

## 0. Chuẩn bị

- [ ] `docker compose up -d` → Qdrant healthy (image `qdrant/qdrant:v1.20.0`).
- [ ] `cp .env.example .env`; mặc định dùng Ollama (`llama3.1` + `nomic-embed-text`), điền key/model nếu dùng OpenAI.
- [ ] `.venv/bin/python tests/eval/generate_fixtures.py` → có 3 PDF mẫu.
- [ ] `streamlit run app/main.py` → mở `localhost:8501`, không exception.
- [ ] Terminal không có traceback khi tải trang.

## 1. Upload một PDF

- [ ] Kéo `hop-dong.pdf` vào uploader → thấy trạng thái đang xử lý.
- [ ] Chờ xử lý → tài liệu **Sẵn sàng**, số trang/dung lượng đúng.
- [ ] `data/uploads/` có file `{doc_id}.pdf`.
- [ ] Qdrant dashboard có point trong `document_chunks`.
- [ ] Refresh trang → tài liệu vẫn còn.

## 2. Upload nhiều PDF + file lỗi

- [ ] Chọn `hop-dong.pdf`, `bao-gia.pdf`, `fake.docx` → file `.docx` bị chặn.
- [ ] Chọn thêm PDF scan → row **Lỗi** `PDF_NO_TEXT`.
- [ ] Hai PDF hợp lệ đều **Sẵn sàng**, không bị dừng bởi file lỗi.
- [ ] Xoá file lỗi → biến mất khỏi danh sách.
- [ ] Tải lại cùng PDF → tạo tài liệu mới (đúng thiết kế).

## 3. Chat trong tài liệu

- [ ] Hỏi "Hạn chót nộp hồ sơ là ngày nào?" → `30/11/2026`, có `[S1]`.
- [ ] Mở "Nguồn" → đúng `hop-dong.pdf`, trang 1.
- [ ] Hỏi tiếp "Bên A là công ty nào?" → đúng, giữ ngữ cảnh.
- [ ] Câu hỏi dài/tiếng Việt có dấu → không lỗi encoding.
- [ ] Câu trả lời hiện dần (streaming), không treo.

## 4. Ngoài phạm vi

- [ ] "Giá cổ phiếu VNM hôm nay?" → "Không tìm thấy thông tin…".
- [ ] "Thủ đô nước Pháp?" → NOT_FOUND, không bịa.
- [ ] Không hiển thị nguồn khi NOT_FOUND.

## 5. Nhiều tài liệu

- [ ] Upload `bao-gia.pdf` + `quy-dinh.pdf` → READY.
- [ ] "So sánh thời gian giao hàng gói A và thời hạn hợp đồng" → cần cả `bao-gia.pdf` + `hop-dong.pdf`.
- [ ] Mở nguồn → có ≥ 2 tài liệu.
- [ ] Câu chỉ liên quan `quy-dinh.pdf` → nguồn đúng file.

## 6. Xoá tài liệu

- [ ] Bấm Xoá → hiện xác nhận.
- [ ] Bấm Huỷ → tài liệu vẫn còn.
- [ ] Xoá → Xác nhận → tài liệu biến mất.
- [ ] Qdrant không còn point `doc_id` đó.
- [ ] File trong `data/uploads/` đã xoá.
- [ ] Hỏi lại → không còn nguồn tài liệu đã xoá; lịch sử chat đã clear.
- [ ] Xoá tài liệu cuối → chat input disabled.

## 7. Trạng thái biên

- [ ] Chưa upload gì → chat disabled + "Tải PDF đầu tiên".
- [ ] Chỉ có tài liệu lỗi → chat disabled + hướng dẫn.
- [ ] Dừng Qdrant, refresh → banner cảnh báo, không crash.
- [ ] Bật Qdrant lại, upload → hoạt động lại.
- [ ] Sai API key, hỏi → thông báo cấu hình/thử lại, không lộ key.
- [ ] Upload file > 25 MB → báo vượt dung lượng.
- [ ] Upload PDF > 400 trang → báo vượt số trang.
- [ ] Upload PDF mã hoá → `PDF_ENCRYPTED`.
- [ ] Upload PDF scan → `PDF_NO_TEXT`, không READY.
- [ ] Refresh khi đang chat → lịch sử mất, tài liệu còn.
- [ ] Tên file dài/Unicode → không vỡ layout, không XSS.
- [ ] Qdrant restart → tài liệu vẫn search được.

## Ghi nhận bug

| ID | Mô tả | Mức độ | Task liên quan |
|---|---|---|---|
| | | | |
