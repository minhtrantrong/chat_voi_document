# T-04-4 — Handler `document.ingest`: extract → chunk → embed → index

| Thuộc tính | Giá trị |
|---|---|
| Story | US-04 (P0) — AC-04.1…04.3; US-03 — AC-03.3 |
| Sprint | S2 |
| Tầng | WRK |
| Ước lượng | 1.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-01-1, T-04-1, T-04-2, T-04-3, T-03-2, F-08, F-09 |
| Chặn | T-04-5, T-04-7, US-07 trở đi (cần tài liệu READY) |

## Bối cảnh

SADD §5.3.3 (SD-02): worker xử lý idempotent, retry 3 lần (30 s/2 phút/5 phút), kiểm tra trạng thái trước mỗi batch, khoá advisory theo tài liệu để không đua với purge.

## Phạm vi

**Làm:** `app/ingestion/worker_handler.py` (đăng ký `@handles("document.ingest")`), repository chunk (`upsert_batch`, `delete_from_index`), chuyển trạng thái tài liệu.

## Đặc tả

```text
@handles("document.ingest")
def handle_ingest(job, ctx):
  doc_id = UUID(job.payload["documentId"]); t0 = ctx.clock.now()
  with ctx.uow() as tx: doc = docs.get(tx, doc_id)
  if doc is None or doc.status != PROCESSING: return                     # đã xoá/đã xong → SUCCEEDED, không làm gì
  tmp = ctx.storage.get_to_tempfile(doc.storage_key)                     # NotFound → PermanentJobError(PDF_CORRUPT)
  try:
    pages = ctx.pdf.extract_pages(tmp)                                   # Permanent/Retryable từ T-04-1
  finally: tmp.unlink(missing_ok=True)
  report = classify_text_layer(pages, limits.min_text_chars_per_page)     # T-03-2
  if not report.has_text: raise PermanentJobError(PDF_NO_TEXT)
  chunks = chunker.chunk([p for p in pages if p.page not in report.empty_pages])
  for batch in batched(chunks, settings.embedding_batch_size):
      try: vectors = ctx.embedding.embed([c.text for c in batch])
      except EmbeddingUnavailable: raise RetryableJobError(EMBED_FAILED)
      with ctx.uow() as tx:
          if not advisory_xact_lock(tx, str(doc_id)): raise RetryableJobError(INDEX_FAILED)
          if docs.status(tx, doc_id) != PROCESSING: return               # bị xoá giữa chừng; purge sẽ dọn
          chunks_repo.upsert_batch(tx, doc_id, batch, vectors, model=ctx.embedding.model)
  with ctx.uow() as tx:
      lock + kiểm tra PROCESSING như trên
      chunks_repo.delete_from_index(tx, doc_id, len(chunks))             # xoá chunk_index >= len (lần chạy trước sinh nhiều hơn)
      doc = docs.get(tx, doc_id); doc.mark_ready(page_count=len(pages), now=ctx.clock.now()); docs.save(tx, doc)
  ctx.telemetry.emit("document_ready", doc.owner_id, document_id=str(doc_id), duration_ms=ms_since(t0))
```

Xử lý lỗi (bọc ngoài, trong cùng handler):

```text
except PermanentJobError as e:
    with uow: docs.mark_error(doc_id, e.code)          # chỉ khi status còn PROCESSING
    telemetry document_failed; raise                    # runtime F-09 đặt job FAILED
except RetryableJobError as e:
    if job.attempts >= job.max_attempts:
        with uow: docs.mark_error(doc_id, e.code); telemetry document_failed
    raise                                               # runtime: retry hoặc DEAD
```

SQL upsert chunk:

```sql
INSERT INTO document_chunks (id, document_id, page, chunk_index, text, token_count, char_start, char_end,
                             anchor, embedding, embedding_model)
VALUES (...)
ON CONFLICT (document_id, chunk_index) DO UPDATE SET
  page = EXCLUDED.page, text = EXCLUDED.text, token_count = EXCLUDED.token_count,
  char_start = EXCLUDED.char_start, char_end = EXCLUDED.char_end, anchor = EXCLUDED.anchor,
  embedding = EXCLUDED.embedding, embedding_model = EXCLUDED.embedding_model;
```

- Backoff riêng của ingest: `backoff_schedule=[30, 120, 300]` khi enqueue (F-08).
- Không giữ transaction trong lúc gọi S3/PDF/embedding.
- Không log nội dung chunk; log `pages`, `chunks`, `duration_ms`.

## Tiêu chí xong

- [ ] `text.pdf` → READY, `page_count=3`, số chunk > 0, mọi chunk có `embedding_model` đúng.
- [ ] Chạy handler 2 lần cho cùng tài liệu (giả lập retry) → không trùng chunk.
- [ ] Đặt tài liệu sang DELETING trong lúc embed batch 2 → handler dừng, không ghi thêm chunk.
- [ ] Embedding lỗi 3 lần → tài liệu ERROR `EMBED_FAILED`, job DEAD.
- [ ] `scan_only.pdf` → ERROR `PDF_NO_TEXT`, job FAILED ngay lần đầu.

## Test

`tests/integration/ingestion/test_ingest_handler.py` (Postgres+MinIO thật, `FakeEmbedding`, Clock giả).

## Tham chiếu

SADD §5.3.3, §5.3.9, §5.4.5 (invariant READY ⇒ ≥ 1 chunk) · US-04
