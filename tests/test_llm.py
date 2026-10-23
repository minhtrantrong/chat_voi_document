from __future__ import annotations

from types import SimpleNamespace

import pytest

from app import llm as module
from app.config import get_settings
from app.llm import LLMError, stream_chat

MESSAGES = [{"role": "user", "content": "hello"}]


class FakeCompletions:
    def __init__(self, *, texts=("Xin", " chào"), fail_times=0, error=None, fail_after=None):
        self.texts = texts
        self.fail_times = fail_times
        self.error = error
        self.fail_after = fail_after
        self.calls = 0

    def create(self, **_kwargs):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise self.error

        def generate():
            for index, text in enumerate(self.texts):
                if self.fail_after is not None and index == self.fail_after:
                    raise self.error
                yield SimpleNamespace(
                    choices=[SimpleNamespace(delta=SimpleNamespace(content=text))]
                )

        return generate()


class FakeClient:
    def __init__(self, **kwargs):
        self.chat = SimpleNamespace(completions=FakeCompletions(**kwargs))


def test_streams_content(settings):
    client = FakeClient()
    assert "".join(stream_chat(MESSAGES, client=client)) == "Xin chào"
    assert client.chat.completions.calls == 1


def test_empty_stream_raises(settings):
    with pytest.raises(LLMError):
        list(stream_chat(MESSAGES, client=FakeClient(texts=())))


def test_skips_chunks_without_choices(settings):
    class Completions:
        def create(self, **_kwargs):
            yield SimpleNamespace(choices=[])
            yield SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="ok"))])

    client = SimpleNamespace(chat=SimpleNamespace(completions=Completions()))
    assert "".join(stream_chat(MESSAGES, client=client)) == "ok"


class DummyError(Exception):
    pass


def test_retries_before_first_token(settings, monkeypatch):
    for name in ("APIConnectionError", "APITimeoutError", "RateLimitError"):
        monkeypatch.setattr(module, name, DummyError)
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)
    client = FakeClient(texts=("ok",), fail_times=1, error=DummyError("temporary"))
    assert "".join(stream_chat(MESSAGES, client=client)) == "ok"
    assert client.chat.completions.calls == 2


def test_does_not_retry_after_first_token(settings, monkeypatch):
    for name in ("APIConnectionError", "APITimeoutError", "RateLimitError"):
        monkeypatch.setattr(module, name, DummyError)
    client = FakeClient(texts=("one", "two"), error=DummyError("temporary"), fail_after=1)
    stream = stream_chat(MESSAGES, client=client)
    assert next(stream) == "one"
    with pytest.raises(LLMError):
        next(stream)
    assert client.chat.completions.calls == 1


def test_non_transient_error(settings):
    client = FakeClient(fail_times=1, error=ValueError("bad"))
    with pytest.raises(LLMError):
        list(stream_chat(MESSAGES, client=client))


def test_retry_exhausted(settings, monkeypatch):
    for name in ("APIConnectionError", "APITimeoutError", "RateLimitError"):
        monkeypatch.setattr(module, name, DummyError)
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)
    client = FakeClient(fail_times=2, error=DummyError("temporary"))
    with pytest.raises(LLMError):
        list(stream_chat(MESSAGES, client=client))
    assert client.chat.completions.calls == 2


def test_missing_api_key(settings, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()
    with pytest.raises(LLMError) as exc:
        list(stream_chat(MESSAGES))
    assert exc.value.code == "CONFIG_MISSING"
