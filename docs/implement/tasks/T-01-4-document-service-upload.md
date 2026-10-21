# T-01-4 — `DocumentService.upload`: kiểm tra, lưu, tạo tài liệu + job

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01 (P0) — AC-01.1, AC-01.2; US-03 — AC-03.1, AC-03.2 |
| Sprint | S2 |
| Tầng | APP |
| Ước lượng | 1.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-01-1, T-01-2, T-01-3, F-04, F-05, F-06, F-07, F-08 |
| Chặn | T-01-5, T-01-6, T-02-1, T-04-4 |

## Bối cảnh

SADD §5.3.2 (SD-01): upload trả quyền điều khiển ≤ 2 s, không chờ extract; tài liệu + job tạo trong **một transaction**; tệp lỗi không chặn tệp khác.

## Phạm vi

**Làm:** `DocumentService.upload` và `_upload_one`, DTO ở `app/documents/schemas.py`, repository `DocumentRepository` (insert, find_active_by_checksum, find_active_by_name, names_like).

**Không làm:** nhánh REPLACE/KEEP_BOTH (T-01-5), song song 3 tệp và giới hạn số tệp (T-02-1), UI (T-01-6).

## Đặc tả

DTO:

```python
class UploadOutcome(StrEnum): ACCEPTED; DUPLICATE; REJECTED; NAME_CONFLICT

@dataclass(frozen=True)
class UploadInput:
    file_name: str; size_bytes: int; stream: BinaryIO
    on_conflict: Literal["REPLACE", "KEEP_BOTH"] | None = None

@dataclass(frozen=True)
class UploadResult:
    file_name: str; outcome: UploadOutcome; document: DocumentDTO | None
    error_code: DocErrorCode | None = None; error_params: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class DocumentDTO:
    id: UUID; file_name: str; uploaded_at: datetime; page_count: int | None; status: DocumentStatus
    error_code: str | None; is_owner: bool; can_delete: bool; can_retry: bool; selectable: bool
```

Chữ ký: `upload(self, actor: Actor, files: Sequence[UploadInput], idempotency_key: str) -> list[UploadResult]`.

`_upload_one(actor, f, limits)` theo thứ tự (mỗi bước thất bại trả `REJECTED` với mã tương ứng):

1. `UploadPolicy.check_name` → `PDF_NOT_PDF`.
2. `UploadPolicy.check_size` → `PDF_TOO_LARGE {limit_mb, actual_mb}`.
3. Đọc 5 byte đầu, `seek(0)`; khác `b"%PDF-"` → `PDF_NOT_PDF`.
4. SHA-256 theo khối 1 MiB, `seek(0)`.
5. Ghi stream ra tệp tạm, `pdf.inspect(tmp)`: `error` → `PDF_CORRUPT`; `needs_pass` → `PDF_ENCRYPTED`; `check_pages` → `PDF_TOO_MANY_PAGES {limit, actual}`.
6. `find_active_by_checksum(owner=actor.user_id, checksum)` có → `DUPLICATE` (kèm DTO cũ).
7. `find_active_by_name(owner, file_name)` có và `on_conflict is None` → `NAME_CONFLICT` (T-01-5 xử lý tiếp).
8. `doc_id = new_id()`, `key = f"documents/{doc_id}/original.pdf"`, `storage.put(key, stream, "application/pdf")` (stream đã `seek(0)`).
9. Transaction: insert `documents` (status `PROCESSING`, `page_count` từ inspect, `visibility = limits.default_visibility`, `version=1`), `jobs.enqueue(tx, "document.ingest", {"documentId": str(doc_id)}, priority=100, max_attempts=3)`, `audit.record(DOCUMENT_UPLOAD, metadata={"size": size_bytes, "pages": page_count})`.
10. Bắt lỗi unique `ux_documents_owner_checksum` (hai request đua) → đọc lại bản ghi thắng, trả `DUPLICATE`; object vừa put để `storage.gc` (PLT-10) dọn.
11. Sau commit: `telemetry.emit("document_uploaded", ...)`, `DOCUMENT_UPLOADS` metric.
12. `finally`: xoá tệp tạm.

Lỗi hạ tầng (S3/DB không khả dụng) trong một tệp: trả `REJECTED` với `error_code=None` và `error_params={"corr_id": ...}`; UI hiện `ERR_INTERNAL`. Không ném ra ngoài làm hỏng cả lô.

`idempotency_key` dùng để log/trace; chống xử lý lại do rerun được làm ở UI (nonce, T-01-6) và bằng chống trùng checksum.

**Không** gọi `UploadedFile.getvalue()` (C-05).

## Tiêu chí xong

- [ ] AC-01.1: PDF hợp lệ → `ACCEPTED`, có 1 dòng `documents(PROCESSING)`, 1 job `document.ingest QUEUED`, 1 object trong bucket, 1 audit.
- [ ] AC-01.2: vượt dung lượng/số trang → `REJECTED` với đúng mã + params; **không** có bản ghi, **không** có object.
- [ ] AC-03.1/03.2: docx → `PDF_NOT_PDF`; mã hoá → `PDF_ENCRYPTED`.
- [ ] Upload lại đúng tệp → `DUPLICATE`, không tạo bản ghi mới.
- [ ] p95 ack 5 × 20 MB ≤ 2 s (MinIO local).

## Test

`tests/integration/documents/test_upload.py`:
`test_valid_pdf_creates_processing_doc_and_job`, `test_upload_rejects_too_large`, `test_upload_rejects_too_many_pages`, `test_docx_rejected`, `test_encrypted_rejected`, `test_duplicate_checksum_returns_existing`, `test_race_same_checksum` (2 thread), `test_storage_down_returns_rejected_internal`, `test_db_failure_after_put_leaves_orphan_only`.
`tests/perf/test_upload_ack.py` (NFR-PERF-03).

## Tham chiếu

SADD §5.3.2, §5.3.9, §5.8.4 · US-01, US-03 · Implement_plan §16 US-01, §14 C-05, C-12
