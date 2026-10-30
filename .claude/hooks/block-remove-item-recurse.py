#!/usr/bin/env python3
"""Hook chặn Claude Code xóa đệ quy file/thư mục con trong repo (Windows, Bash + PowerShell).

Chặn bằng exit code 2 (Claude Code chỉ coi exit 2 là "block"; exit 1 chỉ là lỗi không chặn).
"""

import json
import os
import re
import shlex
import sys

REPO_ROOT = os.path.normcase(os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..")))

SHELL_TOOLS = {"Bash", "PowerShell"}
DELETE_VERBS = {"remove-item", "rm", "ri", "del", "erase", "rd", "rmdir"}
CMD_VERBS = {"del", "erase", "rd", "rmdir"}


def split_segments(command: str):
    """Tách lệnh ghép (; && || |) để mỗi đoạn được kiểm tra riêng."""
    return [s.strip() for s in re.split(r"&&|\|\||[;|\n]", command) if s.strip()]


def tokenize(segment: str):
    try:
        tokens = shlex.split(segment, posix=False)  # posix=False giữ nguyên dấu \ của Windows
    except ValueError:
        tokens = segment.split()
    return [t.strip("\"'") for t in tokens]


def is_recursive_flag(token: str, verb: str) -> bool:
    t = token.lower()
    if verb in CMD_VERBS:
        return t in ("/s", "/q")
    if t in ("--recursive", "--force"):
        return t == "--recursive"
    if re.fullmatch(r"-[a-z]*r[a-z]*", t) and len(t) <= 5:  # -r, -R, -rf, -fr, -rfv
        return True
    # PowerShell: -Recurse hoặc tiền tố viết tắt (-r, -re, -rec, ...)
    return t.startswith("-") and len(t) > 1 and "recurse".startswith(t[1:])


def is_in_repo(path: str, cwd: str) -> bool:
    if not path:
        return False
    path = os.path.expandvars(os.path.expanduser(path))
    if not os.path.isabs(path):
        path = os.path.join(cwd, path)
    try:
        abs_path = os.path.normcase(os.path.realpath(os.path.abspath(path)))
    except Exception:
        return False
    return abs_path == REPO_ROOT or abs_path.startswith(REPO_ROOT + os.sep)


def check_segment(segment: str, cwd: str):
    """Trả về (bị_chặn, lý_do)."""
    tokens = tokenize(segment)
    verb_idx = next((i for i, t in enumerate(tokens) if t.lower() in DELETE_VERBS), None)
    if verb_idx is None:
        return False, ""
    verb = tokens[verb_idx].lower()
    args = tokens[verb_idx + 1 :]

    if not any(is_recursive_flag(a, verb) for a in args):
        return False, ""

    flag_like = (lambda a: re.fullmatch(r"/[a-zA-Z]", a)) if verb in CMD_VERBS else (lambda a: False)
    paths = [a for a in args if not a.startswith("-") and not flag_like(a)]

    if not paths:
        return True, "Lệnh xóa đệ quy không chỉ rõ mục tiêu."
    if any(is_in_repo(p, cwd) for p in paths):
        return True, "Lệnh xóa đệ quy trong repo bị chặn để bảo vệ dữ liệu."
    return False, ""


def main() -> int:
    sys.stderr.reconfigure(encoding="utf-8")  # tiếng Việt không bị lỗi mã hóa trên console Windows
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if payload.get("tool_name") not in SHELL_TOOLS:
        return 0
    command = (payload.get("tool_input") or {}).get("command", "")
    if not isinstance(command, str) or not command.strip():
        return 0

    cwd = payload.get("cwd") or os.getcwd()
    for segment in split_segments(command):
        blocked, reason = check_segment(segment, cwd)
        if blocked:
            sys.stderr.write(
                f"\n[HOOK BLOCKED] {reason}\nLệnh: {command}\n"
                "Vui lòng xóa từng file cụ thể thay vì xóa toàn bộ thư mục con trong repo.\n"
            )
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
