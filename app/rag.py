"""Retrieval, context, prompt và NOT_FOUND."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass, field

from app.config import get_settings
from app.embeddings import embed_query
from app.llm import stream_chat
from app.prompts import SYSTEM_PROMPT
from app.vector_store import SearchHit, search_chunks

NOT_FOUND = "Không tìm thấy thông tin này trong các tài liệu đã tải lên."


@dataclass(frozen=True)
class Source:
    label: str
    doc_id: str
    file_name: str
    page: int
    chunk_index: int
    text: str
    score: float


@dataclass(frozen=True)
class PreparedAnswer:
    messages: list[dict[str, str]] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    not_found: bool = False


def build_context(
    hits: list[SearchHit],
    *,
    max_chars: int = 24_000,
) -> tuple[str, list[Source]]:
    seen_ids: set[str] = set()
    seen_chunks: set[tuple[str, int]] = set()
    blocks: list[str] = []
    sources: list[Source] = []
    used = 0

    for hit in hits:
        payload = hit.payload
        doc_id = str(payload.get("doc_id", ""))
        try:
            chunk_index = int(payload.get("chunk_index", -1))
        except (TypeError, ValueError):
            continue
        if not doc_id or chunk_index < 0:
            continue
        if hit.id in seen_ids or (doc_id, chunk_index) in seen_chunks:
            continue
        seen_ids.add(hit.id)
        seen_chunks.add((doc_id, chunk_index))

        text = str(payload.get("text", "")).strip()
        if not text:
            continue

        label = f"S{len(sources) + 1}"
        file_name = str(payload.get("file_name", "tài liệu")).replace("\n", " ")
        try:
            page = int(payload.get("page", 0))
        except (TypeError, ValueError):
            page = 0
        header = f"[{label}] {file_name} — trang {page}\n"
        separator = "\n\n" if blocks else ""
        budget = max_chars - used - len(separator) - len(header)
        if budget <= 0:
            break
        if len(text) > budget:
            text = text[:budget].rstrip()
        block = header + text
        blocks.append(block)
        sources.append(
            Source(
                label=label,
                doc_id=doc_id,
                file_name=file_name,
                page=page,
                chunk_index=chunk_index,
                text=text,
                score=hit.score,
            )
        )
        used += len(separator) + len(block)
        if used >= max_chars:
            break

    return "\n\n".join(blocks), sources


def select_hits(
    hits: list[SearchHit],
    *,
    top_k: int,
    max_per_doc: int,
) -> list[SearchHit]:
    if top_k <= 0:
        raise ValueError("top_k phải > 0")
    if max_per_doc <= 0:
        raise ValueError("max_per_doc phải > 0")

    seen_ids: set[str] = set()
    seen_chunks: set[tuple[str, int]] = set()
    per_doc: Counter[str] = Counter()
    selected: list[SearchHit] = []

    for hit in sorted(hits, key=lambda item: item.score, reverse=True):
        doc_id = str(hit.payload.get("doc_id", ""))
        if not doc_id:
            continue
        try:
            chunk_index = int(hit.payload.get("chunk_index", -1))
        except (TypeError, ValueError):
            continue
        if chunk_index < 0:
            continue
        if hit.id in seen_ids or (doc_id, chunk_index) in seen_chunks:
            continue
        if per_doc[doc_id] >= max_per_doc:
            continue

        seen_ids.add(hit.id)
        seen_chunks.add((doc_id, chunk_index))
        per_doc[doc_id] += 1
        selected.append(hit)
        if len(selected) >= top_k:
            break

    return selected


def _trim_history(history: list[dict], *, max_messages: int) -> list[dict[str, str]]:
    clean = [
        {"role": message["role"], "content": message["content"]}
        for message in history
        if message.get("role") in {"user", "assistant"} and message.get("content")
    ]
    return clean[-max_messages:]


def prepare_answer(
    question: str,
    history: list[dict],
    *,
    selected_doc_ids: list[str] | None = None,
) -> PreparedAnswer:
    question = question.strip()
    if not question:
        raise ValueError("Câu hỏi rỗng.")

    settings = get_settings()
    question = question[: settings.max_question_chars]
    query_vector = embed_query(question)
    hits = search_chunks(
        query_vector,
        limit=settings.top_k,
        score_threshold=settings.score_threshold,
        doc_ids=selected_doc_ids,
    )
    hits = select_hits(
        hits,
        top_k=settings.top_k,
        max_per_doc=settings.max_chunks_per_doc,
    )
    context, sources = build_context(hits, max_chars=settings.max_context_chars)
    if not sources or not context.strip():
        return PreparedAnswer(not_found=True)

    history = _trim_history(history, max_messages=settings.max_history_messages)
    system = SYSTEM_PROMPT.format(context=context, question=question)
    return PreparedAnswer(
        messages=[{"role": "system", "content": system}, *history],
        sources=sources,
    )


def stream_answer(prepared: PreparedAnswer) -> Iterator[str]:
    if prepared.not_found:
        yield NOT_FOUND
        return
    yield from stream_chat(prepared.messages)


def finalize_answer(
    text: str,
    sources: list[Source],
) -> tuple[str, list[Source], bool]:
    cleaned = text.strip()
    if not cleaned or "KHONG_TIM_THAY" in cleaned:
        return NOT_FOUND, [], True
    return cleaned, sources, False


def answer_question(
    question: str,
    history: list[dict],
    *,
    selected_doc_ids: list[str] | None = None,
) -> tuple[str, list[Source], bool]:
    prepared = prepare_answer(
        question,
        history,
        selected_doc_ids=selected_doc_ids,
    )
    if prepared.not_found:
        return NOT_FOUND, [], True
    text = "".join(stream_answer(prepared))
    return finalize_answer(text, prepared.sources)
