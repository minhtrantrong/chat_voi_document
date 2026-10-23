# S-05 — Qdrant client, collection và health check

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01, US-04, US-06 |
| Phase | P0 |
| Tầng | INFRA |
| Ước lượng | 0,5d |
| Phụ thuộc | S-02, S-03 |
| Chặn | S-10, S-11, S-21, S-23 |
| Owner gợi ý | Backend |

## 1. Mục tiêu

Khởi tạo Qdrant client, tự tạo collection `document_chunks` đúng chiều vector, tạo payload index cho `doc_id`, kiểm tra health và xoá toàn bộ point của một tài liệu. Đây là nền cho upsert (S-10) và search (S-15).

## 2. Phạm vi

**Làm:**

- `app/vector_store.py`.
- `get_client()` trả `QdrantClient` cấu hình từ `Settings`.
- `ensure_collection()` idempotent.
- `health()` trả bool.
- `delete_document(doc_id)` xoá theo filter.
- Phát hiện collection tồn tại nhưng sai `size` → lỗi hướng dẫn recreate.

**Không làm:**

- Chưa upsert/search (S-10/S-15).
- Chưa quản lý multi-tenant/collection theo user.
- Chưa backup.

## 3. File chính

```text
app/vector_store.py
tests/test_vector_store.py
```

## 4. Đặc tả

### 4.1 Client

```python
from qdrant_client import QdrantClient
from app.config import get_settings

def get_client() -> QdrantClient:
    s = get_settings()
    return QdrantClient(
        url=s.qdrant_url,
        api_key=s.qdrant_api_key or None,
        timeout=10,
    )
```

> Tạo client mới mỗi lần gọi để tránh trạng thái session trong Streamlit. Với test, cho phép inject client qua tham số optional.

### 4.2 Ensure collection

```python
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

def ensure_collection(client: QdrantClient | None = None) -> None:
    s = get_settings()
    client = client or get_client()
    name = s.qdrant_collection

    if not client.collection_exists(name):
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=s.embedding_dim, distance=Distance.COSINE),
        )
        client.create_payload_index(
            collection_name=name,
            field_name="doc_id",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        return

    info = client.get_collection(name)
    vectors = info.config.params.vectors
    current_size = getattr(vectors, "size", None)
    if current_size is not None and current_size != s.embedding_dim:
        raise RuntimeError(
            f"Qdrant collection '{name}' có vector size {current_size}, "
            f"nhưng EMBEDDING_DIM={s.embedding_dim}. "
            "Xoá collection cũ và re-index toàn bộ tài liệu."
        )
```

**Lưu ý API:** với qdrant-client mới, `info.config.params.vectors` có thể là `VectorParams` hoặc dict. Viết helper:

```python
def _vector_size(info) -> int | None:
    vectors = info.config.params.vectors
    if isinstance(vectors, dict):
        first = next(iter(vectors.values()), None)
        return getattr(first, "size", None)
    return getattr(vectors, "size", None)
```

### 4.3 Health

```python
def health(client: QdrantClient | None = None) -> bool:
    try:
        client = client or get_client()
        client.get_collections()
        return True
    except Exception:
        return False
```

Không raise trong UI; caller hiển thị banner "Qdrant chưa sẵn sàng".

### 4.4 Delete theo document

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue, FilterSelector

def delete_document(doc_id: str, client: QdrantClient | None = None) -> None:
    s = get_settings()
    client = client or get_client()
    client.delete(
        collection_name=s.qdrant_collection,
        points_selector=FilterSelector(
            filter=Filter(
                must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
            )
        ),
        wait=True,
    )
```

Idempotent: xoá document không có point → không lỗi.

## 5. Trường hợp biên

- Qdrant chưa chạy → `health()` false; `ensure_collection()` raise lỗi kết nối; UI báo.
- Collection tồn tại sai dimension → raise `RuntimeError` với hướng dẫn.
- Payload index đã tồn tại → `create_payload_index` idempotent (Qdrant trả OK); nếu lỗi, bỏ qua có kiểm soát.
- `qdrant_api_key` rỗng → truyền `None`, không truyền chuỗi rỗng.
- Collection name có ký tự lạ → để Qdrant validate; không tự ý đổi.
- Xoá khi Qdrant down → raise; caller hiển thị lỗi và **không** xoá DB/file (tránh mồ côi).

## 6. Tiêu chí xong

- [ ] `ensure_collection()` tạo collection + payload index lần đầu.
- [ ] Gọi lần 2 không lỗi, không tạo trùng.
- [ ] Sai dimension → lỗi rõ, không tự xoá dữ liệu.
- [ ] `health()` true/false đúng.
- [ ] `delete_document()` xoá đúng point của doc, không ảnh hưởng doc khác.
- [ ] Không hard-code collection name/URL.

## 7. Test

`tests/test_vector_store.py`:

- Unit: `_vector_size` với `VectorParams` và dict.
- Integration (marker `integration`):
  - `test_ensure_collection_creates`.
  - `test_ensure_collection_idempotent`.
  - `test_dimension_mismatch_raises` (tạo collection size khác).
  - `test_health`.
  - `test_delete_only_target_doc` (upsert 2 doc giả, xoá 1).

Dùng collection tên `test_<uuid>` và xoá sau test.

## 8. Tham chiếu

- Kế hoạch §5.2, §7.3.
- S-10, S-15, S-23.
