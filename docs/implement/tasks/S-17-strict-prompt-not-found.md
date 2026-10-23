# S-17 — Prompt strict, NOT_FOUND và chuẩn bị câu trả lời

| Thuộc tính | Giá trị |
|---|---|
| Story | US-08, US-09 |
| Phase | P2 |
| Tầng | APP |
| Ước lượng | 0,25d |
| Phụ thuộc | S-15, S-16 |
| Chặn | S-18, S-24 |
| Owner gợi ý | Backend |

## 1. Mục tiêu

Ghép retrieval + prompt + LLM thành một luồng có thể kiểm soát: nếu không có ngữ cảnh đạt ngưỡng thì **không gọi LLM**, trả thông báo cố định; nếu có, gửi prompt strict và trả câu trả lời kèm nguồn.

## 2. Phạm vi

**Làm:**

- `app/rag.py`: `PreparedAnswer`, `prepare_answer`, `stream_answer`, `answer_question`.
- `NOT_FOUND` constant.
- Prompt strict dùng template S-15.
- Giới hạn lịch sử gửi LLM (6 message gần nhất).
- Hỗ trợ `selected_doc_ids` (filter Qdrant) dù UI chưa dùng.
- Post-check: nếu LLM trả `KHONG_TIM_THAY` hoặc rỗng → coi là NOT_FOUND.

**Không làm:**

- Không rerank.
- Không kiểm tra citation từng câu bằng LLM judge.
- Không lưu lịch sử vào DB.

## 3. File chính

```text
app/rag.py
app/prompts.py        # hoặc prompts/qa_answer.md
tests/test_rag_answer.py
```

## 4. Đặc tả

### 4.1 DTO

```python
from dataclasses import dataclass, field
from app.prompts import SYSTEM_PROMPT

NOT_FOUND = "Không tìm thấy thông tin này trong các tài liệu đã tải lên."

@dataclass(frozen=True)
class PreparedAnswer:
    messages: list[dict[str, str]] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    not_found: bool = False
```

### 4.2 Chuẩn bị

```python
def prepare_answer(
    question: str,
    history: list[dict],
    *,
    selected_doc_ids: list[str] | None = None,
) -> PreparedAnswer:
    question = question.strip()
    if not question:
        raise ValueError("Câu hỏi rỗng.")

    s = get_settings()
    query_vector = embed_query(question)
    hits = search_chunks(
        query_vector,
        limit=s.top_k,
        score_threshold=s.score_threshold,
        doc_ids=selected_doc_ids,
    )
    # S-21 sẽ thay bằng select_hits(...) để giới hạn chunk/tài liệu
    context, sources = build_context(hits, max_chars=s.max_context_chars)

    if not sources or not context.strip():
        return PreparedAnswer(not_found=True)

    history = _trim_history(history, max_messages=6)
    system = SYSTEM_PROMPT.format(context=context, question=question)
    messages = [{"role": "system", "content": system}, *history]
    return PreparedAnswer(messages=messages, sources=sources)
```

**Vì sao câu hỏi nằm trong system:** template S-15 đã có `{question}`. Không thêm user message trùng. Nếu đổi template chỉ còn `{context}`, thêm `{"role": "user", "content": question}` ở cuối.

### 4.3 Trim history

```python
def _trim_history(history: list[dict], *, max_messages: int) -> list[dict]:
    clean = [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if m.get("role") in {"user", "assistant"} and m.get("content")
    ]
    return clean[-max_messages:]
```

Không đưa `sources` vào prompt (chỉ là metadata UI).

### 4.4 Stream và post-check

```python
from collections.abc import Iterator

def stream_answer(prepared: PreparedAnswer) -> Iterator[str]:
    if prepared.not_found:
        yield NOT_FOUND
        return
    for token in stream_chat(prepared.messages):
        yield token
```

UI cần biết marker sau khi stream. Cung cấp helper:

