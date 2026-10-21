# F-02 — Mô hình lỗi: AppError, ErrorCode, lỗi job

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng dùng chung (Implement_plan §15) |
| Sprint | S0 |
| Tầng | DOM |
| Ước lượng | 0.5d |
| Owner gợi ý | Tech Lead |
| Phụ thuộc | PLT-01 |
| Chặn | F-03, mọi service |

## Bối cảnh

SADD §5.5.2: exception domain map sang `AppError(code, user_message, retryable)`; UI map mã sang thông điệp. Quyết định C-16 bổ sung một số mã chưa có trong SADD.

## Phạm vi

**Làm:** `app/shared/errors.py` gồm enum mã lỗi, lớp `AppError` và các lớp con, lỗi dành cho job.

**Không làm:** chuỗi hiển thị (F-03).

## Đặc tả

```python
class ErrorCode(StrEnum):
    # Lỗi hướng người dùng (SADD §5.7.5 + C-16)
    ERR_AUTH_401 = "ERR-AUTH-401"; ERR_AUTH_403 = "ERR-AUTH-403"
    ERR_DOC_404 = "ERR-DOC-404"; ERR_DOC_409 = "ERR-DOC-409"
    ERR_DOC_413 = "ERR-DOC-413"; ERR_DOC_422 = "ERR-DOC-422"
    ERR_Q_EMPTY = "ERR-Q-EMPTY"; ERR_Q_TOO_LONG = "ERR-Q-TOO-LONG"
    ERR_NO_READY_DOC = "ERR-NO-READY-DOC"
    ERR_RATE_LIMIT = "ERR-RATE-LIMIT"; ERR_BUDGET = "ERR-BUDGET"
    ERR_REDIS_UNAVAILABLE = "ERR-REDIS-UNAVAILABLE"
    ERR_LLM_UNAVAILABLE = "ERR-LLM-UNAVAILABLE"; ERR_LLM_TIMEOUT = "ERR-LLM-TIMEOUT"
    ERR_INTERNAL = "ERR-INTERNAL"

class DocErrorCode(StrEnum):       # lưu vào documents.error_code / answers.error_code (SADD §10.4 + C-16)
    PDF_NOT_PDF = "PDF_NOT_PDF"; PDF_ENCRYPTED = "PDF_ENCRYPTED"; PDF_CORRUPT = "PDF_CORRUPT"
    PDF_NO_TEXT = "PDF_NO_TEXT"; PDF_TOO_MANY_PAGES = "PDF_TOO_MANY_PAGES"; PDF_TOO_LARGE = "PDF_TOO_LARGE"
    EXTRACT_FAILED = "EXTRACT_FAILED"; EMBED_FAILED = "EMBED_FAILED"; INDEX_FAILED = "INDEX_FAILED"
    PURGE_PARTIAL = "PURGE_PARTIAL"; WORKER_LOST = "WORKER_LOST"
    LLM_TIMEOUT = "LLM_TIMEOUT"; LLM_UNAVAILABLE = "LLM_UNAVAILABLE"
    CITATION_INVALID = "CITATION_INVALID"; REDIS_UNAVAILABLE = "REDIS_UNAVAILABLE"

RETRYABLE_DOC_ERRORS = frozenset({EXTRACT_FAILED, EMBED_FAILED, INDEX_FAILED, WORKER_LOST})   # C-14

class AppError(Exception):
    def __init__(self, code: ErrorCode, params: Mapping[str, Any] | None = None,
                 *, retryable: bool = False) -> None: ...
    code: ErrorCode; params: dict[str, Any]; retryable: bool

class NotFound(AppError): ...       # mặc định ERR_DOC_404
class Forbidden(AppError): ...      # ERR_AUTH_403
class Invalid(AppError): ...
class Conflict(AppError): ...
class RateLimited(AppError): ...    # retryable=True, params["retry_after"]
class Unavailable(AppError): ...    # retryable=True

class PermanentJobError(Exception):  # worker: FAILED, không retry
    def __init__(self, code: DocErrorCode, detail: str = "") -> None: ...
class RetryableJobError(Exception):  # worker: retry theo backoff
    def __init__(self, code: DocErrorCode, detail: str = "") -> None: ...
```

Quy tắc:
- `params` chỉ chứa giá trị **không nhạy cảm** (giới hạn, số đếm, tên tệp người dùng tự tải lên được phép vì chỉ hiển thị lại cho chính họ). **Không** log `params["file_name"]` (F-12 lọc).
- `str(AppError)` trả về mã lỗi, không trả nội dung.
- Ngoại lệ lạ trong UI được bắt ở một chỗ (`app/ui/state.py::run_safely`) và hiển thị `ERR_INTERNAL` kèm `corr_id`.

## Tiêu chí xong

- [ ] Mọi mã ở SADD §5.7.5, §10.4 và C-16 có trong enum.
- [ ] Mypy strict xanh.

## Test

`tests/unit/shared/test_errors.py`: `RateLimited` có `retryable=True`; `RETRYABLE_DOC_ERRORS` đúng danh sách C-14; `str()` không lộ params.

## Tham chiếu

SADD §5.5.2, §5.7.5, §10.4 · Implement_plan §14 C-14, C-16
