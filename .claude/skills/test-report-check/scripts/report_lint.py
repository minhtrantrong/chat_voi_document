"""Kiểm tra và trích xuất dữ liệu từ test_reports/<ID>/report.md.

Dùng chung cho skill test-report-check (kiểm tra) và test-report-summary (tổng hợp).

    python report_lint.py ST-01 ST-02          # kiểm tra vài case, in dạng đọc được
    python report_lint.py --all                 # mọi thư mục trong test_reports/
    python report_lint.py --all --json          # JSON cho skill summary

Exit code: 0 nếu không có lỗi mức ERROR, 1 nếu có.
Chỉ dùng thư viện chuẩn; chạy từ thư mục gốc repo (hoặc truyền --root).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

CASE_ID_RE = re.compile(r"^(ST|UI|SEC|PF|EV|REG|UAT)-\d{2}$")
V_CODE_RE = re.compile(r"V(\d{2})([a-z]?)")
V_RANGE_RE = re.compile(r"V(\d{2})\s*[–-]\s*V(\d{2})")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
BARE_PATH_RE = re.compile(r"(?<![\w/(\[`])((?:screenshots|test-data)/[^\s|)\]`,]*[^\s|)\]`,.])")
BUG_ID_RE = re.compile(r"^(BUG|OBS)-[A-Z]+\d{2}-\d{2}")
SEVERITY_RE = re.compile(r"\bS[1-4]\b")
VIDEO_NAMES = ("video.webm", "video.mp4")


@dataclass
class Issue:
    level: str  # ERROR | WARN
    message: str


@dataclass
class Bug:
    bug_id: str
    description: str
    severity: str
    evidence: str


@dataclass
class ReportData:
    case_id: str
    report_dir: str
    testcase_file: str | None = None
    title: str = ""
    priority: str = ""
    cycle: str = ""
    group: str = ""
    tester: str = ""
    date: str = ""
    overall: str = "MISSING"  # PASS | FAIL | BLOCKED | MISSING | UNKNOWN
    overall_text: str = ""
    steps_total: int = 0
    steps_pass: int = 0
    steps_fail: int = 0
    steps_other: int = 0
    expected_v_codes: list[str] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)
    video: str | None = None
    bugs: list[Bug] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)

    def error(self, msg: str) -> None:
        self.issues.append(Issue("ERROR", msg))

    def warn(self, msg: str) -> None:
        self.issues.append(Issue("WARN", msg))


# ---------- markdown helpers ----------

def split_row(line: str) -> list[str]:
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def iter_tables(text: str):
    """Yield (header_cells, rows) cho mọi bảng markdown ngoài code fence."""
    lines = text.splitlines()
    in_fence = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            i += 1
            continue
        if (
            not in_fence
            and line.lstrip().startswith("|")
            and i + 1 < len(lines)
            and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1])
        ):
            header = split_row(line)
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append(split_row(lines[j]))
                j += 1
            yield header, rows
            i = j
            continue
        i += 1


def strip_md(s: str) -> str:
    return re.sub(r"[*_`]", "", s).strip()


def expand_v_codes(cell: str) -> list[str]:
    codes: list[str] = []
    for a, b in V_RANGE_RE.findall(cell):
        codes += [f"V{n:02d}" for n in range(int(a), int(b) + 1)]
    cell = V_RANGE_RE.sub("", cell)
    codes += [f"V{n}{suffix}" for n, suffix in V_CODE_RE.findall(cell)]
    return codes


def verdict_of(cell: str) -> str:
    c = strip_md(cell).upper()
    if c.startswith("PASS") or c.startswith("ĐÚNG"):
        return "PASS"
    if c.startswith("FAIL") or c.startswith("SAI"):
        return "FAIL"
    if c.startswith("BLOCKED") or c.startswith("N/A") or c.startswith("SKIP"):
        return "OTHER"
    return "UNKNOWN"


# ---------- test case spec ----------

def find_testcase(root: Path, case_id: str) -> Path | None:
    matches = sorted((root / "docs/testing/testcases").glob(f"{case_id}-*.md"))
    return matches[0] if matches else None


def parse_testcase(path: Path, data: ReportData) -> None:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^#\s+\S+\s+[—-]\s+(.+)$", text, re.M)
    if m:
        data.title = m.group(1).strip()
    for header, rows in iter_tables(text):
        if header[:2] == ["Mục", "Giá trị"]:
            meta = {strip_md(r[0]): strip_md(r[1]) for r in rows if len(r) >= 2}
            data.priority = meta.get("Ưu tiên", "")
            data.cycle = meta.get("Chu kỳ", "")
            data.group = meta.get("Nhóm", "")
        if "Bằng chứng" in header:
            idx = header.index("Bằng chứng")
            for r in rows:
                if idx < len(r):
                    data.expected_v_codes += expand_v_codes(r[idx])


# ---------- report ----------

def parse_report(report_dir: Path, data: ReportData) -> None:
    report = report_dir / "report.md"
    if not report.exists():
        data.error("Thiếu report.md")
        return
    text = report.read_text(encoding="utf-8")

    m = re.search(r"\*\*Kết quả tổng:\*\*\s*(.+)", text)
    if not m:
        data.error("Không thấy dòng '**Kết quả tổng:**'")
        data.overall = "UNKNOWN"
    else:
        data.overall_text = m.group(1).strip()
        head = strip_md(data.overall_text).upper()
        if "PASS / FAIL" in head or head.startswith("…"):
            data.overall = "UNKNOWN"
            data.error("Kết quả tổng chưa điền (còn placeholder)")
        elif head.startswith("PASS"):
            data.overall = "PASS"
        elif head.startswith("FAIL"):
            data.overall = "FAIL"
        elif head.startswith("BLOCKED"):
            data.overall = "BLOCKED"
        else:
            data.overall = "UNKNOWN"
            data.error(f"Kết quả tổng không bắt đầu bằng PASS/FAIL/BLOCKED: '{data.overall_text[:40]}'")

    m = re.search(r"\*\*Agent / người test:\*\*\s*(.+?)\s*·\s*\*\*Ngày:\*\*\s*(.+)", text)
    if m:
        data.tester, data.date = m.group(1).strip(), m.group(2).strip()
    else:
        data.warn("Thiếu dòng 'Agent / người test · Ngày'")
    if not re.search(r"\*\*Môi trường:\*\*\s*\S", text) or "OS: …" in text:
        data.warn("Phần Môi trường thiếu hoặc còn placeholder")

    # Bảng kết quả từng bước: cột đầu '#', có cột Kết quả hoặc Đúng/Sai
    step_table = None
    bug_table = None
    for header, rows in iter_tables(text):
        if header and header[0] == "#" and ("Kết quả" in header or "Đúng/Sai" in header):
            step_table = step_table or (header, rows)
        if header and header[0] == "Bug ID":
            bug_table = (header, rows)

    if not step_table:
        data.error("Không thấy bảng kết quả từng bước (cột '#' + 'Kết quả'/'Đúng/Sai')")
    else:
        header, rows = step_table
        col = header.index("Kết quả") if "Kết quả" in header else header.index("Đúng/Sai")
        for r in rows:
            if not r or not r[0] or r[0] == "…":
                continue
            data.steps_total += 1
            v = verdict_of(r[col]) if col < len(r) else "UNKNOWN"
            if v == "PASS":
                data.steps_pass += 1
            elif v == "FAIL":
                data.steps_fail += 1
            else:
                data.steps_other += 1
                if v == "UNKNOWN":
                    data.warn(f"Bước {r[0]}: không đọc được kết quả '{r[col] if col < len(r) else ''}'")
        if data.steps_total == 0:
            data.error("Bảng kết quả từng bước rỗng")

    # Tính nhất quán verdict (EV dùng ngưỡng nên chỉ cảnh báo)
    is_eval = data.case_id.startswith("EV-")
    if data.overall == "PASS" and data.steps_fail and not is_eval:
        data.error(f"Kết quả tổng PASS nhưng có {data.steps_fail} bước FAIL")
    if data.overall == "FAIL" and data.steps_total and not data.steps_fail and not data.bugs and not is_eval:
        data.warn("Kết quả tổng FAIL nhưng không bước nào FAIL — cần giải thích lý do")

    if bug_table:
        header, rows = bug_table
        for r in rows:
            if not r or not r[0] or r[0] == "…":
                continue
            bug_id = strip_md(r[0])
            desc = r[1] if len(r) > 1 else ""
            sev_cell = r[2] if len(r) > 2 else ""
            sev = SEVERITY_RE.search(sev_cell)
            ev = r[3] if len(r) > 3 else ""
            data.bugs.append(Bug(bug_id, desc, sev.group(0) if sev else "", ev))
            if not BUG_ID_RE.match(bug_id):
                data.warn(f"Bug ID '{bug_id}' không theo dạng BUG-<CASE>-NN / OBS-<CASE>-NN")
            if not sev:
                data.error(f"Bug {bug_id}: thiếu mức S1–S4")
            if not ev.strip():
                data.warn(f"Bug {bug_id}: thiếu ảnh bằng chứng")
    else:
        data.warn("Không thấy bảng bug (nên giữ bảng rỗng nếu không có bug)")

    if data.overall == "FAIL" and data.steps_fail and not data.bugs:
        data.warn("Có bước FAIL nhưng bảng bug trống")

    # Link tương đối phải trỏ tới file có thật
    targets = set(LINK_RE.findall(text)) | set(BARE_PATH_RE.findall(text))
    for t in sorted(targets):
        if t.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = (report_dir / t.split("#")[0]).resolve()
        try:
            target.relative_to(report_dir.resolve())
            inside = True
        except ValueError:
            inside = False
        if inside and not target.exists():
            data.error(f"Link hỏng: {t}")

    if "**Video:**" not in text:
        data.warn("Report không ghi dòng '**Video:**'")


def check_artifacts(report_dir: Path, data: ReportData) -> None:
    for name in VIDEO_NAMES:
        if (report_dir / name).exists():
            data.video = name
            break
    if not data.video:
        data.error("Thiếu video.webm / video.mp4")

    shots_dir = report_dir / "screenshots"
    if shots_dir.is_dir():
        data.screenshots = sorted(p.name for p in shots_dir.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"})
    else:
        data.error("Thiếu thư mục screenshots/")

    have = {m.group(0) for s in data.screenshots if (m := re.match(r"V\d{2}[a-z]?", s))}
    for code in dict.fromkeys(data.expected_v_codes):
        if code not in have:
            data.error(f"Thiếu ảnh cho {code} (yêu cầu trong test case)")
    for s in data.screenshots:
        if not re.match(r"V\d{2}[a-z]?-[\w-]+\.(png|jpe?g)$", s, re.I):
            data.warn(f"Tên ảnh không theo mẫu Vxx-mo-ta.png: {s}")


def lint_case(root: Path, case_id: str) -> ReportData:
    report_dir = root / "test_reports" / case_id
    data = ReportData(case_id=case_id, report_dir=str(report_dir.relative_to(root)))
    tc = find_testcase(root, case_id)
    if tc:
        data.testcase_file = str(tc.relative_to(root)).replace("\\", "/")
        parse_testcase(tc, data)
    else:
        data.warn("Không tìm thấy file test case trong docs/testing/testcases/")
    if not report_dir.is_dir():
        data.overall = "MISSING"
        data.error("Chưa có thư mục test_reports/" + case_id)
        return data
    parse_report(report_dir, data)
    check_artifacts(report_dir, data)
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cases", nargs="*", help="Mã test case, vd ST-01")
    ap.add_argument("--all", action="store_true", help="Mọi thư mục case trong test_reports/")
    ap.add_argument("--catalog", action="store_true", help="Cùng --all: gồm cả case chưa chạy (từ docs/testing/testcases)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", default=".", help="Thư mục gốc repo")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    cases = list(args.cases)
    if args.all:
        found = {p.name for p in (root / "test_reports").glob("*") if p.is_dir() and CASE_ID_RE.match(p.name)}
        if args.catalog:
            found |= {
                m.group(1)
                for p in (root / "docs/testing/testcases").glob("*.md")
                if (m := re.match(r"^((?:ST|UI|SEC|PF|EV)-\d{2})-", p.name))
            }
        cases += sorted(found)
    if not cases:
        ap.error("Cần mã test case hoặc --all")

    results = [lint_case(root, c.upper()) for c in dict.fromkeys(cases)]

    if args.json:
        sys.stdout.reconfigure(encoding="utf-8")
        print(json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2))
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        for r in results:
            errs = sum(i.level == "ERROR" for i in r.issues)
            warns = len(r.issues) - errs
            print(
                f"== {r.case_id} [{r.overall}] bước {r.steps_pass}/{r.steps_total} PASS · "
                f"{len(r.bugs)} bug · {errs} lỗi, {warns} cảnh báo"
            )
            for i in r.issues:
                print(f"   {i.level:5} {i.message}")
    return 1 if any(i.level == "ERROR" for r in results for i in r.issues) else 0


if __name__ == "__main__":
    sys.exit(main())
