"""Sinh ID UUIDv7 (SADD §5.4.2) — tăng dần theo thời gian, thân thiện với index B-tree."""

from __future__ import annotations

from uuid import UUID

from uuid_utils.compat import uuid7


def new_id() -> UUID:
    """UUIDv7 dạng `uuid.UUID` chuẩn. Không module nào khác được gọi `uuid.uuid4()`."""
    return uuid7()
