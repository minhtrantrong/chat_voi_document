"""Qdrant: collection, upsert, search và xoá point."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchAny,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)

from app.chunking import Chunk
from app.config import get_settings


@dataclass(frozen=True)
class SearchHit:
    id: str
    score: float
    payload: dict


class VectorStoreError(Exception):
    def __init__(self, message: str, *, code: str = "QDRANT_UNAVAILABLE"):
        self.code = code
        self.message = message
        super().__init__(message)


def get_client() -> QdrantClient:
    settings = get_settings()
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
        timeout=settings.qdrant_timeout,
    )


def _vector_size(info) -> int | None:
    vectors = info.config.params.vectors
    if isinstance(vectors, dict):
        first = next(iter(vectors.values()), None)
        return getattr(first, "size", None)
    return getattr(vectors, "size", None)


def ensure_collection(client: QdrantClient | None = None) -> None:
    settings = get_settings()
    client = client or get_client()
    name = settings.qdrant_collection

    try:
        exists = client.collection_exists(name)
    except Exception as exc:
        raise VectorStoreError("Không kết nối được Qdrant.") from exc

    if not exists:
        try:
            client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=settings.embedding_dim,
                    distance=Distance.COSINE,
                ),
            )
            client.create_payload_index(
                collection_name=name,
                field_name="doc_id",
                field_schema=PayloadSchemaType.KEYWORD,
            )
        except Exception as exc:
            raise VectorStoreError("Không tạo được collection Qdrant.") from exc
        return

    try:
        info = client.get_collection(name)
    except Exception as exc:
        raise VectorStoreError("Không đọc được thông tin collection Qdrant.") from exc
    current_size = _vector_size(info)
    if current_size is not None and current_size != settings.embedding_dim:
        raise RuntimeError(
            f"Qdrant collection '{name}' có vector size {current_size}, "
            f"nhưng EMBEDDING_DIM={settings.embedding_dim}. "
            "Xoá collection cũ và re-index toàn bộ tài liệu."
        )


def health(client: QdrantClient | None = None) -> bool:
    try:
        client = client or get_client()
        client.get_collections()
        return True
    except Exception:
        return False


def upsert_chunks(
    doc_id: str,
    file_name: str,
    chunks: list[Chunk],
    vectors: list[list[float]],
    *,
    client: QdrantClient | None = None,
    batch_size: int = 128,
) -> None:
    if not chunks:
        return
    if len(chunks) != len(vectors):
        raise ValueError(f"Số chunk ({len(chunks)}) khác số vector ({len(vectors)}).")

    settings = get_settings()
    for chunk, vector in zip(chunks, vectors, strict=True):
        if len(vector) != settings.embedding_dim:
            raise ValueError(
                f"Vector chunk {chunk.chunk_index} có {len(vector)} chiều, "
                f"cần {settings.embedding_dim}."
            )

    client = client or get_client()
    ensure_collection(client)

    points: list[PointStruct] = []
    for chunk, vector in zip(chunks, vectors, strict=True):
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{doc_id}:{chunk.chunk_index}"))
        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "doc_id": doc_id,
                    "file_name": file_name,
                    "page": chunk.page,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text,
                    "char_start": chunk.char_start,
                    "char_end": chunk.char_end,
                },
            )
        )

    for index in range(0, len(points), batch_size):
        try:
            client.upsert(
                collection_name=settings.qdrant_collection,
                points=points[index : index + batch_size],
                wait=True,
            )
        except Exception as exc:
            raise VectorStoreError("Không ghi được vector vào Qdrant.") from exc


def search_chunks(
    query_vector: list[float],
    *,
    limit: int,
    score_threshold: float,
    doc_ids: list[str] | None = None,
    client: QdrantClient | None = None,
) -> list[SearchHit]:
    settings = get_settings()
    client = client or get_client()
    query_filter = None
    if doc_ids:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="doc_id",
                    match=MatchAny(any=doc_ids),
                )
            ]
        )

    try:
        response = client.query_points(
            collection_name=settings.qdrant_collection,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True,
        )
    except Exception as exc:
        raise VectorStoreError("Không tìm kiếm được trong Qdrant.") from exc
    return [
        SearchHit(
            id=str(point.id),
            score=float(point.score),
            payload=dict(point.payload or {}),
        )
        for point in response.points
    ]


def delete_document(doc_id: str, client: QdrantClient | None = None) -> None:
    settings = get_settings()
    client = client or get_client()
    try:
        client.delete(
            collection_name=settings.qdrant_collection,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="doc_id",
                            match=MatchValue(value=doc_id),
                        )
                    ]
                )
            ),
            wait=True,
        )
    except Exception as exc:
        raise VectorStoreError("Không xoá được vector trong Qdrant.") from exc


def count_points(client: QdrantClient | None = None) -> int:
    settings = get_settings()
    client = client or get_client()
    try:
        return int(client.count(settings.qdrant_collection, exact=True).count)
    except Exception as exc:
        raise VectorStoreError("Không đếm được point trong Qdrant.") from exc
