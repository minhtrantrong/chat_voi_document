# T-10-2 — CitationAssembler: tạo citation snapshot và quote để highlight

| Thuộc tính | Giá trị |
|---|---|
| Story | US-10 (P0) — AC-10.2; US-13d (quote dùng để highlight) |
| Sprint | S3 |
| Tầng | DOM |
| Ước lượng | 1d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-10-1, T-08-2 (`Source`) |
| Chặn | T-13-3 (finalize) |

## Bối cảnh

DR-04: citation là **snapshot** (tên tệp, trang, anchor, quote) — xoá tài liệu không xoá citation. Quote dùng để highlight đúng đoạn ở khung Nguồn (US-13d).

## Phạm vi

**Làm:** `app/qa/citation.py::CitationAssembler`.

## Đặc tả

```python
@dataclass(frozen=True)
class NewCitation:
    document_id: UUID; chunk_id: UUID; doc_name_snapshot: str; page: int; anchor: str; quote: str

class CitationAssembler:
    def assemble(self, seg: ParsedSegment, sources: Mapping[int, Source]) -> list[NewCitation]: ...
```

Quy tắc:
1. Với mỗi `label` trong `seg.source_labels`, lấy `Source.chunk`; bỏ trùng theo `chunk_id`.
2. `quote` = câu trong `chunk.text` có độ trùng token cao nhất với `seg.text`:
   - tách câu của chunk bằng regex `(?<=[.!?…;])\s+`;
   - điểm = |token(seg) ∩ token(câu)| / |token(câu)| (token = từ viết thường, bỏ dấu câu; không bỏ dấu tiếng Việt);
   - lấy câu điểm cao nhất; hoà thì lấy câu xuất hiện trước; cắt 300 ký tự tại ranh giới từ.
   - Không có câu nào điểm > 0 → 200 ký tự đầu của chunk.
3. `quote` phải là **chuỗi con nguyên văn** của `chunk.text` (để `page.search_for` tìm được) — không chuẩn hoá lại.
4. `doc_name_snapshot = chunk.file_name` tại thời điểm trả lời.

## Tiêu chí xong

- [ ] Quote luôn là chuỗi con của chunk text.
- [ ] Segment nhắc "30/11/2026" chọn đúng câu chứa ngày đó.
- [ ] Hai marker trỏ cùng chunk → 1 citation.

## Test

`tests/unit/qa/test_citation_assembler.py`.

## Tham chiếu

SADD §5.2.4 DR-04, §1.3 (Citation) · US-10, US-13d
