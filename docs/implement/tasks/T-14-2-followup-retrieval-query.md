# T-14-2 — Câu truy vấn retrieval cho câu hỏi tiếp theo (follow-up)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-14 (P1) — AC-14.1 |
| Sprint | S4 |
| Tầng | APP / WRK |
| Ước lượng | 1d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-14-1, T-08-1, T-08-3, F-04 (cờ `query_rewrite`) |
| Chặn | T-14-3 |

## Bối cảnh

Câu "còn hạn chót của nó?" không chứa đủ từ khoá để truy hồi. Prompt có lịch sử nhưng **retrieval** chỉ nhìn câu hiện tại. TD-08: query rewrite bằng LLM chưa bật mặc định (chi phí/độ trễ).

## Phạm vi

**Làm:** hàm `retrieval_query(question, history, is_followup, flags) -> str` trong `app/qa/retrieval.py`; prompt `prompts/query_rewrite.v1.md`.

## Đặc tả

```text
retrieval_query(question, history, is_followup):
  if not is_followup or not history: return question
  if flags.query_rewrite:
      try: return rewrite_with_llm(question, history[-3:], timeout_s=3)        # trả về một câu độc lập
      except (LLMTimeout, LLMUnavailable): log.warn("query_rewrite_fallback")
  return question + "\n" + history[-1].question                                # heuristic mặc định
```

`prompts/query_rewrite.v1.md` (SADD §10.3):

```text
Viết lại câu hỏi sau thành câu hỏi độc lập, giữ nguyên ý định và ngôn ngữ, dùng tối đa 3 lượt hội thoại gần nhất.
Chỉ trả về câu hỏi đã viết lại, không giải thích.
LỊCH SỬ:
$history
CÂU HỎI:
$question
```

- `rewrite_with_llm`: `max_tokens=100`, `temperature=0`, gom toàn bộ stream thành chuỗi; kết quả rỗng hoặc dài > 3× câu gốc → dùng heuristic.
- Token của rewrite cộng vào ngân sách ngày (T-24-2).
- Telemetry `question_submitted.is_followup` đã có (T-07-2).
- Bật cờ rewrite **chỉ** khi eval followup < 0.8 và chạy lại eval gate (Implement_plan §18).

## Tiêu chí xong

- [ ] Heuristic: câu follow-up được ghép với câu hỏi trước khi embed.
- [ ] Cờ bật + LLM giả trả câu viết lại → dùng câu đó; LLM lỗi → fallback heuristic.

## Test

`tests/unit/qa/test_retrieval_query.py` (FakeLLM).

## Tham chiếu

US-14 · SADD §10.3, TD-08
