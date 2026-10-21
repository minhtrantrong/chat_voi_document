"""Nguồn thời gian duy nhất của hệ thống (SADD §5.5.2) — thay được bằng `FrozenClock` khi test."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import Protocol
from zoneinfo import ZoneInfo

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


class Clock(Protocol):
    def now(self) -> datetime:
        """Thời điểm hiện tại, luôn aware UTC."""
        ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class FrozenClock:
    """Đồng hồ đứng yên cho test; chỉ đổi khi gọi `advance`."""

    def __init__(self, at: datetime) -> None:
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("FrozenClock cần datetime có timezone")
        self._now = at.astimezone(UTC)

    def now(self) -> datetime:
        return self._now

    def advance(self, **kw: float) -> None:
        """Tiến đồng hồ, tham số như `timedelta` (seconds=, minutes=, days=...)."""
        self._now += timedelta(**kw)


def to_vn(dt: datetime) -> datetime:
    return dt.astimezone(VN_TZ)


def today_vn(clock: Clock) -> date:
    return to_vn(clock.now()).date()
