# T-13-2 — TokenStreamPort trên Redis Streams

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13 (P0) |
| Sprint | S3 |
| Tầng | INF |
| Ước lượng | 0.75d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | T-13-1 (GO), T-07-1 (`StreamEvent`) |
| Chặn | T-13-3, T-13-4, T-13-5 |

## Bối cảnh

SADD §5.3.4 bảng khoá Redis: stream `answer:{answerId}`, field `type/data/seq`, `EXPIRE 3600`, `MAXLEN ~ 5000`, cờ cancel `answer:{id}:cancel` TTL 300 s, đọc `XREAD COUNT 200` không block.

## Phạm vi

**Làm:** `TokenStreamPort` ở `app/qa/ports.py`, cài đặt `app/infrastructure/redis/token_stream.py`, `InMemoryTokenStream` cho test.

## Đặc tả

```python
class TokenStreamPort(Protocol):
    def append(self, answer_id: UUID, type: str, data: str = "") -> None: ...
    def read(self, answer_id: UUID, last_id: str, count: int = 200) -> TokenBatch: ...
    def request_cancel(self, answer_id: UUID) -> None: ...
    def is_cancelled(self, answer_id: UUID) -> bool: ...
```

| Method | Lệnh Redis |
|---|---|
| `append` | pipeline: `XADD answer:{id} MAXLEN ~ 5000 * type <t> data <d> seq <n>` + `EXPIRE answer:{id} 3600` |
| `read` | `XREAD COUNT 200 STREAMS answer:{id} <last_id>` (không truyền BLOCK) → `TokenBatch(events, last_id mới hoặc giữ nguyên)` |
| `request_cancel` | `SET answer:{id}:cancel 1 EX 300` |
| `is_cancelled` | `EXISTS answer:{id}:cancel` |

- `seq`: bộ đếm trong process của worker cho mỗi answer (bắt đầu 0), giúp UI phát hiện mất sự kiện (chỉ log).
- `data` của `token` là một **lô** token (đã gom), không phải một token.
- Kiểu sự kiện hợp lệ: `status` (`retrieving` | `generating`), `token`, `reset`, `done` (data = outcome viết thường: `answered`, `not_found`, `aborted`, `error`).
- `socket_timeout=1`; lỗi Redis ném `TokenStreamUnavailable`.

## Tiêu chí xong

- [ ] Ghi 6.000 sự kiện → stream giữ khoảng 5.000 gần nhất; TTL được gia hạn mỗi lần ghi.
- [ ] `read` với `last_id` cuối cùng trả danh sách rỗng và giữ nguyên `last_id`.
- [ ] Cờ cancel tự hết sau 300 s.

## Test

`tests/integration/redis/test_token_stream.py`.

## Tham chiếu

ADR-005 · SADD §5.3.4 (Chi tiết kỹ thuật), §5.7.3
