"""Thành phần UI dùng lại: format, trạng thái, nguồn."""

from __future__ import annotations

import re
from dataclasses import asdict, is_dataclass
from typing import Any, cast

import streamlit as st

from app.db import Document, DocumentStatus

STATUS_LABELS: dict[str, str] = {
    DocumentStatus.PROCESSING: "Đang xử lý",
    DocumentStatus.READY: "Sẵn sàng",
    DocumentStatus.ERROR: "Lỗi",
}
STATUS_EMOJI: dict[str, str] = {
    DocumentStatus.PROCESSING: "⏳",
    DocumentStatus.READY: "✅",
    DocumentStatus.ERROR: "❌",
}


STAGE_LABELS: dict[str, str] = {
    "pending": "Đang chờ",
    "validating": "Đang kiểm tra tệp",
    "saving": "Đang lưu tệp",
    "extracting": "Đang đọc văn bản",
    "chunking": "Đang chia đoạn",
    "embedding": "Đang tạo embedding",
    "indexing": "Đang lập chỉ mục",
    "done": "Xong",
}


def ingest_stage_text(file_name: str, stage: str, percent: int | None = None) -> str:
    """Dòng trạng thái xử lý theo từng tệp, vd. '⏳ **a.pdf** — Đang đọc văn bản (15%)'."""
    emoji = STATUS_EMOJI[DocumentStatus.READY if stage == "done" else DocumentStatus.PROCESSING]
    label = STAGE_LABELS.get(stage, STATUS_LABELS[DocumentStatus.PROCESSING])
    suffix = f" ({percent}%)" if percent is not None and stage not in ("pending", "done") else ""
    return f"{emoji} **{md_escape(file_name)}** — {label}{suffix}"


def md_escape(text: str) -> str:
    """Escape ký tự Markdown khi chèn tên tệp do người dùng đặt."""
    for char in "\\`*_{}[]()#+-.!|":
        text = text.replace(char, "\\" + char)
    return text


def truncate_snippet(text: str, *, max_chars: int = 300) -> str:
    cleaned = text.strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars] + "…"


def format_bytes(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024**2:
        return f"{size / 1024:.0f} KB"
    return f"{size / 1024**2:.1f} MB"


def has_ready_documents(docs: list[Document]) -> bool:
    return any(doc.status == DocumentStatus.READY for doc in docs)


def empty_state_message(docs: list[Document]) -> tuple[str, str] | None:
    """Trả (kind, message) khi chưa thể chat; None khi có tài liệu READY."""
    if not docs:
        return ("info", "Tải PDF đầu tiên ở thanh bên để bắt đầu hỏi.")
    if has_ready_documents(docs):
        return None
    if any(doc.status == DocumentStatus.PROCESSING for doc in docs):
        return ("info", "Tài liệu đang được xử lý. Đợi hoàn tất rồi hỏi.")
    return (
        "warning",
        "Chưa có tài liệu sẵn sàng. Kiểm tra lỗi ở thanh bên, xoá tệp lỗi và tải lại PDF khác.",
    )


def status_text(doc: Document) -> str:
    return f"{STATUS_EMOJI[doc.status]} {STATUS_LABELS[doc.status]}"


def source_to_dict(source) -> dict:
    return {
        "label": getattr(source, "label", "?"),
        "doc_id": getattr(source, "doc_id", ""),
        "file_name": getattr(source, "file_name", "tài liệu"),
        "page": getattr(source, "page", 0),
        "chunk_index": getattr(source, "chunk_index", -1),
        "text": getattr(source, "text", ""),
        "score": getattr(source, "score", 0.0),
    }


def _as_dict(source) -> dict:
    if isinstance(source, dict):
        return source
    if is_dataclass(source):
        return asdict(cast(Any, source))
    return source_to_dict(source)


def dedupe_sources(sources: list[dict]) -> list[dict]:
    seen: set[tuple] = set()
    output: list[dict] = []
    for source in sources:
        key = (
            source.get("file_name"),
            source.get("page"),
            source.get("chunk_index"),
        )
        if key in seen:
            continue
        seen.add(key)
        output.append(source)
    return output


def _source_order(source: dict) -> tuple[int, float]:
    label = str(source.get("label") or "")
    match = re.fullmatch(r"S(\d+)", label)
    if match:
        return (0, float(match.group(1)))
    score = source.get("score")
    if isinstance(score, (int, float)):
        return (1, -float(score))
    return (2, 0.0)


def render_sources(sources: list) -> None:
    items = dedupe_sources([_as_dict(source) for source in sources])
    items.sort(key=_source_order)
    if not items:
        return
    with st.expander(f"Nguồn ({len(items)})", expanded=False):
        for source in items:
            label = source.get("label") or "?"
            file_name = source.get("file_name") or "tài liệu"
            page = source.get("page") or "?"
            score = source.get("score")
            header = f"[{label}] {md_escape(str(file_name))} — trang {page}"
            if isinstance(score, (int, float)):
                header += f" · điểm {score:.2f}"
            st.write(header)
            text = str(source.get("text") or "").strip()
            if text:
                st.caption(md_escape(truncate_snippet(text)))
