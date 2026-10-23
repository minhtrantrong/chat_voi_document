# S-21 — Giới hạn chunk/tài liệu và đa dạng nguồn

| Thuộc tính | Giá trị |
|---|---|
| Story | US-09 |
| Phase | P2 |
| Tầng | APP |
| Ước lượng | 0,25d |
| Phụ thuộc | S-10, S-15 |
| Chặn | S-17 (tích hợp), S-24 |
| Owner gợi ý | Backend |

## 1. Mục tiêu

Tránh một tài liệu chiếm hết context khi người dùng có nhiều PDF. Giới hạn số chunk mỗi tài liệu, dedupe và vẫn đảm bảo top-k đa dạng nguồn nếu có thể.

## 2. Phạm vi

**Làm:**

- `select_hits(hits, *, top_k, max_per_doc)` trong `app/rag.py`.
- Dedupe theo point id và `(doc_id, chunk_index)`.
- Sắp score giảm dần (ổn định).
- Mỗi `doc_id` tối đa `max_per_doc`.
- Trả tối đa `top_k`.
- Tích hợp vào `prepare_answer` trước `build_context`.

**Không làm:**

- Không đảm bảo mọi tài liệu đều có mặt (nếu không có hit tốt).
- Không rerank.
- Không chọn theo UI (future).

## 3. File chính

```text
app/rag.py
tests/test_diversity.py
```

## 4. Đặc tả

### 4.1 Hàm

```python
from collections import Counter

def select_hits(
    hits: list[SearchHit],
    *,
    top_k: int,
    max_per_doc: int,
) -> list[SearchHit]:
    if top_k <= 0:
        raise ValueError("top_k phải > 0")
    if max_per_doc <= 0:
        raise ValueError("max_per_doc phải > 0")

    seen_ids: set[str] = set()
    seen_chunks: set[tuple[str, int]] = set()
    per_doc: Counter[str] = Counter()
    selected: list[SearchHit] = []

    for hit in sorted(hits, key=lambda h: h.score, reverse=True):
        doc_id = str(hit.payload.get("doc_id", ""))
        if not doc_id:
            continue
        try:
            chunk_index = int(hit.payload.get("chunk_index", -1))
        except (TypeError, ValueError):
            continue
        if chunk_index < 0:
            continue
        if hit.id in seen_ids or (doc_id, chunk_index) in seen_chunks:
            continue
        if per_doc[doc_id] >= max_per_doc:
            continue

        seen_ids.add(hit.id)
        seen_chunks.add((doc_id, chunk_index))
        per_doc[doc_id] += 1
        selected.append(hit)
        if len(selected) >= top_k:
            break

    return selected
```

### 4.2 Tích hợp

Trong `prepare_answer` (S-17):

```python
hits = search_chunks(...)
hits = select_hits(hits, top_k=s.top_k, max_per_doc=s.max_chunks_per_doc)
context, sources = build_context(hits, max_chars=s.max_context_chars)
```

### 4.3 Ví dụ

| Hit | Doc | Score | Chọn? |
|---|---|---|---|
| 1 | A | 0.91 | ✅ (A=1) |
| 2 | A | 0.90 | ✅ (A=2) |
| 3 | A | 0.89 | ✅ (A=3) |
| 4 | A | 0.88 | ✅ (A=4) |
| 5 | A | 0.87 | ❌ vượt max_per_doc=4 |
| 6 | B | 0.80 | ✅ (B=1) |
| 7 | B | 0.79 | ✅ (B=2) |
| 8 | C | 0.70 | ✅ (C=1) |

`top_k=8`, `max_per_doc=4` → 4 A + 2 B + 1 C = 7 (nếu hết hit thì dừng).

## 5. Trường hợp biên

- `hits=[]` → `[]`.
- `top_k`/`max_per_doc` <= 0 → `ValueError`.
- Hit thiếu `doc_id`/`chunk_index` → bỏ qua.
- Cùng point id xuất hiện 2 lần → dedupe.
- Cùng `(doc_id, chunk_index)` nhưng point id khác (hiếm) → dedupe.
- Chỉ có 1 tài liệu → trả tối đa `max_per_doc`, ít hơn `top_k`; chấp nhận.
- Score bằng nhau → `sorted` ổn định theo thứ tự gốc.
- `max_per_doc > top_k` → thực tế bị giới hạn bởi top_k.
- Nhiều tài liệu nhưng top hit toàn một tài liệu → các tài liệu khác có thể không xuất hiện nếu hit của chúng thấp hơn và đã đủ top_k; đây là hành vi mong đợi.
- `selected_doc_ids` filter ở search → chỉ hit trong phạm vi; select_hits không cần biết.

## 6. Tiêu chí xong

- [ ] Không quá `max_per_doc` chunk/tài liệu.
- [ ] Không quá `top_k` hit.
- [ ] Không trùng chunk/point.
- [ ] Có thể lấy từ nhiều tài liệu nếu có hit.
- [ ] `prepare_answer` dùng `select_hits`.
- [ ] Test với dữ liệu tổng hợp.

## 7. Test

`tests/test_diversity.py`:

- `test_cap_per_doc`.
- `test_top_k_limit`.
- `test_dedupe_point_id`.
- `test_dedupe_doc_chunk`.
- `test_skip_missing_doc_id`.
- `test_invalid_params_raise`.
- `test_multiple_docs_selected`.
- `test_single_doc_returns_at_most_cap`.

## 8. Tham chiếu

- Kế hoạch §6 P2, §10 rủi ro "một tài liệu chiếm hết context".
- S-15, S-17, S-24.
