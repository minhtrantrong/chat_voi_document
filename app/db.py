"""SQLite lưu metadata tài liệu."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from app.config import get_settings


class DocumentStatus(StrEnum):
    PROCESSING = "PROCESSING"
    READY = "READY"
    ERROR = "ERROR"


@dataclass(frozen=True)
class Document:
    id: str
    file_name: str
    stored_path: Path
    size_bytes: int
    page_count: int | None
    status: DocumentStatus
    error_code: str | None
    created_at: str
    processed_at: str | None


SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id            TEXT PRIMARY KEY,
    file_name     TEXT NOT NULL,
    stored_path   TEXT NOT NULL,
    size_bytes    INTEGER NOT NULL,
    page_count    INTEGER,
    status        TEXT NOT NULL CHECK (status IN ('PROCESSING', 'READY', 'ERROR')),
    error_code    TEXT,
    created_at    TEXT NOT NULL,
    processed_at  TEXT
);
CREATE INDEX IF NOT EXISTS idx_documents_created_at
    ON documents(created_at DESC);
"""


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    db_path = get_settings().db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


def _row_to_document(row: sqlite3.Row) -> Document:
    return Document(
        id=row["id"],
        file_name=row["file_name"],
        stored_path=Path(row["stored_path"]),
        size_bytes=row["size_bytes"],
        page_count=row["page_count"],
        status=DocumentStatus(row["status"]),
        error_code=row["error_code"],
        created_at=row["created_at"],
        processed_at=row["processed_at"],
    )


def create_document(
    doc_id: str,
    file_name: str,
    stored_path: Path,
    size_bytes: int,
) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO documents
                (id, file_name, stored_path, size_bytes, page_count,
                 status, error_code, created_at, processed_at)
            VALUES (?, ?, ?, ?, NULL, 'PROCESSING', NULL, ?, NULL)
            """,
            (doc_id, file_name, str(stored_path.resolve()), size_bytes, _now()),
        )


def mark_ready(doc_id: str, page_count: int) -> None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE documents
               SET status = 'READY', page_count = ?, error_code = NULL, processed_at = ?
             WHERE id = ?
            """,
            (page_count, _now(), doc_id),
        )


def mark_error(doc_id: str, error_code: str) -> None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE documents
               SET status = 'ERROR', error_code = ?, processed_at = ?
             WHERE id = ?
            """,
            (error_code, _now(), doc_id),
        )


def get_document(doc_id: str) -> Document | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
    return _row_to_document(row) if row is not None else None


def list_documents() -> list[Document]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM documents ORDER BY created_at DESC, id DESC").fetchall()
    return [_row_to_document(row) for row in rows]


def delete_document(doc_id: str) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))


def count_ready_documents() -> int:
    with connect() as conn:
        row = conn.execute("SELECT COUNT(*) AS n FROM documents WHERE status = 'READY'").fetchone()
    return int(row["n"]) if row is not None else 0


def clear_documents() -> None:
    """Dùng cho eval/reindex; không dùng trong luồng UI thông thường."""
    with connect() as conn:
        conn.execute("DELETE FROM documents")
