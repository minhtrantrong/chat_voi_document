"""Kiểu dùng chung giữa các module: Actor, Role, Page và cursor phân trang (SADD §5.7.2)."""

from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Generic, TypeVar
from uuid import UUID

from app.shared.errors import ErrorCode, Invalid


class Role(StrEnum):
    END_USER = "END_USER"
    PM = "PM"
    ADMIN = "ADMIN"


@dataclass(frozen=True, slots=True)
class Actor:
    user_id: UUID
    role: Role
    session_id: str

    @property
    def is_admin(self) -> bool:
        return self.role is Role.ADMIN


SYSTEM_SESSION = "system"


def system_actor(user_id: UUID) -> Actor:
    """Actor cho worker hành động thay mặt chủ hội thoại."""
    return Actor(user_id=user_id, role=Role.END_USER, session_id=SYSTEM_SESSION)


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    items: list[T]
    next_cursor: str | None


_CURSOR_SEP = "|"


def encode_cursor(ts: datetime, id_: UUID) -> str:
    """base64url("<iso8601 UTC>|<uuid>"), bỏ padding `=`."""
    if ts.tzinfo is None or ts.utcoffset() is None:
        raise ValueError("cursor cần datetime có timezone")
    raw = f"{ts.astimezone(UTC).isoformat()}{_CURSOR_SEP}{id_}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii").rstrip("=")


def decode_cursor(cursor: str) -> tuple[datetime, UUID]:
    """Giải mã cursor; cursor hỏng hoặc bị sửa → `Invalid(ERR_DOC_422)`."""
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        raw = base64.b64decode(padded.encode("ascii"), altchars=b"-_", validate=True).decode("utf-8")
        ts_part, id_part = raw.split(_CURSOR_SEP)
        ts = datetime.fromisoformat(ts_part)
        id_ = UUID(id_part)
    except (ValueError, binascii.Error, UnicodeError) as exc:
        raise Invalid(ErrorCode.ERR_DOC_422) from exc
    if ts.tzinfo is None:
        raise Invalid(ErrorCode.ERR_DOC_422)
    return ts.astimezone(UTC), id_
