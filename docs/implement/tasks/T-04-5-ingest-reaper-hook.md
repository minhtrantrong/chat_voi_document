# T-04-5 — Reaper hook cho ingest: tài liệu ERROR `WORKER_LOST`

| Thuộc tính | Giá trị |
|---|---|
| Story | US-04 (P0) — AC-04.3 |
| Sprint | S2 |
| Tầng | WRK |
| Ước lượng | 0.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | F-08 (REAPER_HOOKS), T-04-4 |
| Chặn | — |

## Bối cảnh

SADD §5.3.7: khi job `document.ingest` chết (worker mất nhiều lần, hết lượt) thì `documents.status='ERROR'`, `error_code='WORKER_LOST'`; người dùng có thể retry.

## Phạm vi

**Làm:** đăng ký hook `REAPER_HOOKS["document.ingest"]` trong `app/ingestion/worker_handler.py`.

## Đặc tả

```python
def on_ingest_dead(tx: UnitOfWork, job: Job) -> None:
    doc_id = UUID(job.payload["documentId"])
    tx.execute(
        "UPDATE documents SET status='ERROR', error_code='WORKER_LOST' "
        "WHERE id=:id AND status='PROCESSING'", {"id": doc_id})
    # telemetry document_failed sau commit (reaper gọi emit với tx=None)
REAPER_HOOKS["document.ingest"] = on_ingest_dead
```

- Điều kiện `status='PROCESSING'` để không ghi đè DELETING (người dùng đã xoá).
- `WORKER_LOST` nằm trong `RETRYABLE_DOC_ERRORS` nên UI hiện nút Thử lại (C-14).

## Tiêu chí xong

- [ ] Job ingest RUNNING quá `visibility_timeout` với `attempts == max_attempts` → reaper đưa tài liệu về ERROR `WORKER_LOST`.
- [ ] Tài liệu đang DELETING không bị đổi.

## Test

`tests/integration/ingestion/test_ingest_reaper.py` (đặt `locked_at` lùi về quá khứ, gọi `run_reaper`).

## Tham chiếu

SADD §5.3.7 (Reaper) · F-08
