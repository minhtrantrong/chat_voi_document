# T-10-3 — Ẩn marker `[S#]` trong lúc stream

| Thuộc tính | Giá trị |
|---|---|
| Story | US-10 (P0) |
| Sprint | S3 |
| Tầng | DOM |
| Ước lượng | 0.25d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-10-1 (regex `MARKER`) |
| Chặn | T-13-6 |

## Bối cảnh

SADD §5.3.4: marker `[S#]` được ẩn tạm trong lúc stream; chip citation chỉ hiển thị sau khi có segment/citation chính thức (Blueprint: chip chỉ hiện khi đoạn hoàn chỉnh). Token đến theo từng mảnh nên marker có thể bị cắt dở ở cuối buffer (`[S`, `[S1`).

## Phạm vi

**Làm:** hàm thuần `strip_markers_for_stream(buf: str) -> str` trong `app/qa/citation.py`.

## Đặc tả

```python
PARTIAL_TAIL = re.compile(r"\[\s*[Ss]?\s*\d{0,3}\s*$")

def strip_markers_for_stream(buf: str) -> str:
    out = MARKER.sub("", buf)
    out = PARTIAL_TAIL.sub("", out)            # bỏ marker dở dang ở cuối
    return re.sub(r"[ \t]+([.,;:!?])", r"\1", out)
```

- Chỉ bỏ dấu `[` ở cuối nếu nó có thể là đầu marker; `[` giữa câu (ví dụ "[ghi chú]") giữ nguyên vì regex chỉ khớp ở cuối chuỗi.

## Tiêu chí xong

- [ ] `"Hạn chót là 30/11 [S1]. Phụ lục [S"` → `"Hạn chót là 30/11. Phụ lục "`.
- [ ] `"Xem [ghi chú] bên dưới"` giữ nguyên.

## Test

`tests/unit/qa/test_strip_markers.py` (bảng ví dụ, gồm marker bị cắt ở mọi vị trí ký tự).

## Tham chiếu

SADD §5.3.4 · Blueprint ADR-UX-03
