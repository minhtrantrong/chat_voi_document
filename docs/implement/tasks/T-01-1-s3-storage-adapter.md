# T-01-1 — Adapter object storage S3/MinIO

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01 — Tải một tệp PDF lên (P0) |
| Sprint | S2 |
| Tầng | INF |
| Ước lượng | 1d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | PLT-04, PLT-05 |
| Chặn | T-01-4, T-04-4, T-06-3, T-13d-2, PLT-10 |

## Bối cảnh

ADR-008: PDF lưu trong bucket **private**, ứng dụng làm proxy, không có presigned URL ra trình duyệt. Timeout/retry/breaker theo SADD §5.7.6.

## Phạm vi

**Làm:** `app/shared/ports.py` (hoặc `app/documents/ports.py`) định nghĩa `ObjectStoragePort`; `app/infrastructure/storage/s3.py` cài đặt bằng boto3; bản `InMemoryStorage` cho unit test.

## Đặc tả

```python
@dataclass(frozen=True)
class ObjectInfo:
    key: str; size: int; last_modified: datetime

class ObjectStoragePort(Protocol):
    def put(self, key: str, data: BinaryIO, content_type: str) -> None: ...
    def get_to_tempfile(self, key: str) -> Path: ...          # tải về tệp tạm, caller xoá
    def delete(self, key: str) -> None: ...                    # idempotent: 404 coi như thành công
    def exists(self, key: str) -> bool: ...
    def list(self, prefix: str, page_size: int = 1000) -> Iterator[list[ObjectInfo]]: ...
```

Cài đặt `S3Storage`:
- `boto3.client("s3", endpoint_url=S3_ENDPOINT, config=Config(connect_timeout=3, read_timeout=30, retries={"max_attempts": 3, "mode": "standard"}, signature_version="s3v4"))`.
- `put`: `upload_fileobj(data, bucket, key, ExtraArgs={"ContentType": content_type, "ServerSideEncryption": "AES256"})` (bỏ SSE nếu MinIO local chưa bật KMS; điều khiển bằng cờ `S3_SSE`). Dùng multipart tự động của boto3 nên không nạp cả tệp vào RAM.
- `get_to_tempfile`: `download_fileobj` vào `NamedTemporaryFile(delete=False, suffix=".pdf", dir=TMP_DIR)`.
- Circuit breaker đơn giản (`app/shared/breaker.py`, dùng chung với LLM/Embedding): 5 lỗi liên tiếp thì mở 60 s; khi mở ném `Unavailable(ERR_INTERNAL)` ngay.
- Lỗi `NoSuchKey` khi `get` thì ném `NotFound`.
- **Không** log key đầy đủ kèm tên tệp (key chỉ chứa UUID nên log được).

## Tiêu chí xong

- [ ] Integration test với MinIO: put/get/delete/exists/list với tệp 20 MB.
- [ ] `delete` hai lần không lỗi.
- [ ] MinIO dừng: sau 5 lỗi breaker mở, lỗi trả về ngay (< 100 ms).

## Test

`tests/integration/storage/test_s3.py`; `tests/unit/shared/test_breaker.py`.

## Tham chiếu

ADR-008 · SADD §5.7.3, §5.7.6, §5.8.6
