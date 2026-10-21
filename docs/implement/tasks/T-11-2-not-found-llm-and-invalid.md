# T-11-2 — NOT_FOUND khi LLM trả "không tìm thấy" hoặc citation không hợp lệ

| Thuộc tính | Giá trị |
|---|---|
| Story | US-11 (P0) — AC-11.1 |
| Sprint | S3 |
| Tầng | WRK |
| Ước lượng | 0.25d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-10-1, T-13-3 |
| Chặn | — |

## Bối cảnh

SADD §5.3.4 bước 3: `ANSWERED` mà không có marker → gửi `reset` để xoá buffer đã stream, retry 1 lần với prompt chặt; vẫn không có → `reset` + NOT_FOUND. LLM tự trả câu không tìm thấy cũng là NOT_FOUND.

## Phạm vi

**Làm:** nhánh `NotFound` / `NoCitation` sau `validator.validate` trong `handle_answer`.

## Đặc tả

```text
for attempt in (1, 2):
    buf = stream_from_llm(prompt)                    # T-13-3
    match validator.validate(buf, sources, lang):
        case Answered(segs): finalize(ANSWERED, segs); return
        case NotFound():     stream.append("reset"); finalize_not_found(lang); return
        case NoCitation():
            stream.append("reset")
            if attempt == 1: prompt = builder.build(..., strict=True); continue
stream.append("reset"); finalize_not_found(lang, error_code="CITATION_INVALID")
```

- `reset` **bắt buộc** trước khi stream lại hoặc chuyển NOT_FOUND, để UI không giữ nội dung của lần thử bị loại (SADD §5.3.4).
- Token của cả hai lần gọi đều được cộng vào usage/budget.
- Log info `citation_retry` (chỉ số lần, không nội dung).

## Tiêu chí xong

- [ ] FakeLLM `not_found` → NOT_FOUND, 0 citation, stream có `reset`.
- [ ] FakeLLM `no_markers` → gọi LLM 2 lần, lần 2 dùng prompt strict, rồi NOT_FOUND với `CITATION_INVALID`.

## Test

`tests/integration/qa/test_not_found.py::test_llm_not_found_sentence`, `::test_no_citation_retry_strict`.

## Tham chiếu

SADD §5.3.4 · ADR-007 · US-11
