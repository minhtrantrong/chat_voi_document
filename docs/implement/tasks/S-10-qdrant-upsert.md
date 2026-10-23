# S-10 — Upsert chunk + payload vào Qdrant

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01, US-06, US-08, US-09 |
| Phase | P1 |
| Tầng | INFRA |
| Ước lượng | 0,5d |
| Phụ thuộc | S-05, S-08, S-09 |
| Chặn | S-11, S-15, S-21 |
| Owner gợi ý | Backend |

## 1. Mục tiêu

Ghi danh sách `Chunk` + vector vào Qdrant với point ID xác định, payload đầy đủ để search và trích nguồn. Upsert phải idempotent: chạy lại cùng tài liệu không tạo point trùng.

## 2. Phạm vi

**Làm:**

- `upsert_chunks(doc_id, file_name, chunks, vectors)`.
- Point ID = `uuid5(NAMESPACE_URL, f"{doc_id}:{chunk_index}")`.
- Payload: `doc_id`, `file_name`, `page`, `chunk_index`, `text`, `char_start`, `char_end`.
- Validate số lượng/chiều vector.
- Upsert theo batch, `wait=True`.
- Gọi `ensure_collection()` trước khi ghi.

**Không làm:**

- Chưa search (S-15).
- Chưa versioning/re-index hàng loạt.
- Chưa lưu vector vào SQLite.

## 3. File chính

```text
app/vector_store.py
tests/test_vector_store.py
```

## 4. Đặc tả

```python
import uuid
from qdrant_client.models import PointStruct

def upsert_chunks(
    doc_id: str,
    file_name: str,
    chunks: list[Chunk],
    vectors: list[list[float]],
    *,
    client: QdrantClient | None = None,
    batch_size: int = 128,
) -> None:
    if not chunks:
        return
    if len(chunks) != len(vectors):
        raise ValueError(
            f"Số chunk ({len(chunks)}) khác số vector ({len(vectors)})."
        )

    s = get_settings()
    client = client or get_client()
    ensure_collection(client)

    points: list[PointStruct] = []
    for chunk, vector in zip(chunks, vectors, strict=True):
        if len(vector) != s.embedding_dim:
            raise ValueError(
                f"Vector chunk {chunk.chunk_index} có {len(vector)} chiều, "
                f"cần {s.embedding_dim}."
            )
        point_id = str(
            uuid.uuid5(uuid.NAMESPACE_URL, f"{doc_id}:{chunk.chunk_index}")
        )
        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "doc_id": doc_id,
                    "file_name": file_name,
                    "page": chunk.page,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text,
                    "char_start": chunk.char_start,
                    "char_end": chunk.char_end,
                },
            )
        )

    for i in range(0, len(points), batch_size):
        client.upsert(
            collection_name=s.qdrant_collection,
            points=points[i : i + batch_size],
            wait=True,
        )
```

### 4.1 Quy ước payload

| Field | Kiểu | Dùng cho |
|---|---|---|
| `doc_id` | keyword | filter, delete |
| `file_name` | text | hiển thị nguồn |
| `page` | integer | hiển thị nguồn |
| `chunk_index` | integer | dedupe/point id |
| `text` | text | context cho LLM |
| `char_start` | integer | trích nguồn (tuỳ chọn) |
| `char_end` | integer | trích nguồn (tuỳ chọn) |

> `payload_index` cho `doc_id` đã tạo ở S-05. Không cần index cho các field còn lại.

## 5. Trường hợp biên

- `chunks=[]` → no-op (ingest đã chặn PDF không text).
- Mismatch chunks/vectors → `ValueError` trước khi ghi.
- Vector sai chiều → `ValueError`, không ghi batch nào (validate toàn bộ trước khi upsert).
- Cùng `doc_id` + `chunk_index` upsert lại → ghi đè point cũ, không nhân đôi.
- Qdrant down giữa batch → một số point đã ghi; caller (S-11) phải gọi `delete_document(doc_id)` để dọn.
- `file_name` rất dài/Unicode → Qdrant payload chấp nhận; UI cắt hiển thị.
- `doc_id` không phải UUID → vẫn dùng làm chuỗi hash; point id vẫn là UUID hợp lệ.
- Batch size quá lớn → Qdrant có giới hạn request; 128 là an toàn cho demo.

## 6. Tiêu chí xong

- [ ] Upsert 1 tài liệu → số point = số chunk.
- [ ] Payload đủ field, `page` đúng, `text` khớp chunk.
- [ ] Upsert lại cùng dữ liệu → số point không đổi.
- [ ] Xoá tài liệu (S-05) → không còn point.
- [ ] Không log text/vector.
- [ ] Validate trước khi ghi, tránh ghi nửa vời do lỗi input.

## 7. Test

`tests/test_vector_store.py` (integration):

- `test_upsert_creates_points`.
- `test_upsert_idempotent`.
- `test_payload_fields`.
- `test_mismatch_count_raises`.
- `test_wrong_dimension_raises`.
- `test_empty_chunks_noop`.
- `test_delete_after_upsert`.

Dùng collection test riêng, fake vector cùng chiều `EMBEDDING_DIM` (monkeypatch settings).

## 8. Tham chiếu

- Kế hoạch §5.2, §7.3.
- S-05, S-09, S-11, S-15.
