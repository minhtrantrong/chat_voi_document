# T-18-2 — Job `document.suggest`: sinh và kiểm tra câu hỏi gợi ý (P2)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-18 (P2) — AC-18.1 |
| Sprint | S4 — chỉ khi còn dung lượng |
| Tầng | WRK |
| Ước lượng | 1.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-18-1, T-04-4, T-09-1, T-08-3 |
| Chặn | T-18-3 |

## Bối cảnh

AC-18.1: hiển thị 1–3 gợi ý; mỗi gợi ý khi hỏi đều có câu trả lời kèm trích dẫn. Vì vậy chỉ giữ câu hỏi mà retrieval chắc chắn tìm được ngữ cảnh.

## Phạm vi

**Làm:** enqueue trong bước finalize của ingest (khi cờ bật), handler `@handles("document.suggest")` (queue của `worker-ingest`, priority 50, max_attempts 2), prompt `prompts/suggest.v1.md`.

## Đặc tả

```text
handle_suggest(job):
  doc_id = job.payload["documentId"]
  if not flags.suggestions: return
  chunks = 6 chunk đầu tiên có token_count ≥ 100 của tài liệu
  raw = llm(suggest.v1, chunks, max_tokens=300, temperature=0.3)      # "Viết 5 câu hỏi ngắn mà tài liệu trả lời được, mỗi dòng một câu"
  candidates = tách dòng, bỏ đánh số, bỏ câu > 150 ký tự, bỏ trùng
  kept = []
  for q in candidates:
      hits = retriever.search(owner_actor, embed(q), scope=[doc_id])
      if hits and hits[0].score >= limits.retrieval_min_score + 0.1: kept.append(q)
      if len(kept) == 3: break
  with uow: DELETE cũ; INSERT kept với ord 0..2
```

- Ngưỡng `min_score + 0.1` để gợi ý chắc chắn trả lời được.
- Token cộng vào ngân sách ngày (T-24-2).
- Lỗi LLM → retry 1 lần; vẫn lỗi thì bỏ qua (không ảnh hưởng trạng thái READY).

## Tiêu chí xong

- [ ] Tài liệu READY + cờ bật → có 1–3 gợi ý trong bảng.
- [ ] Cờ tắt → không enqueue job.

## Test

`tests/integration/jobs/test_suggest.py` (FakeLLM trả 5 câu, 2 câu không liên quan bị loại).

## Tham chiếu

US-18 · BR-021
