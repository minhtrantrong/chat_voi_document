# F-08 — Job queue trên PostgreSQL: enqueue, claim, NOTIFY, reaper

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng dùng chung (Implement_plan §15; Phần I §4 S1, mục 1.5) |
| Sprint | S1 |
| Tầng | INF / WRK |
| Ước lượng | 3d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | PLT-08, F-07 |
| Chặn | F-09, PLT-12, T-01-4, T-04-4, T-07-2, T-06-3 |

## Bối cảnh

ADR-003 và SADD §5.3.7: queue bền vững trong Postgres để tạo nghiệp vụ + job trong **cùng transaction**. `LISTEN/NOTIFY` được thêm để worker nhận job ngay (ngân sách first-token ≤ 200 ms cho bước claim, §17 US-13).

## Phạm vi

**Làm:** `app/shared/jobs.py` (port + `Job`), `app/infrastructure/db/jobs.py` (cài đặt), reaper chung có hook theo loại job.

**Không làm:** vòng lặp worker và registry (F-09), scheduler (PLT-12), hook cụ thể cho answer/ingest (T-13-8, T-04-5).

## Đặc tả

```python
@dataclass(frozen=True)
class Job:
    id: int; type: str; payload: dict[str, Any]; attempts: int; max_attempts: int
    locked_by: str | None; last_error: str | None

class JobQueuePort(Protocol):
    def enqueue(self, tx: UnitOfWork, type: str, payload: Mapping[str, Any], *,
                priority: int = 100, max_attempts: int = 3, run_at: datetime | None = None) -> int: ...
    def claim(self, worker_id: str, types: Sequence[str]) -> Job | None: ...
    def complete(self, job_id: int) -> None: ...
    def fail(self, job_id: int, error: str, *, retry: bool) -> None: ...
    def wait_for_notify(self, timeout_s: float) -> None: ...
```

**enqueue:** `INSERT INTO jobs(...)` + `SELECT pg_notify('cvd_jobs', :type)` trong **cùng** `tx` (Postgres chỉ gửi NOTIFY khi commit). Tự thêm `corrId` từ contextvar vào payload. Vi phạm partial unique (`ux_jobs_answer`, `ux_jobs_document`) thì ném `Conflict` để caller quyết định.

**claim:** đúng câu SQL ở SADD §5.3.7 (`FOR UPDATE SKIP LOCKED`, `ORDER BY priority DESC, run_at`, `attempts = attempts + 1`), transaction riêng, commit ngay.

**fail(retry=True):** nếu `attempts < max_attempts` thì `status='QUEUED', run_at = now() + backoff, last_error=:e, locked_at=NULL`; ngược lại `status='DEAD'`. Backoff = `min(300, 15 * 2**attempts) + random(0..5)` giây. Riêng `document.ingest` dùng lịch cố định 30 s / 2 phút / 5 phút (SADD §5.3.3): cho phép truyền `backoff_schedule` theo loại job.
**fail(retry=False):** `status='FAILED'`.
**complete:** `status='SUCCEEDED'`.

**wait_for_notify:** connection riêng `LISTEN cvd_jobs`, `select()` trên socket với timeout (fallback poll 1 s).

**Reaper** (`run_reaper(now)`, mỗi 60 s trong mọi worker, idempotent):

```text
expired = SELECT ... FROM jobs WHERE status='RUNNING' AND locked_at < now() - visibility_timeout FOR UPDATE SKIP LOCKED
for j in expired:
   if j.attempts < j.max_attempts: UPDATE → QUEUED (locked_at NULL)
   else: UPDATE → DEAD, last_error='WORKER_LOST'; gọi hook REAPER_HOOKS[j.type](tx, j) nếu có
```

`visibility_timeout`: mặc định 15 phút; `answer.generate` dùng 3 phút (answer không retry, cần kết thúc sớm cho UI). `REAPER_HOOKS: dict[str, Callable[[UnitOfWork, Job], None]]` được đăng ký từ module nghiệp vụ (T-04-5, T-13-8).

Dọn lịch sử: job `SUCCEEDED` > 30 ngày xoá theo lô 1.000 (gọi từ `retention.sweep`, T-15-3).

## Tiêu chí xong

- [ ] Hai worker claim song song 100 job: mỗi job được xử lý đúng một lần.
- [ ] Job enqueue trong transaction bị rollback thì không tồn tại và không có NOTIFY.
- [ ] Worker đang `wait_for_notify` nhận job trong ≤ 100 ms sau khi commit (đo trong test).
- [ ] Job RUNNING quá hạn được reaper trả về QUEUED; hết lượt thì DEAD và hook được gọi.

## Test

`tests/integration/jobs/test_queue.py`: claim đồng thời (threads); backoff (FrozenClock); retry hết lượt → DEAD; partial unique ném `Conflict`; NOTIFY latency; reaper + hook giả.

## Tham chiếu

ADR-003 · SADD §5.3.7, §5.3.9, §5.7.4
