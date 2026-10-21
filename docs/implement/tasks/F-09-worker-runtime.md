# F-09 — Worker runtime: vòng lặp, registry handler, graceful shutdown

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng dùng chung (Implement_plan §15; Phần I §4 S1, mục 1.6) |
| Sprint | S1 |
| Tầng | WRK |
| Ước lượng | 1d (gồm 0.5d registry + 0.5d runtime/shutdown) |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | F-08, PLT-06 |
| Chặn | Mọi handler job (T-04-4, T-06-3, T-13-3, PLT-10, T-15-3, T-23-1) |

## Bối cảnh

SADD §5.3.1: `python -m app.worker --queues ...` với thread pool; §5.3.10: graceful shutdown tối đa 30 s, trả job chưa xong về QUEUED.

## Phạm vi

**Làm:** `app/worker.py` (CLI + vòng lặp), `app/shared/worker_context.py` (`WorkerContext`), registry `HANDLERS`, heartbeat cho healthcheck.

## Đặc tả

CLI:

```
python -m app.worker --queues answer.generate,document.purge --threads 10 --metrics-port 9102 [--scheduler] [--healthcheck]
```

```python
@dataclass(frozen=True)
class WorkerContext:
    uow: UnitOfWorkFactory; jobs: JobQueuePort; clock: Clock; config: ConfigService
    storage: ObjectStoragePort; pdf: PdfPort; embedding: EmbeddingPort; llm: LLMPort
    stream: TokenStreamPort; telemetry: TelemetryService; audit: AuditService
    worker_id: str                                  # f"{hostname}:{pid}"

Handler = Callable[[Job, WorkerContext], None]
HANDLERS: dict[str, Handler] = {}                  # đăng ký bằng decorator @handles("document.ingest")
```

Vòng lặp (mỗi thread):

```text
while not stopping:
    job = jobs.claim(worker_id, queues)
    if job is None: jobs.wait_for_notify(timeout_s=1.0); continue
    set corr_id = job.payload.get("corrId")
    t0 = clock; try:
        HANDLERS[job.type](job, ctx); jobs.complete(job.id); JOBS_TOTAL{status=SUCCEEDED}
    except PermanentJobError as e: jobs.fail(job.id, e.code, retry=False)
    except RetryableJobError as e: jobs.fail(job.id, e.code, retry=True)
    except Exception as e:        jobs.fail(job.id, type(e).__name__, retry=True); log.exception (không kèm payload nhạy cảm)
    finally: JOB_DURATION.observe
```

- Thread phụ: reaper (60 s), heartbeat (ghi `time.time()` vào `/tmp/worker_heartbeat` mỗi 15 s), scheduler nếu `--scheduler` (PLT-12).
- `--healthcheck`: đọc heartbeat file, quá 60 s thì thoát 1 (dùng cho Docker healthcheck, PLT-04).
- SIGTERM/SIGINT: đặt `stopping`, ngừng claim, chờ các thread tối đa 30 s; job vẫn đang chạy sau 30 s thì `UPDATE jobs SET status='QUEUED', locked_at=NULL WHERE id=:id AND locked_by=:me` rồi thoát.
- Handler **không** giữ transaction khi gọi LLM/embedding/S3 (SADD §5.3.1 quy tắc 6): mỗi handler tự mở UoW ngắn.

## Tiêu chí xong

- [ ] Handler giả ném `PermanentJobError` → FAILED; `RetryableJobError` → QUEUED với backoff; exception lạ → retry.
- [ ] Gửi SIGTERM khi đang chạy handler dài 60 s: worker thoát trong ≈ 30 s, job về QUEUED.
- [ ] `--healthcheck` trả 1 khi heartbeat cũ.

## Test

`tests/integration/worker/test_runtime.py`: chạy worker trong thread với handler giả; test shutdown bằng subprocess + `signal`.

## Tham chiếu

SADD §5.3.1, §5.3.10 · F-08
