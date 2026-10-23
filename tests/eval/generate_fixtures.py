"""Tạo 3 PDF mẫu nhỏ cho eval/demo.

Chạy:
    .venv/bin/python tests/eval/generate_fixtures.py

Nội dung dùng tiếng Việt có dấu. Nếu máy có DejaVu Sans thì nhúng font để
PyMuPDF trích xuất đúng dấu; nếu không, dùng font mặc định (một số dấu có thể
hiển thị sai nhưng số/ngày tháng vẫn giữ nguyên).
"""

from __future__ import annotations

import unicodedata
from pathlib import Path

import pymupdf

FIXTURES = Path(__file__).parent / "fixtures"
FONT_CANDIDATES = (
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"),
    Path("/Library/Fonts/Arial Unicode.ttf"),
)


def _font() -> tuple[str, str | None]:
    for path in FONT_CANDIDATES:
        if path.exists():
            return "F0", str(path)
    return "helv", None


def _ascii(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def _write_pdf(path: Path, title: str, lines: list[str]) -> None:
    font_name, font_file = _font()
    if font_file is None:
        # Font mặc định chỉ hỗ trợ Latin-1; dùng bản không dấu để script vẫn chạy.
        title = _ascii(title)
        lines = [_ascii(line) for line in lines]
    doc = pymupdf.open()
    page = doc.new_page()
    if font_file:
        page.insert_font(fontname=font_name, fontfile=font_file)
    page.insert_text((72, 72), title, fontsize=16, fontname=font_name)
    y = 110
    for line in lines:
        page.insert_text((72, y), line, fontsize=11, fontname=font_name)
        y += 20
    doc.subset_fonts()
    doc.save(path, garbage=4, deflate=True)
    doc.close()


def generate() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)

    _write_pdf(
        FIXTURES / "hop-dong.pdf",
        "HỢP ĐỒNG",
        [
            "Bên A: Công ty Minh Phát",
            "Bên B: Công ty Đông Á",
            "Giá trị hợp đồng: 1.200.000.000 VND",
            "Hạn chót nộp hồ sơ: 30/11/2026",
            "Thời hạn hợp đồng: 12 tháng từ 01/12/2026",
            "Bảo hành: 24 tháng",
        ],
    )
    _write_pdf(
        FIXTURES / "bao-gia.pdf",
        "BÁO GIÁ",
        [
            "Gói A: 450.000.000 VND",
            "Gói B: 620.000.000 VND",
            "Thời gian giao hàng gói A: 45 ngày",
            "Thời gian giao hàng gói B: 60 ngày",
            "Hiệu lực báo giá: 30 ngày",
        ],
    )
    _write_pdf(
        FIXTURES / "quy-dinh.pdf",
        "QUY ĐỊNH",
        [
            "Mật khẩu tối thiểu 12 ký tự",
            "Bắt buộc xác thực hai yếu tố",
            "Thời gian lưu log: 90 ngày",
            "Sao lưu dữ liệu: hàng ngày, giữ 30 bản",
            "Thời gian khôi phục mục tiêu (RTO): 4 giờ",
        ],
    )


if __name__ == "__main__":
    generate()
    print(f"created fixtures in {FIXTURES}")
