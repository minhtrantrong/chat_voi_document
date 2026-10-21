# T-17-1 — `QaService.summarize`: yêu cầu tóm tắt một tài liệu (P2)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-17 — Tóm tắt một tài liệu mới (P2) |
| Sprint | S4 — **chỉ làm nếu còn dung lượng**; cờ `FEATURE_SUMMARIZE` mặc định tắt |
| Tầng | APP |
| Ước lượng | 0.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-07-2, T-05-1, F-04 |
| Chặn | T-17-2, T-17-3 |

## Bối cảnh

US-17: mục "Tóm tắt" trong menu ⋯ của tài liệu; chưa có thiết kế riêng — dùng khung hội thoại hiện tại để hiển thị.

## Phạm vi

**Làm:** method `summarize(actor, doc_id, conversation_id) -> AnswerHandle`, tái sử dụng luồng `ask`.

## Đặc tả

```text
summarize(actor, doc_id, conversation_id):
  if not config.flags().summarize: raise Forbidden(ERR_AUTH_403)
  doc = documents.get(actor, doc_id)                 # NotFound nếu không quyền; phải READY
  if doc.status != READY: raise Invalid(ERR_NO_READY_DOC)
  question = t_server("summarize.question", file_name=doc.file_name)    # "Tóm tắt tài liệu «{file_name}»"
  return self._create_answer(actor, conversation_id, question,
                             job_payload_extra={"mode": "summarize", "documentId": str(doc_id)},
                             scope=[doc_id])
```

- Tách phần dùng chung của `ask` (kiểm tra Redis, rate limit, budget, transaction tạo message/answer/job) thành `_create_answer` để không lặp code.
- Câu "câu hỏi" tóm tắt là chuỗi phía server (tiếng Việt), đặt trong `app/qa/strings.py` (không phải UI i18n vì lưu vào DB).
- Rate limit và ngân sách áp dụng như câu hỏi thường.

## Tiêu chí xong

- [ ] Cờ tắt → `Forbidden`; cờ bật + tài liệu READY → tạo answer + job `mode=summarize`.

## Test

`tests/integration/qa/test_summarize_service.py`.

## Tham chiếu

US-17 · BR-020 · Implement_plan §19
