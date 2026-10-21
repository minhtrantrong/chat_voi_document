"""Mô hình lỗi dùng chung (SADD §5.5.2).

Bản tối thiểu phục vụ F-01; F-02 hoàn thiện enum, các lớp con còn lại và lỗi job.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Any


class ErrorCode(StrEnum):
    ERR_DOC_422 = "ERR-DOC-422"
    ERR_INTERNAL = "ERR-INTERNAL"


class AppError(Exception):
    def __init__(
        self, code: ErrorCode, params: Mapping[str, Any] | None = None, *, retryable: bool = False
    ) -> None:
        super().__init__(code.value)
        self.code = code
        self.params: dict[str, Any] = dict(params or {})
        self.retryable = retryable

    def __str__(self) -> str:
        return self.code.value


class Invalid(AppError): ...
