# T-13-3 — Handler `answer.generate`: truy hồi, gọi LLM, stream, finalize

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13 (P0); hiện thực US-07…US-11, US-13b, US-14 ở phía worker |
| Sprint | S3 |
| Tầng | WRK |
| Ước lượng | 2d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-13-2, T-09-1, T-08-2, T-08-3, T-10-1, T-10-2, T-11-3, F-08, F-09 |
| Chặn | T-11-1, T-11-2, T-13-8, T-10-6, T-12-2 |

## Bối cảnh

SADD §5.3.4 (SD-03). Quy tắc: không giữ transaction khi chờ LLM; token không ghi Postgres từng cái; kiểm tra cancel trước khi gọi LLM và sau mỗi lô token; finalize trong **một** transaction; `answer.generate` không retry tự động.

## Phạm vi

**Làm:** `app/qa/worker_handler.py` (`@handles("answer.generate")`), `TokenBatcher`, hàm `finalize`.

## Đặc tả

```text
@handles("answer.generate")
def handle_answer(job, ctx):
  aid = UUID(job.payload["answerId"])
  with ctx.uow() as tx: st = answers.load_for_generation(tx, aid)
      # → outcome, question, conv_id, conv_user_id, created_at, assistant_message_id, history (T-14-1)
  if st.outcome != "PENDING": return
  actor = system_actor(st.conv_user_id)
  if ctx.stream.is_cancelled(aid): return finalize(ABORTED, [])
  ctx.stream.append(aid, "status", "retrieving")
  qtext = retrieval_query(st.question, st.history, job.payload["isFollowup"])          # T-14-2
  try: qvec = ctx.embedding.embed([qtext], timeout_s=5)[0]
  except EmbeddingUnavailable: return finalize(ERROR, [], error_code="LLM_UNAVAILABLE")
  hits = retriever.search(actor, qvec, [UUID(x) for x in job.payload["scopeDocIds"]])
  if not hits: return finalize_not_found(lang)                                         # T-11-1
  built = builder.build(st.question, hits, st.history)
  if ctx.stream.is_cancelled(aid): return finalize(ABORTED, [])
  ctx.stream.append(aid, "status", "generating")
  usage_total = Usage(0, 0)
  for attempt in (1, 2):
      buf, first_ms = "", None
      llm_stream = ctx.llm.stream_chat(built.messages, max_tokens=limits.max_output_tokens, temperature=0.1)
      try:
        for ev in llm_stream:
            if first_ms is None:
                first_ms = ms_between(st.created_at, ctx.clock.now()); record_first_token(aid, first_ms)
            buf += ev.text
            if batcher.add(ev.text):                         # flush mỗi 50 ms hoặc 20 token
                ctx.stream.append(aid, "token", batcher.drain())
                if ctx.stream.is_cancelled(aid):
                    llm_stream.close()
                    return finalize(ABORTED, validator.parse_partial(buf, built.sources), first_ms=first_ms)
        if rest := batcher.drain(): ctx.stream.append(aid, "token", rest)
      finally: llm_stream.close(); usage_total += llm_stream.usage or estimate(buf)
      match validator.validate(buf, built.sources, built.lang):          # T-10-1, T-11-2
          case Answered(segs): return finalize(ANSWERED, segs, first_ms=first_ms, usage=usage_total)
          case NotFound():     ctx.stream.append(aid, "reset"); return finalize_not_found(built.lang)
          case NoCitation() if attempt == 1:
              ctx.stream.append(aid, "reset"); built = builder.build(..., strict=True)
  ctx.stream.append(aid, "reset"); return finalize_not_found(built.lang, error_code="CITATION_INVALID")
```

Xử lý lỗi bao ngoài: `LLMTimeout` → `finalize(ERROR, error_code="LLM_TIMEOUT")`; `LLMUnavailable` → `LLM_UNAVAILABLE`; `TokenStreamUnavailable` → `REDIS_UNAVAILABLE`; exception khác → `ERROR` + log exception. Handler **không** ném lỗi ra runtime sau khi đã finalize (job SUCCEEDED về mặt kỹ thuật; outcome nằm ở `answers`). Nếu chính `finalize` lỗi DB: retry finalize 1 lần, vẫn lỗi thì ném để reaper xử lý.

`record_first_token(aid, ms)`: `UPDATE answers SET first_token_ms=:ms WHERE id=:id` (transaction ngắn), metric `FIRST_TOKEN_SECONDS.observe`, telemetry `answer_first_token`.

`finalize(outcome, segs, *, first_ms=None, usage=None, error_code=None)` — **một transaction**:
1. Insert `answer_segments` (ord, text, cited) và `citations` (T-10-2 cho từng segment).
2. `UPDATE answers SET outcome, first_token_ms (nếu chưa có), total_ms, prompt_tokens, completion_tokens, cost_estimate_usd, error_code, completed_at WHERE id=:aid AND outcome='PENDING'` — điều kiện `PENDING` để không ghi đè trạng thái do `cancel` đặt.
3. `UPDATE messages SET content=<text các segment nối \n\n>, state=MESSAGE_STATE_FOR[outcome]` cho assistant message.
4. `conversations.touch`.

Sau commit: `stream.append(aid, "done", outcome.lower())` (lỗi Redis chỉ log — UI có fallback DB); `budget.add(usage)` (T-24-2); telemetry `answer_completed` hoặc `answer_error`; metric `ASK_TOTAL{outcome}`, `ANSWER_SECONDS`.

`cost_estimate_usd`: bảng giá theo model trong cấu hình `LLM_PRICE_PER_1K` (env JSON); không có thì `NULL`.

## Tiêu chí xong

- [ ] Với FakeLLM `echo_sources`: answer ANSWERED, segments + citations đúng, message COMPLETE, stream có `status → token… → done`.
- [ ] Đặt cờ cancel sau 5 token: dừng ≤ 2 s, outcome ABORTED, phần đã sinh được lưu, message INTERRUPTED.
- [ ] LLM timeout → ERROR `LLM_TIMEOUT`, stream có `done error`.
- [ ] Không transaction nào mở trong lúc đọc stream LLM (review code + test bằng `pg_stat_activity` "idle in transaction" = 0).

## Test

`tests/integration/qa/test_answer_handler.py`: answered, cancel giữa chừng, cancel trước khi gọi LLM, timeout, 503, Redis lỗi lúc stream, finalize không ghi đè ABORTED.

## Tham chiếu

SADD §5.3.1 (quy tắc 6), §5.3.4, §5.3.9, §5.7.4 · Implement_plan §17 US-13
