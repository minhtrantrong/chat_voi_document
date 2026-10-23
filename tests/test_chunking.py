from __future__ import annotations

import pytest

from app.chunking import chunk_pages
from app.pdf import PageText


def test_single_short_page_keeps_offsets():
    text = "Short text."
    chunks = chunk_pages([PageText(1, text)], size_tokens=100, overlap_tokens=10)
    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.text == text
    assert text[chunk.char_start : chunk.char_end] == chunk.text


def test_long_page_has_overlap_and_offsets():
    text = "abcdefghijklmnopqrstuvwxyz"
    chunks = chunk_pages([PageText(1, text)], size_tokens=3, overlap_tokens=1)
    assert len(chunks) == 3
    for chunk in chunks:
        assert text[chunk.char_start : chunk.char_end] == chunk.text
    for left, right in zip(chunks, chunks[1:], strict=False):
        assert right.char_start < left.char_end


def test_chunks_do_not_cross_pages():
    pages = [
        PageText(1, "a" * 40),
        PageText(2, "b" * 40),
    ]
    chunks = chunk_pages(pages, size_tokens=3, overlap_tokens=1)
    assert {chunk.page for chunk in chunks} == {1, 2}
    assert all(set(chunk.text) == {"a"} for chunk in chunks if chunk.page == 1)
    assert all(set(chunk.text) == {"b"} for chunk in chunks if chunk.page == 2)


def test_sentence_break_prefers_punctuation():
    text = "Sentence one. Sentence two. Sentence three."
    chunks = chunk_pages([PageText(1, text)], size_tokens=4, overlap_tokens=0)
    assert chunks
    assert all(chunk.text.endswith(".") for chunk in chunks)


def test_global_chunk_indexes_are_sequential():
    pages = [
        PageText(1, "First page has enough text."),
        PageText(2, "Second page has enough text."),
    ]
    chunks = chunk_pages(pages, size_tokens=100, overlap_tokens=10)
    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))


def test_invalid_overlap_raises():
    with pytest.raises(ValueError):
        chunk_pages([PageText(1, "text")], size_tokens=10, overlap_tokens=10)


def test_invalid_size_raises():
    with pytest.raises(ValueError):
        chunk_pages([PageText(1, "text")], size_tokens=0, overlap_tokens=0)


def test_empty_pages_are_skipped():
    assert chunk_pages([PageText(1, "")], size_tokens=10, overlap_tokens=1) == []


def test_chunk_size_limit():
    text = "a" * 100
    chunks = chunk_pages([PageText(1, text)], size_tokens=3, overlap_tokens=0)
    assert all(len(chunk.text) <= 12 for chunk in chunks)


def test_long_word_does_not_loop():
    text = "a" * 10_000
    chunks = chunk_pages([PageText(1, text)], size_tokens=3, overlap_tokens=1)
    assert len(chunks) > 1
    assert sum(len(chunk.text) for chunk in chunks) >= len(text)


def test_overlap_is_positive():
    text = "b" * 100
    chunks = chunk_pages([PageText(1, text)], size_tokens=3, overlap_tokens=0)
    assert all(
        right.char_start == left.char_end for left, right in zip(chunks, chunks[1:], strict=False)
    )

    chunks_overlap = chunk_pages([PageText(1, text)], size_tokens=3, overlap_tokens=1)
    assert any(
        right.char_start < left.char_end
        for left, right in zip(chunks_overlap, chunks_overlap[1:], strict=False)
    )
