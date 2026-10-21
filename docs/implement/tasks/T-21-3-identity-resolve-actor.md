# T-21-3 — IdentityService: JIT provision người dùng và ánh xạ nhóm → role

| Thuộc tính | Giá trị |
|---|---|
| Story | US-21 (P0) — AC-21.1 |
| Sprint | S1 |
| Tầng | APP / INF |
| Ước lượng | 1d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | PLT-08, F-01, F-05, F-07, T-21-2 |
| Chặn | Mọi service cần `Actor` thật |

## Bối cảnh

SADD §5.8.2: claims tối thiểu `sub`, `email`, `name`, `groups`; nhóm `cvd-admins` → ADMIN, `cvd-pms` → PM, `cvd-users` → END_USER; **mặc định từ chối**; user `DISABLED` bị từ chối; role đọc từ IdP/DB mỗi phiên, không nhận từ client.

## Phạm vi

**Làm:** `app/identity/{domain,service,repository,schemas}.py`, repository Postgres, cấu hình `ROLE_GROUP_MAPPING`.

## Đặc tả

```python
# app/identity/domain.py
DEFAULT_GROUP_ROLES = {"cvd-admins": Role.ADMIN, "cvd-pms": Role.PM, "cvd-users": Role.END_USER}
ROLE_RANK = {Role.END_USER: 1, Role.PM: 2, Role.ADMIN: 3}
def role_from_groups(groups: Iterable[str], mapping: Mapping[str, Role]) -> Role | None:
    """Trả role cao nhất trong các nhóm khớp; không khớp nhóm nào → None."""

@dataclass(frozen=True)
class Claims:
    sub: str; email: str; name: str; groups: tuple[str, ...]; iat: int | None

# app/identity/service.py
class IdentityService:
    def resolve_actor(self, claims: Claims, session_id: str) -> Actor:
        role = role_from_groups(claims.groups, self._mapping)
        if role is None:
            self._audit_denied(claims, "no_group"); AUTH_FAILURES.labels("no_group").inc()
            raise Forbidden(ErrorCode.ERR_AUTH_403)
        with self._uow() as tx:
            user = self._users.upsert_by_subject(tx, claims.sub, email=claims.email,
                                                 display_name=claims.name or claims.email, role=role)
            if user.status == "DISABLED": ... raise Forbidden
            self._users.touch_login(tx, user.id, self._clock.now())
            self._audit.record(tx, Actor(user.id, role, session_id), AuditAction.AUTH_LOGIN, "user", user.id)
        return Actor(user.id, role, session_id)
```

- `upsert_by_subject`: `INSERT … ON CONFLICT (subject) DO UPDATE SET email, display_name, role = EXCLUDED.role` (role **luôn** theo nhóm IdP hiện tại, để rút quyền ở IdP có hiệu lực ở phiên sau). `status` **không** bị ghi đè (admin có thể DISABLED thủ công trong DB).
- `ROLE_GROUP_MAPPING` đọc từ env dạng JSON (thêm vào PLT-05), mặc định `DEFAULT_GROUP_ROLES`.
- UI (`get_actor` ở F-11): đọc `st.user` → `Claims` (`groups` có thể là list hoặc chuỗi cách nhau bởi dấu phẩy, chuẩn hoá về tuple); `session_id` = `st.context.session_id` nếu có, không thì `new_id()` lưu trong `session_state`; gọi `resolve_actor` **một lần mỗi session** rồi lưu `Actor` vào `K.AUTH_ACTOR`.
- `email` lưu dạng citext; **không** log email (log `hash_id(sub)`).

## Tiêu chí xong

- [ ] Đăng nhập lần đầu tạo bản ghi `users`; lần sau cập nhật `last_login_at`, không tạo trùng.
- [ ] User thuộc cả `cvd-users` và `cvd-admins` nhận ADMIN.
- [ ] User không thuộc nhóm nào: `Forbidden`, có audit `auth.denied`, metric tăng.
- [ ] User bị đổi nhóm ở IdP: phiên sau role mới có hiệu lực.

## Test

- `tests/unit/identity/test_roles.py`: `role_from_groups` mọi tổ hợp.
- `tests/integration/identity/test_resolve_actor.py`: JIT, cập nhật, DISABLED, không nhóm.

## Tham chiếu

SADD §5.8.2, §5.8.3, ADR-006 · US-21
