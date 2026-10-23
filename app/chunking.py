"""Chia văn bản theo trang thành các chunk có overlap."""

from __future__ import annotations

from dataclasses import dataclass

from app.pdf import PageText

CHARS_PER_TOKEN = 4


@dataclass(frozen=True)
class Chunk:
    page: int
    chunk_index: int
    text: str
    char_start: int
    char_end: int


def _find_sentence_break(text: str, start: int, hard_end: int) -> int:
    if hard_end >= len(text):
        return len(text)
    min_break = start + int((hard_end - start) * 0.6)
    for i in range(hard_end, min_break, -1):
        if text[i - 1] in ".!?\n":
            return i
    return hard_end


def chunk_pages(
    pages: list[PageText],
    *,
    size_tokens: int = 700,
    overlap_tokens: int = 100,
) -> list[Chunk]:
    if size_tokens <= 0:
        raise ValueError("size_tokens phải > 0")
    max_chars = size_tokens * CHARS_PER_TOKEN
    overlap_chars = max(0, overlap_tokens * CHARS_PER_TOKEN)
    if overlap_chars >= max_chars:
        raise ValueError("overlap phải nhỏ hơn size")

    chunks: list[Chunk] = []
    global_index = 0

    for page in pages:
        text = page.text
        n = len(text)
        if n == 0:
            continue

        if n <= max_chars:
            chunks.append(Chunk(page.page, global_index, text, 0, n))
            global_index += 1
            continue

        start = 0
        while start < n:
            hard_end = min(start + max_chars, n)
            end = _find_sentence_break(text, start, hard_end)

            raw = text[start:end]
            left = len(raw) - len(raw.lstrip())
            right = len(raw) - len(raw.rstrip())
            chunk_text = raw.strip()
            chunk_start = start + left
            chunk_end = end - right

            if chunk_text:
                chunks.append(Chunk(page.page, global_index, chunk_text, chunk_start, chunk_end))
                global_index += 1

            if end >= n:
                break

            next_start = max(0, end - overlap_chars)
            if next_start <= start:
                next_start = end
            start = next_start

    return chunks
