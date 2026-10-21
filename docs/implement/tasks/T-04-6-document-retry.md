# T-04-6 — `DocumentService.retry`: xử lý lại tài liệu lỗi

| Thuộc tính | Giá trị |
|---|---|
| Story | US-04 (P0) — AC-04.3 |
| Sprint | S2 |
| Tầng | APP |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-01-3, T-05-1 (AccessPolicy), F-05, F-08 |
| Chặn | T-03-3 |

## Bối cảnh

AC-04.3: xử lý thất bại thì trạng thái "Lỗi" kèm lý do và nút "Thử lại" hoặc "Xoá". State machine cho phép `ERROR → PROCESSING`.

## Phạm vi

**Làm:** method `retry(actor, doc_id) -> DocumentDTO`.

## Đặc tả

```text
retry(actor, doc_id):
  with uow() as tx:
    doc = repo.get_for_update(tx, doc_id)
    if doc is None or not doc.is_active or not policy.can_view(actor, doc): raise NotFound(ERR_DOC_404)
    if not policy.can_delete(actor, doc): raise Forbidden(ERR_AUTH_403)          # quyền retry = quyền xoá (owner/ADMIN)
    if doc.status != ERROR or doc.error_code not in RETRYABLE_DOC_ERRORS:
        raise Invalid(ERR_DOC_422, {"reason": "not_retryable"})
    doc.mark_retry(); repo.save(tx, doc)                                          # PROCESSING, error_code NULL, version+1
    jobs.enqueue(tx, "document.ingest", {"documentId": str(doc_id)}, priority=100, max_attempts=3)
    audit.record(tx, actor, DOCUMENT_RETRY, "document", doc_id)
  return to_dto(doc, actor)
```

- Enqueue vi phạm `ux_jobs_document` (đã có job ingest đang chạy) → coi như thành công, không báo lỗi (idempotent khi bấm hai lần).
- `version` tăng để cache ảnh trang (T-13d-2) không dùng lại dữ liệu cũ.

## Tiêu chí xong

- [ ] Tài liệu `EMBED_FAILED` → retry → PROCESSING + job mới.
- [ ] Tài liệu `PDF_NO_TEXT` → `Invalid`.
- [ ] Người không phải chủ (END_USER) → `Forbidden`; tài liệu private của người khác → `NotFound`.
- [ ] Bấm retry hai lần liên tiếp → một job.

## Test

`tests/integration/documents/test_retry.py`; thêm dòng vào authz matrix (T-21-8).

## Tham chiếu

US-04 AC-04.3 · SADD §5.3.8 · Implement_plan §14 C-14
