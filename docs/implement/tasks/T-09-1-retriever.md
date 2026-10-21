# T-09-1 — Retriever: tìm vector có lọc quyền/phạm vi, đa dạng theo tài liệu, mở rộng lân cận

| Thuộc tính | Giá trị |
|---|---|
| Story | US-09 — Câu trả lời tổng hợp từ nhiều tài liệu (P0) — AC-09.1; dùng cho US-07, US-11, US-13c |
| Sprint | S3 |
| Tầng | APP / INF |
| Ước lượng | 1.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-04-3, T-04-4, T-05-1, F-07 |
| Chặn | T-08-2, T-13-3, T-11-1 |

## Bối cảnh

SADD §5.3.4 (Truy hồi): `top_k=8`, `min_score` 0.25, `ef_search=40`, lọc READY + chưa xoá + scope + quyền, chỉ cùng `embedding_model`, mở rộng `chunk_index ± 1`, tối đa 8 chunk. Thêm `MAX_CHUNKS_PER_DOC` để không một tài liệu chiếm hết ngữ cảnh (US-09).

## Phạm vi

**Làm:** `app/qa/retrieval.py::Retriever` (logic chọn), `app/infrastructure/db/repositories/chunks.py::search` và `neighbors` (SQL).

## Đặc tả

```python
@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: UUID; document_id: UUID; file_name: str; page: int; chunk_index: int
    anchor: str; text: str; score: float; is_neighbor: bool = False

class Retriever:
    def search(self, actor: Actor, query_vec: list[float], scope_ids: list[UUID]) -> list[RetrievedChunk]: ...
```

SQL ứng viên (một transaction ngắn):

```sql
SET LOCAL hnsw.ef_search = 40;
-- pgvector >= 0.8: SET LOCAL hnsw.iterative_scan = relaxed_order;
SELECT c.id, c.document_id, d.file_name, c.page, c.chunk_index, c.anchor, c.text,
       1 - (c.embedding <=> CAST(:q AS vector)) AS score
FROM document_chunks c
JOIN documents d ON d.id = c.document_id
WHERE d.status = 'READY' AND d.deleted_at IS NULL
  AND c.embedding_model = :model
  AND (d.owner_id = :uid OR d.visibility = 'SHARED')
  AND (cardinality(CAST(:scope AS uuid[])) = 0 OR d.id = ANY(CAST(:scope AS uuid[])))
ORDER BY c.embedding <=> CAST(:q AS vector)
LIMIT 40;
```

Chọn trong Python:

```text
cands = [c for c in rows if c.score >= limits.retrieval_min_score]
picked, per_doc = [], Counter()
for c in cands:                                            # đã sắp theo score giảm dần
    if per_doc[c.document_id] >= limits.max_chunks_per_doc: continue
    picked.append(c); per_doc[c.document_id] += 1
    if len(picked) == 6: break                              # 6 chunk lõi
neighbors = repo.neighbors([(c.document_id, c.chunk_index ± 1) for c in picked])   # cùng điều kiện lọc
kết quả = picked + neighbors (bỏ trùng theo chunk_id), cắt còn tối đa limits.retrieval_top_k (8)
```

- ADMIN **không** được truy hồi tài liệu private của người khác (khác với `can_view`): retrieval dùng đúng `owner_id = :uid OR SHARED` cho mọi role, tránh câu trả lời của admin trộn dữ liệu riêng của người khác. Ghi chú quyết định này trong code.
- Vector truyền bằng `pgvector.psycopg.register_vector` hoặc chuỗi `'[..]'`.
- `ef_search` và `LIMIT 40` đặt trong hằng số có comment lý do (post-filter của HNSW).
- Metric `cvd_retrieval_hits` (số chunk trả về), `cvd_retrieval_score` (histogram điểm cao nhất).

## Tiêu chí xong

- [ ] Tài liệu DELETING / chưa READY / private của người khác / ngoài scope **không bao giờ** xuất hiện.
- [ ] Hai tài liệu cùng chủ đề: kết quả có chunk của cả hai khi cả hai vượt ngưỡng (đa dạng).
- [ ] Không chunk nào vượt ngưỡng → danh sách rỗng.
- [ ] Chunk của `embedding_model` cũ bị bỏ qua.

## Test

`tests/integration/qa/test_retriever.py` (pgvector thật, `FakeEmbedding`): lọc trạng thái, lọc quyền, scope, per-doc cap, neighbor, model khác, rỗng.

## Tham chiếu

SADD §5.3.4 (Truy hồi), §5.4.3, DR-01, NFR-PERF-02 · US-09, US-13c
