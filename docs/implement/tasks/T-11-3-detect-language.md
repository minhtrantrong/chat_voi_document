# T-11-3 — Nhận diện ngôn ngữ câu hỏi (vi/en)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-11 (P0); US-13b (P0) |
| Sprint | S3 |
| Tầng | DOM |
| Ước lượng | 0.25d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | — |
| Chặn | T-08-2, T-10-1, T-11-1, T-13b-4 |

## Bối cảnh

DR-07: câu trả lời cùng ngôn ngữ câu hỏi. Câu NOT_FOUND do hệ thống tạo (không qua LLM) cũng phải đúng ngôn ngữ. ASM-003: chủ yếu tiếng Việt/tiếng Anh.

## Phạm vi

**Làm:** `app/qa/lang.py::detect_lang(text) -> Literal["vi", "en"]` và `not_found_text(lang)`.

## Đặc tả

```python
VI_CHARS = set("ăâđêôơưàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ")
VI_WORDS = {"là", "của", "và", "không", "có", "được", "những", "cho", "này", "gì", "nào", "bao", "khi"}

def detect_lang(text: str) -> Literal["vi", "en"]:
    s = unicodedata.normalize("NFC", text.lower())
    if any(ch in VI_CHARS for ch in s): return "vi"
    words = re.findall(r"[a-z]+", s)
    if words and sum(w in VI_WORDS for w in words) / len(words) >= 0.2: return "vi"    # tiếng Việt gõ không dấu
    return "en" if words else "vi"
```

- Mặc định `vi` khi không xác định (ngôn ngữ vận hành chính).
- Không thêm thư viện nhận diện ngôn ngữ cho MVP.

## Tiêu chí xong

- [ ] "Hạn chót nộp hồ sơ?" → vi; "han chot nop ho so la ngay nao" → vi; "What is the deadline?" → en; "12/11?" → vi.

## Test

`tests/unit/qa/test_lang.py` (≥ 20 ví dụ).

## Tham chiếu

SADD §5.2.4 DR-07 · US-11, US-13b
