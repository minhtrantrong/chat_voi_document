"""Adapter gọi LLM streaming qua API tương thích OpenAI."""

from __future__ import annotations

import time
from collections.abc import Iterable, Iterator
from typing import Any, cast

from openai import APIConnectionError, APITimeoutError, OpenAI, RateLimitError

from app.config import get_settings, require_api_key


class LLMError(Exception):
    def __init__(self, message: str, *, code: str = "LLM_FAILED"):
        self.code = code
        self.message = message
        super().__init__(message)


def _client() -> OpenAI:
    settings = get_settings()
    try:
        require_api_key(settings)
    except RuntimeError as exc:
        raise LLMError(str(exc), code="CONFIG_MISSING") from exc
    return OpenAI(
        api_key=settings.openai_api_key.strip(),
        base_url=settings.openai_base_url.rstrip("/"),
        timeout=60.0,
        max_retries=0,
    )


def stream_chat(
    messages: list[dict[str, str]],
    *,
    client: OpenAI | None = None,
) -> Iterator[str]:
    settings = get_settings()
    client = client or _client()
    emitted = False

    for attempt in range(2):
        try:
            stream = cast(
                Iterable[Any],
                client.chat.completions.create(
                    model=settings.llm_model,
                    messages=cast(Any, messages),
                    temperature=settings.llm_temperature,
                    stream=True,
                ),
            )
            got_any = False
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                text = getattr(delta, "content", None)
                if text:
                    got_any = True
                    emitted = True
                    yield text
            if not got_any:
                raise LLMError("Mô hình không trả về nội dung.")
            return
        except LLMError:
            raise
        except (APIConnectionError, APITimeoutError, RateLimitError) as exc:
            if emitted or attempt == 1:
                raise LLMError("Trợ lý tạm thời không phản hồi. Thử lại sau.") from exc
            time.sleep(2**attempt)
        except Exception as exc:
            raise LLMError(f"Lỗi gọi mô hình: {type(exc).__name__}") from exc

    raise LLMError("Trợ lý tạm thời không phản hồi. Thử lại sau.")
