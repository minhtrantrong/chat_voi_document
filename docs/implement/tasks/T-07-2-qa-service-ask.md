# T-07-2 — `QaService.ask`: kiểm tra điều kiện, tạo message + answer + job

| Thuộc tính | Giá trị |
|---|---|
| Story | US-07 (P0) — AC-07.1, AC-07.2 (tầng service) |
| Sprint | S3 |
| Tầng | APP |
| Ước lượng | 1.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-07-1, T-07-3, T-07-6, T-13c-2 (`resolve_scope`), T-24-2 (`BudgetService`, có thể stub), F-06, F-08 |
| Chặn | T-07-5, T-13-3 |

## Bối cảnh

SADD §5.3.4 (SD-03) bước 1–3 và "Kiểm tra trước khi tạo job": ping Redis, rate limit, có tài liệu READY trong scope, idempotency; tạo toàn bộ trong **một transaction**.

## Phạm vi

**Làm:** method `ask(actor, cmd) -> AnswerHandle`, repository `messages`, `answers` (insert), telemetry `question_submitted`.

## Đặc tả

```text
ask(actor, cmd):
  q = cmd.question.strip(); limits = config.limits()
  if not q: raise Invalid(ERR_Q_EMPTY)
  if len(q) > limits.max_question_chars: raise Invalid(ERR_Q_TOO_LONG, {"max": limits.max_question_chars})
  if not guard.ping(): raise Unavailable(ERR_REDIS_UNAVAILABLE)
  ok, retry_after = guard.rate_limit(actor.user_id, limits.rate_limit_asks_per_hour)
  if not ok: RATE_LIMITED.labels("ask").inc(); raise RateLimited(ERR_RATE_LIMIT, {"retry_after": retry_after})
  if budget.exhausted_today(): raise Unavailable(ERR_BUDGET)
  if (aid := guard.idempotency_get(actor.user_id, cmd.conversation_id, cmd.idempotency_key)):
      return AnswerHandle(aid, ...)                                         # đọc conversation_id từ DB
  scope = documents.resolve_scope(actor, cmd.scope_doc_ids)                 # T-13c-2
  if not scope.has_any_ready: raise Invalid(ERR_NO_READY_DOC)
  with uow() as tx:
     conv = conversations.get_or_create(tx, actor, cmd.conversation_id, title=q[:60])   # T-07-6
     is_followup = conversations.has_completed_answer(tx, conv.id)
     m_user = messages.insert(tx, new_id(), conv.id, "USER", q, "COMPLETE")
     m_asst = messages.insert(tx, new_id(), conv.id, "ASSISTANT", "", "STREAMING")
     ans_id = new_id()
     answers.insert(tx, ans_id, m_user.id, m_asst.id, outcome="PENDING", model=settings.llm_model,
                    prompt_version=prompts.current_version, embedding_model=settings.embedding_model)
     jobs.enqueue(tx, "answer.generate",
                  {"answerId": str(ans_id), "scopeDocIds": [str(i) for i in scope.ids_or_empty],
                   "isFollowup": is_followup},
                  priority=200, max_attempts=1)
     conversations.touch(tx, conv.id)
     telemetry.emit("question_submitted", actor.user_id, answer_id=ans_id, tx=tx,
                    conversation_id=str(conv.id), is_followup=is_followup,
                    scope_count=len(scope.ids), question_len=len(q))
  guard.idempotency_set(actor.user_id, conv.id, cmd.idempotency_key, ans_id)
  ASK_TOTAL.labels("submitted").inc()
  return AnswerHandle(ans_id, conv.id)
```

- `conversation_id` không phải của actor → `NotFound` (qua `get_or_create`).
- `scope.ids_or_empty`: rỗng nghĩa là "mọi tài liệu READY trong quyền" (giảm kích thước payload).
- Telemetry `question_submitted` ghi **trong cùng transaction** để báo cáo US-20 nhất quán với answer.
- Thứ tự kiểm tra cố định như trên (rẻ trước, đắt sau); kiểm tra đầu vào trước khi chạm Redis.

## Tiêu chí xong

- [ ] Gọi thành công → 2 message, 1 answer PENDING, 1 job `answer.generate` priority 200, 1 telemetry event; tất cả cùng transaction.
- [ ] Câu rỗng / quá dài / không có tài liệu READY / Redis down / vượt rate limit → đúng mã lỗi và **không** tạo bản ghi nào.
- [ ] Gửi hai lần cùng `idempotency_key` → cùng `answer_id`, chỉ 1 job.

## Test

`tests/integration/qa/test_ask.py`: `test_ask_creates_answer_and_job`, `test_ask_rejects_empty`, `test_ask_rejects_too_long`, `test_ask_rejects_without_ready_doc`, `test_ask_redis_down_no_job`, `test_ask_rate_limited`, `test_ask_idempotent`, `test_ask_foreign_conversation_not_found`.

## Tham chiếu

SADD §5.3.4, §5.3.9 · US-07 · Implement_plan §17 US-07
