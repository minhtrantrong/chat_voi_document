# S-11 — Pipeline ingest PDF

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01, US-02, US-03, US-04 |
| Phase | P1 |
| Tầng | APP |
| Ước lượng | 0,75d |
| Phụ thuộc | S-04, S-06, S-07, S-08, S-09, S-10 |
| Chặn | S-12, S-13, S-14, S-24 |
| Owner gợi ý | Backend |

## 1. Mục tiêu

Nối các mảnh thành một luồng duy nhất: nhận file upload → lưu → tạo row `PROCESSING` → validate → extract → chunk → embed → upsert Qdrant → `READY`. Mọi lỗi phải được bắt, map mã lỗi, cập nhật `ERROR` và dọn point dở dang.

## 2. Phạm vi

**Làm:**

- `app/ingest.py`: `ingest_pdf`.
- Lưu file theo `doc_id` (không dùng tên gốc làm path).
- Progress callback cho UI.
- Dọn Qdrant point nếu lỗi sau khi đã upsert.
- Giữ file gốc khi lỗi để người dùng có thể xem/xoá; row ở trạng thái `ERROR`.
- Trả `Document` mới nhất.

**Không làm:**

- Background job/queue.
- Retry toàn bộ pipeline.
- Dedupe theo checksum.
- Xoá file tự động khi lỗi (người dùng bấm Xoá).

## 3. File chính

```text
app/ingest.py
tests/test_ingest.py
```

## 4. Đặc tả

### 4.1 Chữ ký

```python
from collections.abc import BinaryIO, Callable
from pathlib import Path

ProgressFn = Callable[[str, int], None]

def ingest_pdf(
    file_name: str,
    file_obj: BinaryIO,
    *,
    size_bytes: int | None = None,
    progress: ProgressFn | None = None,
) -> Document:
    ...
```

`progress(stage, percent)` với stage: `validating`, `saving`, `extracting`, `chunking`, `embedding`, `indexing`, `done`.

### 4.2 Thuật toán

```python
def ingest_pdf(file_name, file_obj, *, size_bytes=None, progress=None):
    s = get_settings()
    _progress(progress, "validating", 0)

    # 1. Kiểm tra tên + size sớm (không đọc file)
    validate_filename(file_name)
    if size_bytes is not None and size_bytes > s.max_upload_mb * 1024 * 1024:
        raise PdfError(
            "PDF_TOO_LARGE",
            f"Tệp vượt quá {s.max_upload_mb} MB.",
        )

    # 2. Lưu file
    doc_id = uuid.uuid4().hex
    stored_path = s.uploads_dir / f"{doc_id}.pdf"
    _progress(progress, "saving", 5)
    with stored_path.open("wb") as out:
        shutil.copyfileobj(file_obj, out, length=1024 * 1024)

    # 3. Tạo row
    create_document(doc_id, file_name, stored_path, stored_path.stat().st_size)

    try:
        # 4. Validate nội dung
        info = inspect_pdf(
            stored_path,
            max_pages=s.max_pages,
            max_bytes=s.max_upload_mb * 1024 * 1024,
        )
        _progress(progress, "extracting", 15)

        # 5. Extract + chunk
        pages = extract_pages(
            stored_path,
            min_text_chars_per_page=s.min_text_chars_per_page,
        )
        _progress(progress, "chunking", 30)
        chunks = chunk_pages(
            pages,
            size_tokens=s.chunk_size_tokens,
            overlap_tokens=s.chunk_overlap_tokens,
        )
        if not chunks:
            raise PdfError("PDF_NO_TEXT", "Không tạo được đoạn văn bản nào.")

        # 6. Embed
        _progress(progress, "embedding", 40)
        vectors = embed_texts([c.text for c in chunks])

        # 7. Upsert
        _progress(progress, "indexing", 80)
        ensure_collection()
        upsert_chunks(doc_id, file_name, chunks, vectors)

        # 8. Ready
        mark_ready(doc_id, page_count=info.page_count)
        _progress(progress, "done", 100)
        return get_document(doc_id)  # type: ignore[return-value]

    except PdfError as exc:
        mark_error(doc_id, exc.code)
        raise
    except Exception as exc:
        mark_error(doc_id, "INGEST_FAILED")
        # dọn point dở dang, không để search thấy tài liệu lỗi
        try:
            delete_document(doc_id)
        except Exception:
            pass
        raise IngestError("Không xử lý được tài liệu.", detail=str(exc)) from exc
```

### 4.3 Lỗi

```python
class IngestError(Exception):
    def __init__(self, message: str, *, code: str = "INGEST_FAILED", detail: str | None = None):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(message)
```

- `PdfError` giữ nguyên mã (`PDF_*`).
- `EmbeddingError` map thành `EMBEDDING_FAILED` (hoặc giữ code).
- Lỗi Qdrant/khác → `INGEST_FAILED`.
- UI (S-14) map mã → thông điệp.

### 4.4 Progress

- Không cần progress chính xác từng chunk; đủ stage.
- Nếu `progress=None`, bỏ qua.
- Không gọi `st.*` trong `ingest.py` để giữ core độc lập UI.

## 5. Trường hợp biên

- File không phải PDF: `validate_filename` raise trước khi lưu → **không tạo row**. UI hiển thị lỗi ngay.
- File quá lớn: raise trước khi lưu nếu `size_bytes` có; nếu không, lưu rồi `inspect_pdf` phát hiện, row `ERROR`, file còn trên disk.
- PDF mã hoá/scan: row `ERROR`, file còn; người dùng xoá.
- Embedding lỗi giữa batch: row `ERROR`; point có thể đã ghi một phần → `delete_document(doc_id)`.
- Qdrant down: row `ERROR`; file còn; thử lại = upload lại (tạo doc_id mới) hoặc xoá.
- Ghi file lỗi (disk full/quyền): chưa có row; raise `IngestError`; UI báo.
- `create_document` lỗi sau khi lưu file: file mồ côi; cố gắng `stored_path.unlink(missing_ok=True)` trong except.
- Hai session upload cùng lúc: doc_id khác nhau; SQLite WAL; Qdrant xử lý.
- Upload lại cùng file: tạo tài liệu mới (không dedupe) — ghi rõ trong README.

## 6. Tiêu chí xong

- [ ] Upload PDF hợp lệ → row `READY`, `page_count` đúng, point trong Qdrant.
- [ ] PDF scan → row `ERROR` mã `PDF_NO_TEXT`, không có point.
- [ ] PDF mã hoá → row `ERROR` mã `PDF_ENCRYPTED`.
- [ ] Lỗi embedding → row `ERROR`, point dở dang bị xoá.
- [ ] File gốc nằm ở `data/uploads/{doc_id}.pdf`.
- [ ] Không lộ stack trace ra UI.
- [ ] Không log nội dung PDF.

## 7. Test

`tests/test_ingest.py`:

- `test_ingest_valid_pdf_ready` (fake embeddings + Qdrant test collection).
- `test_ingest_scan_pdf_error`.
- `test_ingest_encrypted_error`.
- `test_ingest_not_pdf_no_row` (validate trước khi lưu).
- `test_embedding_failure_marks_error_and_cleans_points`.
- `test_file_saved_with_doc_id_name`.
- `test_progress_called_in_order`.

Dùng `monkeypatch` cho `DATA_DIR`, `EMBEDDING_DIM`, và fake `embed_texts` để không gọi mạng.

## 8. Tham chiếu

- Kế hoạch §2, §6 P1, §7.5.
- S-04, S-06…S-10, S-12, S-14.
