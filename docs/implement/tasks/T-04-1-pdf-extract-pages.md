# T-04-1 — `PdfPort.extract_pages`: trích văn bản theo trang và block

| Thuộc tính | Giá trị |
|---|---|
| Story | US-04 — Thấy trạng thái từng tài liệu (P0) |
| Sprint | S2 |
| Tầng | INF |
| Ước lượng | 1d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | F-10, T-01-2 (adapter đã có), T-03-4 |
| Chặn | T-03-2, T-04-2, T-04-4 |

## Bối cảnh

SADD §5.3.3: worker trích text + block/char offset từng trang để chunk giữ được `page`, `anchor`, `char_start/char_end` (cần cho highlight ở US-13d).

## Phạm vi

**Làm:** hàm sandbox `_extract(path, out_json)` và method `extract_pages` của adapter.

## Đặc tả

```python
@dataclass(frozen=True)
class Block:
    char_start: int; char_end: int            # vị trí trong PageText.text

@dataclass(frozen=True)
class PageText:
    page: int                                  # bắt đầu từ 1
    text: str                                  # đã chuẩn hoá, các block nối bằng "\n"
    blocks: tuple[Block, ...]
```

Hàm chạy trong process con:

```text
_extract(path, out_json):
  doc = fitz.open(path)
  if doc.needs_pass: write {"error": "PDF_ENCRYPTED"}; return
  pages = []
  for i, page in enumerate(doc, start=1):
      raw_blocks = page.get_text("blocks", sort=True)        # (x0,y0,x1,y1,text,block_no,block_type)
      parts, blocks, pos = [], [], 0
      for b in raw_blocks:
          if b[6] != 0: continue                              # bỏ block ảnh
          s = normalize(b[4])                                 # NFC, gộp khoảng trắng, nối từ bị gạch nối cuối dòng
          if not s: continue
          if parts: pos += 1                                  # ký tự "\n" nối block
          blocks.append((pos, pos + len(s))); parts.append(s); pos += len(s)
      pages.append({"page": i, "text": "\n".join(parts), "blocks": blocks})
  json.dump({"pages": pages}, open(out_json, "w", encoding="utf-8"))
```

- `normalize`: `unicodedata.normalize("NFC", s)`; thay `\s+` bằng một khoảng trắng; nối `"-\n"` giữa chữ (`hợp-\nđồng` → `hợpđồng` chỉ khi hai phía là chữ cái thường; giữ nguyên gạch nối thật trong từ ghép tiếng Việt viết có gạch).
- Adapter: `run_in_sandbox(_extract, str(path), out_json, timeout_s=300, mem_mb=1536)`; đọc JSON; `SandboxTimeout`/`SandboxCrashed` → `RetryableJobError(EXTRACT_FAILED)`; `error == "PDF_ENCRYPTED"` hoặc mở thất bại → `PermanentJobError(PDF_ENCRYPTED | PDF_CORRUPT)`.
- Bất biến: `page.text[b.char_start:b.char_end]` là nội dung block.

## Tiêu chí xong

- [ ] `text.pdf` trả 3 `PageText`, trang 2 chứa câu "Hạn chót nộp hồ sơ là 30/11/2026."
- [ ] Bất biến offset đúng với mọi block của mọi fixture.
- [ ] PDF 400 trang hoàn tất ≤ 60 s trên máy CI.

## Test

`tests/integration/pdf/test_extract.py` (fixture T-03-4, gồm `hyphen.pdf`, `rotated.pdf`, `long_page.pdf`).

## Tham chiếu

SADD §5.3.3, §5.7.3 · F-10
