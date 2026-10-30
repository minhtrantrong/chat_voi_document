#!/usr/bin/env python3
"""Hook chặn Claude Code thực thi lệnh rm -rf trong repo."""

import json
import sys
import re


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        # Không parse được stdin -> không can thiệp
        return 0

    tool = payload.get("tool")
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command", "")

    if tool != "Bash" or not isinstance(command, str):
        return 0

    # Chuẩn hoá lệnh: xóa khoảng trắng thừa, thay nhiều khoảng trắng bằng 1
    normalized = re.sub(r"\s+", " ", command.strip()).lower()

    # Các mẫu rm -rf nguy hiểm (bao gồm rm -rf, rm -r -f, rm -fr, ...)
    dangerous_patterns = [
        r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*|-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*|-[rf][a-zA-Z]*-[rf])\b",
        r"\brm\s+-\s*r\s+-\s*f\b",
        r"\brm\s+-\s*f\s+-\s*r\b",
        r"\brm\s+-rf\b",
        r"\brm\s+-fr\b",
    ]

    if any(re.search(p, normalized) for p in dangerous_patterns):
        sys.stderr.write(
            "\n[HOOK BLOCKED] Lệnh 'rm -rf' bị chặn để bảo vệ kho lưu trữ.\n"
            "Vui lòng xóa file/thư mục cụ thể thay vì dùng rm -rf.\n"
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
