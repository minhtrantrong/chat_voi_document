"""Mã lỗi và thông điệp tiếng Việt hiển thị cho người dùng."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

ERROR_MESSAGES: dict[str, str] = {
    "PDF_NOT_PDF": "Tệp không phải PDF hợp lệ.",
    "PDF_TOO_LARGE": "Tệp vượt quá dung lượng cho phép.",
    "PDF_TOO_MANY_PAGES": "Tệp có quá nhiều trang.",
    "PDF_ENCRYPTED": "PDF đang được bảo vệ bằng mật khẩu. Hãy bỏ mật khẩu rồi tải lại.",
    "PDF_CORRUPT": "Không đọc được tệp PDF. Tệp có thể bị hỏng.",
    "PDF_NO_TEXT": (
        "PDF không có văn bản để tìm kiếm (có thể là PDF scan). Ứng dụng chưa hỗ trợ OCR."
    ),
    "EMBEDDING_FAILED": (
        "Không tạo được vector cho tài liệu. Kiểm tra cấu hình embedding và thử lại."
    ),
    "QDRANT_UNAVAILABLE": ("Cơ sở dữ liệu vector chưa sẵn sàng. Kiểm tra Qdrant đang chạy."),
    "LLM_FAILED": "Trợ lý tạm thời không trả lời được. Thử lại sau.",
    "CONFIG_MISSING": (
        "Chưa cấu hình API key hoặc mô hình AI. Với Ollama, dùng OPENAI_API_KEY=ollama."
    ),
    "INGEST_FAILED": "Không xử lý được tài liệu. Thử lại hoặc xoá tệp.",
    "INTERNAL": "Đã xảy ra lỗi. Thử lại; nếu vẫn lỗi, kiểm tra log.",
}


def error_code(exc: BaseException) -> str:
    code = getattr(exc, "code", None)
    return code if isinstance(code, str) and code in ERROR_MESSAGES else "INTERNAL"


def error_message(exc: BaseException, file_name: str | None = None) -> str:
    code = error_code(exc)
    # Lỗi PDF có message riêng chứa giới hạn thực tế (MB, số trang) và vẫn thân thiện.
    if code.startswith("PDF_"):
        message = getattr(exc, "message", None)
        base = message if isinstance(message, str) and message.strip() else ERROR_MESSAGES[code]
    else:
        base = ERROR_MESSAGES.get(code, ERROR_MESSAGES["INTERNAL"])
    if file_name:
        return f"{file_name}: {base}"
    return base


def log_error(exc: BaseException, *, context: str) -> None:
    """Log kỹ thuật; không log nội dung tài liệu/câu hỏi/câu trả lời."""
    logger.warning(
        "error context=%s code=%s type=%s",
        context,
        error_code(exc),
        type(exc).__name__,
        exc_info=True,
    )
