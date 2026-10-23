"""Adapter embedding qua API tương thích OpenAI."""

from __future__ import annotations

import time

from openai import APIConnectionError, APITimeoutError, OpenAI, RateLimitError

from app.config import get_settings, require_api_key


class EmbeddingError(Exception):
    def __init__(self, message: str, *, code: str = "EMBEDDING_FAILED"):
        self.code = code
        self.message = message
        super().__init__(message)


def _client() -> OpenAI:
    settings = get_settings()
    try:
        require_api_key(settings)
    except RuntimeError as exc:
        raise EmbeddingError(str(exc), code="CONFIG_MISSING") from exc
    return OpenAI(
        api_key=settings.openai_api_key.strip(),
        base_url=settings.openai_base_url.rstrip("/"),
        timeout=60.0,
        max_retries=0,
    )


def embed_texts(
    texts: list[str],
    *,
    client: OpenAI | None = None,
) -> list[list[float]]:
    if not texts:
        return []

    settings = get_settings()
    client = client or _client()
    output: list[list[float]] = []

    for offset in range(0, len(texts), settings.embedding_batch_size):
        batch = texts[offset : offset + settings.embedding_batch_size]
        if any(not text.strip() for text in batch):
            raise EmbeddingError("Không thể embedding text rỗng.")

        response = None
        for attempt in range(3):
            try:
                response = client.embeddings.create(
                    model=settings.embedding_model,
                    input=batch,
                )
                break
            except (APIConnectionError, APITimeoutError, RateLimitError) as exc:
                if attempt == 2:
                    raise EmbeddingError(
                        "Dịch vụ embedding tạm thời không phản hồi. Thử lại sau."
                    ) from exc
                time.sleep(2**attempt)
            except Exception as exc:
                raise EmbeddingError(f"Lỗi embedding: {type(exc).__name__}") from exc

        if response is None:
            raise EmbeddingError("Không nhận được phản hồi embedding.")

        items = sorted(response.data, key=lambda item: item.index)
        vectors = [item.embedding for item in items]
        if len(vectors) != len(batch):
            raise EmbeddingError(
                f"Số vector trả về ({len(vectors)}) không khớp số input ({len(batch)})."
            )
        for vector in vectors:
            if len(vector) != settings.embedding_dim:
                raise EmbeddingError(
                    f"Vector có {len(vector)} chiều, cấu hình EMBEDDING_DIM="
                    f"{settings.embedding_dim}. Kiểm tra EMBEDDING_MODEL và EMBEDDING_DIM."
                )
        output.extend(vectors)

    return output


def embed_query(text: str, *, client: OpenAI | None = None) -> list[float]:
    if not text.strip():
        raise EmbeddingError("Câu hỏi rỗng.")
    return embed_texts([text], client=client)[0]
