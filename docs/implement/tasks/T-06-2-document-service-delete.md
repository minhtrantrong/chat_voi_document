# T-06-2 — `DocumentService.delete`: xoá mềm, audit, tạo job purge

| Thuộc tính | Giá trị |
|---|---|
| Story | US-06 (P0) — AC-06.1, AC-06.2; US-23 |
| Sprint | S4 |
| Tầng | APP |
| Ước lượng | 0.75d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-06-1, T-05-1, F-05, F-06, F-08 |
| Chặn | T-06-3, T-06-5, T-06-6 |

## Bối cảnh

SADD §5.3.6 (SD-05): `SELECT … FOR UPDATE`, kiểm tra quyền, `UPDATE status=DELETING, deleted_at=now()`, `INSERT AuditLog`, `INSERT Job(PURGE)`, commit; trả ngay.

## Phạm vi

**Làm:** `delete(actor, doc_id) -> None` và hàm nội bộ dùng chung `_mark_deleting(tx, actor, doc, *, reason)` (T-01-5 gọi với REPLACE).

## Đặc tả

```text
delete(actor, doc_id):
  with uow() as tx:
    doc = repo.get_for_update(tx, doc_id)                       # SELECT ... FOR UPDATE
    if doc is None or not doc.is_active or not policy.can_view(actor, doc): raise NotFound(ERR_DOC_404)
    if not policy.can_delete(actor, doc): raise Forbidden(ERR_AUTH_403)
    _mark_deleting(tx, actor, doc, reason="user")
  telemetry.emit("document_deleted", actor.user_id, document_id=str(doc_id))

_mark_deleting(tx, actor, doc, reason):
  doc.mark_deleting(clock.now()); repo.save(tx, doc)
  tx.execute("""UPDATE jobs SET status='DEAD', last_error='CANCELED'
                WHERE type='document.ingest' AND payload->>'documentId'=:id AND status='QUEUED'""")
  jobs.enqueue(tx, "document.purge", {"documentId": str(doc.id)}, priority=150, max_attempts=5)
  audit.record(tx, actor, DOCUMENT_DELETE, "document", doc.id,
               {"cause": reason, "admin_override": actor.user_id != doc.owner_id})
```

- Enqueue purge vi phạm `ux_jobs_document` (đã có purge đang chờ) → bỏ qua.
- Ingest đang RUNNING không bị huỷ ở đây; handler ingest tự dừng ở batch kế tiếp (T-04-4).
- Hiệu lực ngay: retrieval (T-09-1) và list (T-05-2) lọc `deleted_at IS NULL`; citation tính `deleted` động (T-13d / T-13-4).
- Tài liệu SHARED do người khác sở hữu: END_USER thấy được nhưng không xoá được → `Forbidden` (UI ẩn nút nhờ `can_delete`).

## Tiêu chí xong

- [ ] Sau commit: tài liệu `DELETING`, `deleted_at` có giá trị, 1 job purge QUEUED, 1 audit.
- [ ] Gọi `delete` lần hai → `NotFound`.
- [ ] Không phải chủ (END_USER) → `Forbidden`; tài liệu private người khác → `NotFound`.
- [ ] ADMIN xoá tài liệu người khác → audit có `admin_override: true`.

## Test

`tests/integration/documents/test_delete.py`; dòng `delete` trong authz matrix.

## Tham chiếu

SADD §5.3.6, §5.3.9, ADR-010 · US-06
