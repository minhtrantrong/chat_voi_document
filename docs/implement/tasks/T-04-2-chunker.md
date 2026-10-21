# T-04-2 — Chunker: chia văn bản theo token, giữ trang và vị trí

| Thuộc tính | Giá trị |
|---|---|
| Story | US-04 (P0); ảnh hưởng chất lượng US-08…US-12 |
| Sprint | S2 |
| Tầng | DOM |
| Ước lượng | 1.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-04-1 (kiểu `PageText`), F-01 |
| Chặn | T-04-4 |

## Bối cảnh

SADD §5.3.3: chunk 700 token, overlap 15% (105), ưu tiên ranh giới đoạn, **không vượt trang**; `anchor = "p{page}#c{chunkIndex}"`; lưu `char_start`, `char_end`.

## Phạm vi

**Làm:** `app/ingestion/chunker.py` (thuần Python, không I/O). Tokenizer truyền vào qua Protocol để domain không phụ thuộc trực tiếp `tiktoken`.

## Đặc tả

```python
class Tokenizer(Protocol):
    def count(self, text: str) -> int: ...
    def tail(self, text: str, n_tokens: int) -> str: ...      # n token cuối, cắt tại ranh giới từ

@dataclass(frozen=True)
class Chunk:
    page: int; chunk_index: int; text: str; token_count: int
    char_start: int; char_end: int; anchor: str

class Chunker:
    def __init__(self, tokenizer: Tokenizer, size: int = 700, overlap: int = 105) -> None: ...
    def chunk(self, pages: Sequence[PageText]) -> list[Chunk]: ...
```

Thuật toán (cho mỗi trang, `chunk_index` đếm liên tục cho cả tài liệu):

```text
units = []                                    # (start, end) trong page.text
for block in page.blocks:
    if tok(block) <= size: units.append(block)
    else: tách block theo câu (regex (?<=[.!?…])\s+); câu > size thì cắt theo cửa sổ token
cur_start = None; cur_end = None
for u in units:
    if cur_start is None: cur_start, cur_end = u; continue
    if tok(page.text[cur_start:u.end]) > size:
        emit(cur_start, cur_end)
        ov_start = vị trí bắt đầu của tail(page.text[cur_start:cur_end], overlap)
        cur_start = ov_start if ov_start < u.start else u.start; cur_end = u.end
    else: cur_end = u.end
emit cuối trang
emit(s, e): text = page.text[s:e]; Chunk(page, idx, text, tok(text), s, e, f"p{page}#c{idx}"); idx += 1
```

Cài đặt tokenizer ở `app/infrastructure/embedding/tokenizer.py`: `TiktokenTokenizer("cl100k_base")` (xấp xỉ; ghi chú trong code rằng provider có thể đếm khác ±10%).

Tham số lấy từ env `CHUNK_SIZE_TOKENS`, `CHUNK_OVERLAP_TOKENS` (SADD §10.2).

## Tiêu chí xong

- [ ] Mọi chunk `token_count <= size` (cho phép vượt khi một "từ" duy nhất dài hơn size — trường hợp cực hiếm, log warn).
- [ ] Không chunk nào chứa văn bản của hai trang.
- [ ] `page.text[c.char_start:c.char_end] == c.text` cho mọi chunk.
- [ ] Overlap giữa hai chunk liên tiếp cùng trang nằm trong 105 ± 15 token.
- [ ] Trang rỗng không sinh chunk; `chunk_index` liên tục 0..n-1.

## Test

`tests/unit/ingestion/test_chunker.py` (tokenizer giả đếm theo từ để tất định + một test với tiktoken thật), property-based bằng `hypothesis` cho bất biến offset.

## Tham chiếu

SADD §5.3.3, §10.2 · RISK-02, IR-03
