#!/usr/bin/env python3
"""Hook chặn Claude Code xóa toàn bộ file/thư mục con của bất kỳ thư mục nào trong repo (Windows)."""

import json
import sys
import re
import os


REPO_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", ".."))


def is_repo_path(path: str) -> bool:
    if not path:
        return False
    try:
        abs_path = os.path.realpath(os.path.abspath(path))
    except Exception:
        return False
    return abs_path == REPO_ROOT or abs_path.startswith(REPO_ROOT + os.sep)


def extract_targets(command: str):
    targets = []
    # Trích xuất chuỗi trong ngoặc kép (đường dẫn có khoảng trắng)
    for m in re.finditer(r'"([^"]*)"', command):
        token = m.group(1).strip()
        if token:
            targets.append(token)
    # Trích xuất đường dẫn không ngoặc (có :, \, /)
    for m in re.finditer(r"[A-Za-z]:[\\/][^\s&|<>]*|[\\/](?:[^\s&|<>]+[\\/]?)+", command):
        token = m.group(0).strip("\"'")
        if token:
            targets.append(token)
    return targets


def is_destructive(command: str) -> bool:
    normalized = re.sub(r"\s+", " ", command.strip()).lower()

    destructive_patterns = [
        # PowerShell Remove-Item / alias rm with -Recurse (-r or -Recurse), including combined flags like -rf, -fr
        r"\b(remove-item|rm)\b.*-\s*[a-z]*r[a-z]*(?:ecurse)?\b",
        r"\b(remove-item|rm)\b.*-force\b.*-\s*[a-z]*r[a-z]*(?:ecurse)?\b",
        r"\b(remove-item|rm)\b.*-\s*[a-z]*r[a-z]*(?:ecurse)?\b.*-force\b",
        # wildcard recursion
        r"\*\s*-\s*r(?:ecurse)?\b",
        # cmd rd / rmdir with /s
        r"\b(rd|rmdir)\b.*(/s|/recurse)\b",
        # cmd del / erase with /s
        r"\b(del|erase)\b.*(/s|/q)\b",
    ]

    return any(re.search(p, normalized) for p in destructive_patterns)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool = payload.get("tool")
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command", "")

    if tool != "Bash" or not isinstance(command, str) or not command.strip():
        return 0

    if not is_destructive(command):
        return 0

    targets = extract_targets(command)

    # Có chỉ rõ đường dẫn mục tiêu
    if targets:
        if any(is_repo_path(t) for t in targets):
            sys.stderr.write(
                "\n[HOOK BLOCKED] Lệnh xóa đệ quy trong repo bị chặn để bảo vệ dữ liệu.\n"
                f"Lệnh: {command}\n"
                "Vui lòng xóa từng file cụ thể thay vì xóa toàn bộ thư mục con trong repo.\n"
            )
            return 1
        # Đường dẫn nằm ngoài repo -> cho phép
        return 0

    # Không chỉ rõ đường dẫn (xóa toàn bộ / thư mục hiện tại / wildcard) -> chặn để an toàn
    normalized_cmd = re.sub(r"\s+", " ", command.strip())
    sys.stderr.write(
        "\n[HOOK BLOCKED] Lệnh xóa đệ quy không chỉ rõ mục tiêu bị chặn.\n"
        f"Lệnh: {normalized_cmd}\n"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
