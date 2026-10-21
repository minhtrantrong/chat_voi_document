# T-10-1 — CitationValidator: tách segment, kiểm tra marker `[S#]`

| Thuộc tính | Giá trị |
|---|---|
| Story | US-10 — Thấy tên tài liệu và số trang cho mỗi thông tin (P0) — AC-10.1; US-11 |
| Sprint | S3 |
| Tầng | DOM |
| Ước lượng | 1.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-07-1, T-11-3 (câu not-found theo ngôn ngữ) |
| Chặn | T-10-2, T-13-3 |

## Bối cảnh

ADR-007 citation-first; DR-02: mỗi segment có thông tin từ tài liệu phải có ≥ 1 citation; validator chặn output không citation (SADD §5.3.4 bước 1–4).

## Phạm vi

**Làm:** `app/qa/citation.py::CitationValidator` (thuần, không I/O) + `parse_partial` dùng khi người dùng bấm Dừng.

## Đặc tả

```python
@dataclass(frozen=True)
class ParsedSegment:
    ord: int; text: str; cited: bool; source_labels: tuple[int, ...]

@dataclass(frozen=True)
class Answered:   segments: list[ParsedSegment]
@dataclass(frozen=True)
class NotFound:   pass
@dataclass(frozen=True)
class NoCitation: segments: list[ParsedSegment]
ValidationResult = Answered | NotFound | NoCitation

MARKER = re.compile(r"\[\s*[Ss]\s*(\d{1,3})\s*\]")

class CitationValidator:
    def validate(self, raw: str, sources: Mapping[int, Source], lang: str) -> ValidationResult: ...
    def parse_partial(self, raw: str, sources: Mapping[int, Source]) -> list[ParsedSegment]: ...
```

Thuật toán `validate`:

```text
text = raw.strip()
if text == "": return NotFound
if is_not_found(text, lang) and không có marker hợp lệ: return NotFound
   is_not_found: chuẩn hoá (lowercase, bỏ dấu câu cuối) và so khớp "bắt đầu bằng" câu chuẩn vi/en
blocks = tách theo dòng trống (\n\s*\n); trong mỗi block, mỗi dòng bắt đầu bằng "-", "*", "•", "\d+[.)]" là một segment riêng
for each block → segment:
    labels = [int(m) for m in MARKER.findall(seg)]  → giữ thứ tự, bỏ trùng
    valid = [l for l in labels if l in sources]       # marker không tồn tại trong context bị bỏ
    clean = MARKER.sub("", seg); chuẩn hoá: bỏ khoảng trắng trước . , ; : ! ? ) và gộp nhiều khoảng trắng
    if clean.strip() == "": bỏ segment
    ParsedSegment(ord, clean, cited=bool(valid), source_labels=valid)
if not any(s.cited for s in segments): return NoCitation(segments)
return Answered(segments)
```

- Không chấp nhận các dạng khác `[S1]` như `【S1】`, `(S1)`, `S1` trần (coi như chữ thường, không phải marker).
- Segment không có marker nhưng có nội dung → `cited=False` (ví dụ câu dẫn "Theo tài liệu:"). Đếm "segment thông tin không có nguồn" (`> 40` ký tự và không kết thúc bằng `:`) để eval (T-12-3) theo dõi.
- `parse_partial`: như validate nhưng không bao giờ trả NotFound/NoCitation; dùng cho câu trả lời bị Dừng (giữ phần đã có).

## Tiêu chí xong

- [ ] ≥ 15 kịch bản unit (danh sách ở Implement_plan §17 US-10) đều đúng.
- [ ] Không có `Answered` nào mà mọi segment `cited=False`.

## Test

`tests/unit/qa/test_citation_validator.py`.

## Tham chiếu

ADR-007 · SADD §5.2.4 DR-02/DR-03, §5.3.4 · US-10, US-11 · Implement_plan §17 US-10
