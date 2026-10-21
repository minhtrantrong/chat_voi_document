# F-10 — Sandbox subprocess cho mọi thao tác parse/render PDF

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng dùng chung (Implement_plan §15) |
| Sprint | S1 |
| Tầng | INF |
| Ước lượng | 1.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | PLT-01 |
| Chặn | T-01-2, T-04-1, T-13d-1, PLT-11 |

## Bối cảnh

SADD §5.8.4 mục 7: `web` và `worker` **không được** parse PDF trong process chính; extract chạy trong subprocess `spawn` có `RLIMIT_AS` và timeout, để PDF độc chỉ giết được process con.

## Phạm vi

**Làm:** `app/infrastructure/pdf/sandbox.py`: chạy một hàm top-level trong process con, có giới hạn RAM và thời gian; pool dài hạn cho render trang (T-13d-1 dùng).

## Đặc tả

```python
class SandboxTimeout(Exception): ...
class SandboxCrashed(Exception): ...         # process con chết (OOM, segfault)

def run_in_sandbox(fn: Callable[..., R], *args: Any, timeout_s: float, mem_mb: int) -> R:
    """fn phải là hàm top-level (pickle được). Tham số chỉ là đường dẫn tệp và giá trị nhỏ."""

class SandboxPool:
    """ProcessPoolExecutor(mp_context=spawn, max_workers=n, initializer=_set_limits(mem_mb)).
       Dùng cho render trang (nhiều lần, nhanh). Worker con bị hỏng → tạo lại pool."""
    def submit(self, fn, *args, timeout_s: float) -> R: ...
```

Cài đặt `run_in_sandbox`:
1. `ctx = multiprocessing.get_context("spawn")`, tạo `Process` với `target=_child(fn, args, conn, mem_mb)` và `Pipe`.
2. Trong process con: `resource.setrlimit(RLIMIT_AS, (mem_mb*MiB,)*2)` (chỉ Linux; Windows bỏ qua và log debug), gọi `fn`, gửi kết quả hoặc exception qua pipe.
3. Process cha: `conn.poll(timeout_s)`; hết giờ thì `terminate()` → `kill()` sau 2 s → `SandboxTimeout`.
4. Process con thoát mà không gửi gì (exit code ≠ 0) → `SandboxCrashed`.
5. Kết quả trả qua pipe phải nhỏ (metadata, list text các trang). Với tài liệu lớn, process con ghi kết quả ra tệp JSON tạm và chỉ trả **đường dẫn**.

Giá trị dùng ở các task:

| Dùng ở | timeout | RAM |
|---|---|---|
| `inspect` khi upload (T-01-2) | 10 s | 512 MB |
| `extract_pages` trong ingest (T-04-1) | 300 s | 1536 MB |
| `render_page` (T-13d-1, pool 2 worker) | 15 s | 768 MB |

## Tiêu chí xong

- [ ] Hàm con chạy vô hạn → `SandboxTimeout` đúng hạn, không còn process zombie.
- [ ] Hàm con cấp phát > giới hạn RAM (Linux) → `SandboxCrashed`/`MemoryError`, process cha vẫn sống.
- [ ] Exception trong hàm con được truyền lại với đúng kiểu.

## Test

`tests/integration/pdf/test_sandbox.py` (đánh dấu `skipif` RLIMIT trên Windows): timeout, OOM, exception, kết quả lớn qua tệp tạm, pool tự phục hồi sau crash.

## Tham chiếu

SADD §5.8.4, RISK-10
