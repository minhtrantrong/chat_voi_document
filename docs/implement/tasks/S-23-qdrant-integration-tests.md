# S-23 — Integration test với Qdrant

| Thuộc tính | Giá trị |
|---|---|
| Story | Chất lượng (US-01, US-06, US-08, US-09) |
| Phase | P3 |
| Tầng | TEST |
| Ước lượng | 0,5d |
| Phụ thuộc | S-05, S-10, S-11 |
| Chặn | S-26 |
| Owner gợi ý | Backend |

## 1. Mục tiêu

Kiểm chứng hành vi thật của Qdrant: tạo collection, payload index, upsert idempotent, search có filter/ngưỡng, xoá theo tài liệu và phát hiện sai dimension. Test phải **skip sạch** khi Qdrant không chạy, để `pytest` mặc định vẫn xanh.

## 2. Phạm vi

**Làm:**

- `tests/test_vector_store.py` (hoặc `tests/integration/test_qdrant.py`).
- Marker `@pytest.mark.integration`.
- Fixture kiểm tra Qdrant, tạo collection tên duy nhất, cleanup.
- Test ensure/upsert/search/delete/dimension/health.
- Dùng vector giả, không gọi embedding API.

**Không làm:**

- Test hiệu năng/load.
- Test Qdrant Cloud/auth.
- Test backup/restore.
- Test đồng thời nhiều client.

## 3. File chính

```text
tests/integration/test_qdrant.py
tests/conftest.py
```

## 4. Đặc tả

### 4.1 Fixture

```python
import os
import uuid
import pytest
from qdrant_client import QdrantClient

@pytest.fixture(scope="session")
def qdrant_url() -> str:
    url = os.getenv("QDRANT_URL", "http://localhost:6333")
    try:
        QdrantClient(url=url, timeout=2).get_collections()
    except Exception:
        pytest.skip("Qdrant không chạy; bỏ qua integration test.")
    return url

@pytest.fixture
def qdrant_settings(qdrant_url, monkeypatch):
    from app.config import get_settings
    name = f"test_{uuid.uuid4().hex[:12]}"
    monkeypatch.setenv("QDRANT_URL", qdrant_url)
    monkeypatch.setenv("QDRANT_COLLECTION", name)
    monkeypatch.setenv("EMBEDDING_DIM", "8")
    get_settings.cache_clear()
    yield get_settings()
    client = QdrantClient(url=qdrant_url)
    if client.collection_exists(name):
        client.delete_collection(name)
    get_settings.cache_clear()
```

### 4.2 Test cases

```python
@pytest.mark.integration
def test_ensure_collection_creates(qdrant_settings):
    ensure_collection()
    client = get_client()
    assert client.collection_exists(qdrant_settings.qdrant_collection)
    info = client.get_collection(qdrant_settings.qdrant_collection)
    assert info.config.params.vectors.size == 8

@pytest.mark.integration
def test_ensure_collection_idempotent(qdrant_settings):
    ensure_collection()
    ensure_collection()
    assert get_client().count(qdrant_settings.qdrant_collection).count == 0
```

Các test còn lại:

| Test | Kỳ vọng |
|---|---|
| `test_dimension_mismatch_raises` | Tạo collection size 4, settings dim 8 → `RuntimeError` |
| `test_health_true` | `health()` true |
| `test_upsert_creates_points` | 3 chunk → count 3 |
| `test_upsert_idempotent` | upsert 2 lần → count 3 |
| `test_payload_fields` | payload đúng doc_id/file/page/chunk/text/offset |
| `test_search_returns_top_k` | 5 point, limit 2 → 2 hit, score giảm |
| `test_search_filter_doc_id` | 2 doc, filter 1 → chỉ hit doc đó |
| `test_search_score_threshold` | vector xa → không hit |
| `test_delete_only_target_doc` | xoá doc A → count doc B còn |
| `test_delete_idempotent` | xoá 2 lần không lỗi |

### 4.3 Vector giả

```python
def vec(i: int, dim: int = 8) -> list[float]:
    v = [0.0] * dim
    v[i % dim] = 1.0
    return v
```

Search cùng vector để đảm bảo hit; vector trực giao để test threshold.

### 4.4 Chạy

```bash
docker compose up -d
pytest -q -m integration
# hoặc
QDRANT_URL=http://localhost:6333 pytest -q -m integration
```

## 5. Trường hợp biên

- Qdrant không chạy → skip, không fail.
- Collection tên trùng giữa test → dùng uuid.
- Test chạy song song → mỗi test collection riêng; fixture function-scope.
- Cleanup lỗi (Qdrant chết giữa test) → bỏ qua, không che lỗi chính.
- Payload index đã tồn tại → ensure không lỗi.
- `EMBEDDING_DIM` thay đổi giữa test → `cache_clear`.
- Qdrant phiên bản cũ không có `query_points` → dùng `search` fallback; test theo API đang dùng.
- Vector toàn 0 → Qdrant có thể lỗi; dùng vector đơn vị.

## 6. Tiêu chí xong

- [ ] `pytest -q` (không Qdrant) → integration skip, unit pass.
- [ ] `pytest -q -m integration` với Docker → pass.
- [ ] Không còn collection `test_*` sau khi chạy.
- [ ] Không gọi API embedding/LLM.
- [ ] Test dimension mismatch không tự xoá collection.
- [ ] Thời gian < 30s.

## 7. Test (meta)

- Chạy integration 2 lần liên tiếp → pass, không rò collection.
- Tắt Qdrant → `pytest -q -m integration` skip.
- Đổi `EMBEDDING_DIM` → test dimension mismatch chạy đúng.

## 8. Tham chiếu

- Kế hoạch §9.1.
- S-05, S-10, S-22.
