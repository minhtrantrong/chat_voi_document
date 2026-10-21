# T-13c-2 — `DocumentService.resolve_scope`: kiểm tra phạm vi ở server

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13c (P1); US-07 (điều kiện có tài liệu READY) |
| Sprint | S3 |
| Tầng | APP |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-05-1, T-05-2 |
| Chặn | T-07-2 |

## Bối cảnh

Không tin `doc_id` do UI gửi (SADD §4.5). Scope phải được lọc lại theo quyền và trạng thái ở server.

## Phạm vi

**Làm:** method `resolve_scope(actor, ids) -> ResolvedScope`.

## Đặc tả

```python
@dataclass(frozen=True)
class ResolvedScope:
    ids: list[UUID]              # các id hợp lệ (READY, trong quyền); rỗng khi người dùng không giới hạn
    has_any_ready: bool
    @property
    def ids_or_empty(self) -> list[UUID]: return self.ids

def resolve_scope(self, actor: Actor, ids: Sequence[UUID]) -> ResolvedScope:
    if not ids:
        return ResolvedScope([], has_any_ready=self._repo.exists_ready_visible(actor.user_id))
    valid = self._repo.filter_ready_visible(actor.user_id, ids[:200])    # giới hạn 200 id
    return ResolvedScope(valid, has_any_ready=bool(valid))
```

```sql
-- filter_ready_visible
SELECT id FROM documents
WHERE id = ANY(:ids) AND status = 'READY' AND deleted_at IS NULL
  AND (owner_id = :uid OR visibility = 'SHARED');
-- exists_ready_visible: cùng điều kiện, không lọc id, LIMIT 1
```

- Người dùng chọn một số id nhưng **không id nào** hợp lệ (ví dụ vừa bị xoá) → `has_any_ready=False` → `ask` trả `ERR_NO_READY_DOC` (không âm thầm mở rộng ra tất cả tài liệu).
- Id không hợp lệ bị bỏ im lặng (log debug số lượng), không báo lỗi để không lộ sự tồn tại.

## Tiêu chí xong

- [ ] Id private của người khác bị loại.
- [ ] Danh sách rỗng + có tài liệu READY → `has_any_ready=True`, `ids=[]`.

## Test

`tests/integration/documents/test_resolve_scope.py`; T-13c-3.

## Tham chiếu

US-13c · SADD §4.5, §5.8.3
