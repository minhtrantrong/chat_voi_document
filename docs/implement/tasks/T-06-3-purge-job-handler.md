# T-06-3 — Handler `document.purge`: xoá vector, object và đánh dấu citation

| Thuộc tính | Giá trị |
|---|---|
| Story | US-06 (P0); US-23 (BR-025, BRU-006) |
| Sprint | S4 |
| Tầng | WRK |
| Ước lượng | 1d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-06-2, T-01-1, F-07 (`advisory_xact_lock`), F-08, F-09 |
| Chặn | T-06-6, T-23-1 |

## Bối cảnh

SADD §5.3.6: worker xoá chunk/vector, xoá object S3, `UPDATE citations SET deleted=true`, tài liệu `DELETED`; lỗi một phần → retry (max 5), tài liệu giữ DELETING. Purge lấy **cùng** advisory lock với ingest; không lấy được thì retry với backoff.

## Phạm vi

**Làm:** `app/documents/worker_handler.py` (`@handles("document.purge")`) chạy ở queue của `worker-answer` (SADD §5.3.1).

## Đặc tả

```text
@handles("document.purge")
def handle_purge(job, ctx):
  doc_id = UUID(job.payload["documentId"])
  with ctx.uow() as tx:
     doc = docs.get(tx, doc_id)
     if doc is None or doc.status == DELETED: return
     if doc.status != DELETING: return                                        # không bao giờ purge tài liệu chưa xoá mềm
     if not advisory_xact_lock(tx, str(doc_id)): raise RetryableJobError(PURGE_PARTIAL, "lock_busy")
     tx.execute("UPDATE citations SET deleted = true, chunk_id = NULL WHERE document_id = :id")
     tx.execute("DELETE FROM document_chunks WHERE document_id = :id")
  try: ctx.storage.delete(doc.storage_key)                                    # idempotent
  except Exception as e: raise RetryableJobError(PURGE_PARTIAL, "storage")
  with ctx.uow() as tx:
     tx.execute("UPDATE documents SET status='DELETED' WHERE id=:id AND status='DELETING'")
  log.info("purge_done", document_id=str(doc_id))
```

- Thứ tự: DB (chunk + citation) trước, storage sau, rồi đánh dấu DELETED. Lỗi ở storage → retry toàn bộ; bước DB idempotent.
- `DELETE FROM document_chunks` với tài liệu 400 trang (~2.000 chunk) chạy một lần là được; nếu > 50.000 chunk thì xoá theo lô 5.000 (ghi chú cho tương lai).
- Job DEAD sau 5 lần → reaper không đổi trạng thái (giữ DELETING, retrieval đã chặn) và **alert** (`IntegrityViolation` qua T-23-1 phát hiện DELETING > 24 h).
- Bản PDF trong cache đĩa của container `web` (T-13d-2) **không** bị purge xoá (khác container); nó hết hạn theo TTL 30 phút và không truy cập được vì `render_page` kiểm tra `deleted_at` trước khi đọc cache.
- `chunk_id = NULL` cần thiết vì FK `citations.chunk_id ON DELETE SET NULL` — đặt rõ ràng để không phụ thuộc thứ tự.

## Tiêu chí xong

- [ ] Sau purge: 0 chunk của tài liệu, object không còn, mọi citation `deleted=true`, tài liệu `DELETED`.
- [ ] MinIO lỗi tạm → retry rồi hoàn tất khi MinIO trở lại.
- [ ] Ingest đang giữ lock → purge retry, không xoá sót chunk ghi sau đó.

## Test

`tests/integration/documents/test_purge.py`: purge thường; storage lỗi rồi phục hồi; đua với ingest (hai thread, lock); tài liệu không ở DELETING thì không làm gì.

## Tham chiếu

SADD §5.3.3 (khoá theo tài liệu), §5.3.6, §5.7.4, ADR-010
