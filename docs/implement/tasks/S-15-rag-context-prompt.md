# S-15 — Retrieval và build context có nguồn

| Thuộc tính | Giá trị |
|---|---|
| Story | US-07, US-08, US-09 |
| Phase | P2 |
| Tầng | APP |
| Ước lượng | 0,5d |
| Phụ thuộc | S-10 |
| Chặn | S-17, S-18, S-21, S-24 |
| Owner gợi ý | Backend |

## 1. Mục tiêu

Từ câu hỏi đã embed, search Qdrant top-k, chuyển hit thành `Source` có nhãn `[S1]…`, và build context văn bản giới hạn `MAX_CONTEXT_CHARS`. Context này là **nguồn duy nhất** cho LLM ở S-17.

## 2. Phạm vi

**Làm:**

- `search_chunks(query_vector, limit, score_threshold, doc_ids=None)` trong `app/vector_store.py`.
- `SearchHit` DTO.
- `build_context(hits, max_chars)` trong `app/rag.py`.
- Dedupe cơ bản theo point id và `(doc_id, chunk_index)`.
- Format block:
  ```text
  [S1] hop-dong.pdf — trang 7
  <text>
  ```
- Trả `(context: str, sources: list[Source])`.

**Không làm:**

- Chưa gọi LLM (S-16).
- Chưa giới hạn số chunk/tài liệu (S-21) — S-15 chỉ dedupe/truncate.
- Chưa rerank bằng cross-encoder.

## 3. File chính

```text
app/vector_store.py   # search_chunks + SearchHit
app/rag.py            # Source + build_context
tests/test_rag_context.py
```

## 4. Đặc tả

### 4.1 SearchHit

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class SearchHit:
    id: str
    score: float
    payload: dict
```

### 4.2 Search

```python
from qdrant_client.models import Filter, FieldCondition, MatchAny

def search_chunks(
    query_vector: list[float],
    *,
    limit: int,
    score_threshold: float,
    doc_ids: list[str] | None = None,
    client: QdrantClient | None = None,
) -> list[SearchHit]:
    s = get_settings()
    client = client or get_client()
    query_filter = None
    if doc_ids:
        query_filter = Filter(
            must=[FieldCondition(key="doc_id", match=MatchAny(any=doc_ids))]
        )

    response = client.query_points(
        collection_name=s.qdrant_collection,
        query=query_vector,
        query_filter=query_filter,
        limit=limit,
        score_threshold=score_threshold,
        with_payload=True,
    )
    return [
        SearchHit(id=str(p.id), score=float(p.score), payload=dict(p.payload or {}))
        for p in response.points
    ]
```

> Nếu qdrant-client cũ không có `query_points`, dùng `client.search(...)` và map tương tự. Ghi chú trong code.

### 4.3 Source

```python
@dataclass(frozen=True)
class Source:
    label: str          # S1, S2...
    doc_id: str
    file_name: str
    page: int
    chunk_index: int
    text: str
    score: float
```

### 4.4 Build context

```python
def build_context(
    hits: list[SearchHit],
    *,
    max_chars: int = 24_000,
) -> tuple[str, list[Source]]:
    seen_ids: set[str] = set()
    seen_chunks: set[tuple[str, int]] = set()
    blocks: list[str] = []
    sources: list[Source] = []
    used = 0

    for hit in hits:
        payload = hit.payload
        doc_id = str(payload.get("doc_id", ""))
        chunk_index = int(payload.get("chunk_index", -1))
        if not doc_id or chunk_index < 0:
            continue
        if hit.id in seen_ids or (doc_id, chunk_index) in seen_chunks:
            continue
        seen_ids.add(hit.id)
        seen_chunks.add((doc_id, chunk_index))

        text = str(payload.get("text", "")).strip()
        if not text:
            continue

        label = f"S{len(sources) + 1}"
        file_name = str(payload.get("file_name", "tài liệu"))
        page = int(payload.get("page", 0))
        header = f"[{label}] {file_name} — trang {page}\n"
        budget = max_chars - used - len(header)
        if budget <= 0:
            break
        if len(text) > budget:
            text = text[:budget].rstrip()
        block = header + text
        blocks.append(block)
        sources.append(
            Source(
                label=label,
                doc_id=doc_id,
                file_name=file_name,
                page=page,
                chunk_index=chunk_index,
                text=text,
                score=hit.score,
            )
        )
        used += len(block) + 2  # "\n\n"
        if used >= max_chars:
            break

    return "\n\n".join(blocks), sources
```

### 4.5 Prompt template (S-17 dùng)

Tạo `app/prompts.py` hoặc `prompts/qa_answer.md`:

```text
Bạn là trợ lý trả lời câu hỏi dựa trên tài liệu người dùng đã tải lên.

QUY TẮC:
1. Chỉ dùng thông tin trong NGỮ CẢNH bên dưới.
2. Không dùng kiến thức bên ngoài, không suy đoán.
3. Nếu ngữ cảnh không đủ để trả lời, trả đúng một dòng: KHONG_TIM_THAY
4. Trả lời bằng cùng ngôn ngữ với câu hỏi.
5. Ghi nguồn ngay sau thông tin, dạng [S1], [S2].
6. Nếu nhiều tài liệu, tổng hợp và ghi nguồn cho từng ý.
7. Không bịa số liệu, tên, ngày, điều khoản.

NGỮ CẢNH:
{context}

CÂU HỎI:
{question}
```

## 5. Trường hợp biên

- `hits=[]` → `("", [])`.
- Hit thiếu `doc_id`/`text` → bỏ qua, không crash.
- `page`/`chunk_index` sai kiểu → `int()` có thể raise; dùng try/except hoặc `payload.get` mặc định; tốt nhất validate:
  ```python
  try: chunk_index = int(...)
  except (TypeError, ValueError): continue
  ```
- Text dài hơn budget → truncate; đánh dấu `…`? Có thể thêm `…` nhưng làm lệch text; chấp nhận truncate.
- Nhiều hit cùng chunk (Qdrant không trả trùng, nhưng vẫn dedupe).
- `max_chars` nhỏ hơn header → dừng, trả context rỗng; caller xử lý NOT_FOUND.
- File name chứa newline → thay bằng khoảng trắng khi format header.
- Nhiều tài liệu → nhãn S1..Sn tăng dần theo thứ tự hit (score giảm dần).
- Không đảm bảo mỗi tài liệu có mặt; S-21 xử lý.

## 6. Tiêu chí xong

- [ ] Search trả hit đúng filter `doc_id`.
- [ ] `score_threshold` được áp dụng.
- [ ] Context có nhãn `[S#]`, tên file, trang.
- [ ] Tổng context <= `max_chars`.
- [ ] Không trùng source.
- [ ] Hit thiếu field không làm crash.
- [ ] `sources` cùng thứ tự với block.

## 7. Test

`tests/test_rag_context.py`:

- `test_empty_hits`.
- `test_build_context_labels`.
- `test_context_respects_max_chars`.
- `test_dedupe_same_chunk`.
- `test_skip_missing_payload`.
- `test_truncate_long_text`.
- `test_multiple_docs_labels`.
- Integration: `test_search_filter_by_doc_id`.
- Integration: `test_score_threshold`.

## 8. Tham chiếu

- Kế hoạch §2 luồng chat, §7.4.
- S-10, S-16, S-17, S-21.
