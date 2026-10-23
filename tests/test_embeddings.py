from __future__ import annotations

from types import SimpleNamespace

import pytest

from app import embeddings as module
from app.config import get_settings
from app.embeddings import EmbeddingError, embed_query, embed_texts


class FakeEmbeddings:
    def __init__(self, *, dim=8, fail_times=0, error=None, drop=0):
        self.dim = dim
        self.fail_times = fail_times
        self.error = error
        self.drop = drop
        self.calls: list[list[str]] = []

    def create(self, *, model, input):
        self.calls.append(list(input))
        if len(self.calls) <= self.fail_times:
            raise self.error
        data = [
            SimpleNamespace(index=index, embedding=[float(index + 1)] * self.dim)
            for index in range(len(input) - self.drop)
        ]
        return SimpleNamespace(data=data)


class FakeClient:
    def __init__(self, **kwargs):
        self.embeddings = FakeEmbeddings(**kwargs)


def test_empty_input_returns_empty_without_client():
    assert embed_texts([]) == []


def test_embeds_in_batches(settings):
    client = FakeClient()
    vectors = embed_texts(["a", "b", "c"], client=client)
    assert len(vectors) == 3
    assert [len(call) for call in client.embeddings.calls] == [2, 1]
    assert all(len(vector) == 8 for vector in vectors)


def test_embed_query(settings):
    client = FakeClient()
    vector = embed_query("hello", client=client)
    assert len(vector) == 8
    assert client.embeddings.calls == [["hello"]]


def test_batch_order_preserved(settings, monkeypatch):
    monkeypatch.setenv("EMBEDDING_BATCH_SIZE", "3")
    get_settings.cache_clear()

    class ShuffledEmbeddings:
        def create(self, *, model, input):
            data = [
                SimpleNamespace(
                    index=index,
                    embedding=[float(index)] + [0.0] * 7,
                )
                for index in reversed(range(len(input)))
            ]
            return SimpleNamespace(data=data)

    class Client:
        embeddings = ShuffledEmbeddings()

    vectors = embed_texts(["a", "b", "c"], client=Client())
    assert [vector[0] for vector in vectors] == [0.0, 1.0, 2.0]


def test_embed_query_empty_raises(settings):
    with pytest.raises(EmbeddingError):
        embed_query("   ", client=FakeClient())


def test_no_response_raises(settings):
    class NoResponse:
        def create(self, **_kwargs):
            return None

    class Client:
        embeddings = NoResponse()

    with pytest.raises(EmbeddingError, match="phản hồi"):
        embed_texts(["a"], client=Client())


def test_blank_text_raises(settings):
    with pytest.raises(EmbeddingError):
        embed_texts(["a", "  "], client=FakeClient())


def test_dimension_mismatch_raises(settings):
    with pytest.raises(EmbeddingError, match="chiều"):
        embed_texts(["a"], client=FakeClient(dim=4))


def test_count_mismatch_raises(settings):
    with pytest.raises(EmbeddingError, match="không khớp"):
        embed_texts(["a"], client=FakeClient(drop=1))


class DummyError(Exception):
    pass


def test_retries_transient_errors(settings, monkeypatch):
    for name in ("APIConnectionError", "APITimeoutError", "RateLimitError"):
        monkeypatch.setattr(module, name, DummyError)
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)
    client = FakeClient(fail_times=2, error=DummyError("temporary"))
    vectors = embed_texts(["a"], client=client)
    assert len(vectors) == 1
    assert len(client.embeddings.calls) == 3


def test_retry_exhausted_raises(settings, monkeypatch):
    for name in ("APIConnectionError", "APITimeoutError", "RateLimitError"):
        monkeypatch.setattr(module, name, DummyError)
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)
    client = FakeClient(fail_times=3, error=DummyError("temporary"))
    with pytest.raises(EmbeddingError):
        embed_texts(["a"], client=client)
    assert len(client.embeddings.calls) == 3


def test_non_transient_error_raises(settings):
    with pytest.raises(EmbeddingError):
        embed_texts(["a"], client=FakeClient(fail_times=1, error=ValueError("bad")))


def test_missing_api_key(settings, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()
    with pytest.raises(EmbeddingError) as exc:
        embed_texts(["a"])
    assert exc.value.code == "CONFIG_MISSING"
