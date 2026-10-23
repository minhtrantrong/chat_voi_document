# S-08 — Chunking theo trang

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01, US-08, US-09 |
| Phase | P1 |
| Tầng | APP |
| Ước lượng | 0,5d |
| Phụ thuộc | S-07 |
| Chặn | S-10, S-11, S-15 |
| Owner gợi ý | Backend |

## 1. Mục tiêu

Chia text của từng trang thành chunk có overlap, **không vượt ranh giới trang**, giữ `char_start/char_end` để trích nguồn. `chunk_index` là duy nhất trong toàn tài liệu (không reset theo trang) để point ID không trùng.

## 2. Phạm vi

**Làm:**

- `app/chunking.py`: `Chunk`, `chunk_pages`.
- Ước lượng token bằng ký tự (`4 ký tự ≈ 1 token`) để đơn giản, không phụ thuộc tokenizer của từng model.
- Cắt ưu tiên cuối câu (`., !, ?, newline`) trong 40% cuối cửa sổ.
- Overlap theo ký tự.
- Bỏ chunk rỗng; không tạo chunk vượt `max_chars`.
- `chunk_index` tuần tự toàn tài liệu.

**Không làm:**

- Chunk xuyên trang.
- Semantic chunking/LLM-based chunking.
- Tối ưu token chính xác theo model embedding (có thể thêm sau).

## 3. File chính

```text
app/chunking.py
tests/test_chunking.py
```

## 4. Đặc tả

### 4.1 DTO

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Chunk:
    page: int          # 1-based
    chunk_index: int   # 0-based, duy nhất toàn tài liệu
    text: str
    char_start: int    # offset trong PageText.text
    char_end: int
```

### 4.2 Hàm

```python
CHARS_PER_TOKEN = 4

def chunk_pages(
    pages: list[PageText],
    *,
    size_tokens: int = 700,
    overlap_tokens: int = 100,
) -> list[Chunk]:
    if size_tokens <= 0:
        raise ValueError("size_tokens phải > 0")
    max_chars = size_tokens * CHARS_PER_TOKEN
    overlap_chars = max(0, overlap_tokens * CHARS_PER_TOKEN)
    if overlap_chars >= max_chars:
        raise ValueError("overlap phải nhỏ hơn size")

    chunks: list[Chunk] = []
    global_index = 0

    for page in pages:
        text = page.text
        n = len(text)
        if n == 0:
            continue

        if n <= max_chars:
            chunks.append(Chunk(page.page, global_index, text, 0, n))
            global_index += 1
            continue

        start = 0
        while start < n:
            hard_end = min(start + max_chars, n)
            end = _find_sentence_break(text, start, hard_end)

            raw = text[start:end]
            left = len(raw) - len(raw.lstrip())
            right = len(raw) - len(raw.rstrip())
            chunk_text = raw.strip()
            chunk_start = start + left
            chunk_end = end - right

            if chunk_text:
                chunks.append(
                    Chunk(page.page, global_index, chunk_text, chunk_start, chunk_end)
                )
                global_index += 1

            if end >= n:
                break

            next_start = max(0, end - overlap_chars)
            if next_start <= start:
                next_start = end
            start = next_start

    return chunks
```

### 4.3 Tìm điểm cắt câu

```python
def _find_sentence_break(text: str, start: int, hard_end: int) -> int:
    if hard_end >= len(text):
        return len(text)
    min_break = start + int((hard_end - start) * 0.6)
    for i in range(hard_end, min_break, -1):
        if text[i - 1] in ".!?\n":
            return i
    return hard_end
```

**Quy tắc:**

- `hard_end` là giới hạn cứng; không bao giờ vượt.
- Nếu tìm thấy dấu câu, cắt sau dấu đó.
- Nếu không, cắt cứng tại `hard_end`.
- Với tiếng Việt, dấu câu có thể theo sau bởi khoảng trắng; cắt sau dấu là ổn.
- Không cắt giữa từ nếu có thể; nếu không có dấu câu, chấp nhận cắt cứng.

### 4.4 Ví dụ

```python
pages = [PageText(page=1, text="A" * 5000)]
chunks = chunk_pages(pages, size_tokens=700, overlap_tokens=100)
# max_chars = 2800, overlap_chars = 400
# chunk 0: [0, 2800)
# chunk 1: [2400, 5200) nhưng nếu trang chỉ 5000 -> [2400, 5000)
```

## 5. Trường hợp biên

- Text ngắn hơn `max_chars` → 1 chunk.
- Trang rỗng → bỏ.
- Text toàn khoảng trắng → `strip()` rỗng; không thêm chunk; vòng lặp vẫn tiến.
- Một "từ" dài > `max_chars` (URL/base64) → cắt cứng, không treo.
- Overlap >= size → raise `ValueError`.
- `size_tokens <= 0` → raise `ValueError`.
- Nhiều trang → `chunk_index` liên tục; không reset.
- Offset: `page.text[chunk.char_start:chunk.char_end] == chunk.text` phải đúng (sau khi strip).
- Unicode tiếng Việt: cắt theo ký tự Python (code point), không cắt byte.

## 6. Tiêu chí xong

- [ ] Không chunk nào vượt `max_chars`.
- [ ] Không chunk nào chứa text của 2 trang.
- [ ] `chunk_index` duy nhất, tăng dần.
- [ ] Offset khớp text.
- [ ] Overlap > 0 khi đủ dài; không lặp vô hạn.
- [ ] Test với 1 trang ngắn, 1 trang dài, nhiều trang, text Unicode.

## 7. Test

`tests/test_chunking.py`:

- `test_short_page_single_chunk`.
- `test_long_page_multiple_chunks`.
- `test_chunk_size_limit`.
- `test_no_cross_page`.
- `test_offsets_match_text`.
- `test_chunk_index_global`.
- `test_overlap_positive`.
- `test_sentence_break_preferred`.
- `test_long_word_no_infinite_loop`.
- `test_overlap_ge_size_raises`.

## 8. Tham chiếu

- Kế hoạch §5.2, §7.2.
- S-07, S-10, S-15.