```python
def finalize_answer(text: str, sources: list[Source]) -> tuple[str, list[Source], bool]:
    cleaned = text.strip()
    if not cleaned or "KHONG_TIM_THAY" in cleaned:
        return NOT_FOUND, [], True
    return cleaned, sources, False
```

### 4.5 Answer cho test/eval

```python
def answer_question(
    question: str,
    history: list[dict],
    *,
    selected_doc_ids: list[str] | None = None,
) -> tuple[str, list[Source], bool]:
    prepared = prepare_answer(question, history, selected_doc_ids=selected_doc_ids)
    if prepared.not_found:
        return NOT_FOUND, [], True
    text = "".join(stream_answer(prepared))
    return finalize_answer(text, prepared.sources)
```

### 4.6 Prompt

Dùng template S-15. Bổ sung quy tắc:

- “Nếu câu hỏi yêu cầu thông tin không có trong ngữ cảnh, trả `KHONG_TIM_THAY`.”
- “Không trả lời bằng kiến thức chung.”
- “Trích dẫn `[S#]` sau mỗi ý.”
- “Nếu ngữ cảnh mâu thuẫn, nêu mâu thuẫn và nguồn.”

## 5. Trường hợp biên

- Câu hỏi rỗng/toàn khoảng trắng → `ValueError`; UI bỏ qua.
- Không có tài liệu READY → UI chặn trước (S-19); nếu gọi trực tiếp, `search_chunks` trả [] → NOT_FOUND.
- Không có hit đạt ngưỡng → NOT_FOUND, không gọi LLM.
- Có hit nhưng context rỗng (payload thiếu text) → NOT_FOUND.
- LLM trả `KHONG_TIM_THAY` → `finalize_answer` đổi thành NOT_FOUND, ẩn nguồn.
- LLM trả rỗng → NOT_FOUND.
- LLM trả câu trả lời không có `[S#]` → vẫn trả lời, nhưng UI hiển thị nguồn từ `sources`; có thể thêm cảnh báo "Câu trả lời chưa gắn nguồn" (tuỳ chọn).
- Lịch sử dài → cắt 6 message; không cắt giữa cặp user/assistant? Cắt thô có thể mất ngữ cảnh; chấp nhận.
- `selected_doc_ids=[]` → hiểu là không lọc (giống None) hay không có tài liệu? Quy ước: `None`/rỗng = tất cả. Ghi rõ.
- Ngôn ngữ câu hỏi khác tiếng Việt → prompt yêu cầu trả cùng ngôn ngữ.
- Tài liệu bị xoá giữa lúc retrieve và stream → sources vẫn hiển thị trong câu trả lời hiện tại; lần hỏi sau không còn.

## 6. Tiêu chí xong

- [ ] Không hit → NOT_FOUND, không gọi `stream_chat`.
- [ ] Có hit → prompt chứa context + câu hỏi, gọi LLM.
- [ ] `sources` khớp nhãn `[S#]` trong prompt.
- [ ] `KHONG_TIM_THAY`/rỗng → NOT_FOUND.
- [ ] History chỉ gồm role/content, tối đa 6.
- [ ] `selected_doc_ids` được truyền vào filter.
- [ ] Test không gọi mạng thật.

## 7. Test

`tests/test_rag_answer.py`:

- `test_no_hits_returns_not_found_without_llm` (mock `stream_chat`, assert không gọi).
- `test_hits_build_prompt_and_stream`.
- `test_marker_maps_to_not_found`.
- `test_empty_llm_output_maps_to_not_found`.
- `test_history_trimmed`.
- `test_selected_doc_ids_forwarded`.
- `test_empty_question_raises`.
- `test_sources_match_prompt_labels`.

Dùng monkeypatch `embed_query`, `search_chunks`, `stream_chat`.

## 8. Tham chiếu

- Kế hoạch §2 luồng chat, §7.4.
- S-15, S-16, S-18, S-24.
