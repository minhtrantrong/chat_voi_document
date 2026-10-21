# T-11-1 — NOT_FOUND khi không có chunk đạt ngưỡng (không gọi LLM)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-11 — Được báo rõ khi tài liệu không có thông tin (P0) — AC-11.1 |
| Sprint | S3 |
| Tầng | WRK |
| Ước lượng | 0.25d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-09-1, T-13-3 (khung handler + finalize) |
| Chặn | — |

## Bối cảnh

DR-03: không có chunk đạt ngưỡng ⇒ `NOT_FOUND`, 0 citation, rẽ nhánh **trước** khi gọi LLM (tiết kiệm chi phí, NFR-COST-01).

## Phạm vi

**Làm:** nhánh trong `handle_answer` (T-13-3) và hàm `finalize_not_found(aid, lang, error_code=None)`.

## Đặc tả

```text
hits = retriever.search(actor, qvec, scope)
if not hits:
    finalize(outcome=NOT_FOUND, segments=[ParsedSegment(0, not_found_text(lang), cited=False, ())])
    return                                                   # không gọi LLM, không tính token LLM
```

- `not_found_text("vi") = "Không tìm thấy thông tin này trong các tài liệu đã tải lên."`; `"en" = "No information about this was found in the uploaded documents."`
- Lưu một segment với text trên, `cited=False`, 0 citation; `assistant message.content` = text đó; state `COMPLETE`.
- `XADD done not_found`.
- Telemetry `answer_completed {outcome: NOT_FOUND, citation_count: 0}`.

## Tiêu chí xong

- [ ] Câu hỏi không liên quan (FakeEmbedding cho điểm thấp) → NOT_FOUND, FakeLLM ghi nhận **0** lần gọi.

## Test

`tests/integration/qa/test_not_found.py::test_no_hits_skips_llm`.

## Tham chiếu

SADD §5.2.4 DR-03, §5.3.4 · US-11
