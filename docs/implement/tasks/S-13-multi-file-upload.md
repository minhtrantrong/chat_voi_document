# S-13 — Upload nhiều file, cô lập lỗi từng file

| Thuộc tính | Giá trị |
|---|---|
| Story | US-02, US-03 |
| Phase | P1 |
| Tầng | APP + UI |
| Ước lượng | 0,25d |
| Phụ thuộc | S-12 |
| Chặn | S-25 |
| Owner gợi ý | Full-stack |

## 1. Mục tiêu

Khi người dùng chọn nhiều PDF, xử lý **tuần tự**, mỗi file có kết quả riêng. Một file lỗi không dừng các file còn lại, và UI tổng hợp được bao nhiêu thành công/thất bại.

## 2. Phạm vi

**Làm:**

- Hàm `ingest_many(files)` trong `app/ingest.py` (không phụ thuộc Streamlit).
- `IngestResult(file_name, ok, document, error)`.
- UI hiển thị trạng thái từng file + summary.
- Giữ thứ tự file như người dùng chọn.
- Chỉ tăng uploader nonce sau khi xử lý hết.

**Không làm:**

- Xử lý song song (tránh tranh chấp SQLite/Qdrant và khó hiển thị).
- Retry tự động từng file.
- Giới hạn số file cứng (có thể thêm `MAX_FILES_PER_UPLOAD=10` nếu cần).

## 3. File chính

```text
app/ingest.py
app/main.py
tests/test_ingest_many.py
```

## 4. Đặc tả

### 4.1 DTO

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class IngestResult:
    file_name: str
    ok: bool
    document: Document | None = None
    error: Exception | None = None
```

### 4.2 Hàm

```python
def ingest_many(
    files: list[tuple[str, BinaryIO, int | None]],
    *,
    progress_factory: Callable[[str], ProgressFn] | None = None,
) -> list[IngestResult]:
    results: list[IngestResult] = []
    for file_name, file_obj, size_bytes in files:
        progress = progress_factory(file_name) if progress_factory else None
        try:
            doc = ingest_pdf(
                file_name,
                file_obj,
                size_bytes=size_bytes,
                progress=progress,
            )
            results.append(IngestResult(file_name, True, document=doc))
        except Exception as exc:
            results.append(IngestResult(file_name, False, error=exc))
    return results
```

> `files` là list tuple thay vì `UploadedFile` để core không import Streamlit. UI map `[(f.name, f, f.size) for f in uploaded]`.

### 4.3 UI

```python
if uploaded:
    results = ingest_many(
        [(f.name, f, f.size) for f in uploaded],
        progress_factory=lambda name: make_progress(name),
    )
    ok = sum(r.ok for r in results)
    fail = len(results) - ok
    if fail == 0:
        st.success(f"Đã xử lý {ok} tệp.")
    else:
        st.warning(f"Đã xử lý {ok} tệp, {fail} tệp lỗi.")
        for r in results:
            if not r.ok:
                st.error(error_message(r.error, r.file_name))
    st.session_state.uploader_nonce += 1
    st.rerun()
```

**Lưu ý:** nếu `st.rerun()` ngay, các `st.error` ở trên có thể biến mất. Hai cách:

1. Lưu summary vào `st.session_state["last_ingest_results"]`, hiển thị sau rerun.
2. Không rerun ngay; hiển thị kết quả, người dùng tự tải lại. Nhưng uploader còn file → có thể ingest lặp.

**Chọn cách 1:** lưu list `(file_name, ok, code)` vào session, rerun, render ở đầu sidebar. Xoá sau khi người dùng bấm "Đóng" hoặc sau lần upload tiếp theo.

```python
st.session_state.last_ingest = [
    {"file_name": r.file_name, "ok": r.ok, "code": getattr(r.error, "code", None)}
    for r in results
]
```

## 5. Trường hợp biên

- 0 file → không gọi ingest.
- 1 file lỗi giữa danh sách → file sau vẫn chạy.
- Tất cả lỗi → summary 0 thành công, N lỗi.
- Hai file cùng tên → vẫn tạo 2 doc_id; hiển thị trùng tên, có thể phân biệt bằng ngày/ID (không cần).
- File quá lớn → lỗi riêng, không lưu.
- Upload 10 file lớn → UI chờ lâu; hiển thị progress từng file; cân nhắc giới hạn 5–10 file.
- Một file làm app crash (lỗi không bắt được) → `except Exception` trong `ingest_many` bắt; nếu lỗi hệ thống (MemoryError) có thể không; chấp nhận.
- Người dùng đóng tab giữa chừng → request dừng; file đã lưu có thể còn; row PROCESSING mồ côi. Ghi chú: có thể thêm cleanup thủ công; ngoài phạm vi.

## 6. Tiêu chí xong

- [ ] Chọn 3 file (2 hợp lệ, 1 lỗi) → 2 `READY`, 1 `ERROR`, không dừng giữa chừng.
- [ ] Summary đúng số thành công/lỗi.
- [ ] Thứ tự file giữ nguyên.
- [ ] Uploader nonce tăng một lần sau khi xử lý xong.
- [ ] Kết quả lỗi còn hiển thị sau rerun (session state).
- [ ] Không xử lý song song.

## 7. Test

`tests/test_ingest_many.py`:

- `test_all_success`.
- `test_one_failure_does_not_stop_others`.
- `test_all_failure`.
- `test_order_preserved`.
- `test_empty_list`.

Dùng fake `ingest_pdf` (monkeypatch) để không cần PDF/Qdrant thật.

## 8. Tham chiếu

- Kế hoạch §1.2 US-02, §6 P1.
- S-11, S-12, S-14.
