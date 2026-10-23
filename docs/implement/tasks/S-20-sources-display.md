# S-20 — Hiển thị nguồn trích dẫn

| Thuộc tính | Giá trị |
|---|---|
| Story | US-08, US-09 |
| Phase | P2 |
| Tầng | UI |
| Ước lượng | 0,25d |
| Phụ thuộc | S-18 |
| Chặn | S-25 |
| Owner gợi ý | Full-stack |

## 1. Mục tiêu

Dưới mỗi câu trả lời, hiển thị danh sách nguồn đã dùng: tên tệp, số trang, nhãn `[S#]`, đoạn trích ngắn và điểm tương đồng. Giúp người dùng kiểm chứng câu trả lời mà không cần mở PDF.

## 2. Phạm vi

**Làm:**

- `render_sources(sources)` trong `app/ui.py`.
- Nhận `list[Source]` hoặc `list[dict]` (khi đọc từ session).
- Dedupe theo `(file_name, page, chunk_index)`.
- Sắp theo thứ tự nhãn `S1..Sn` (hoặc score giảm dần nếu không có nhãn).
- `st.expander("Nguồn (N)")`, mặc định đóng.
- Mỗi nguồn: `**[S1] hop-dong.pdf — trang 7**`, snippet 200–300 ký tự, score.
- Không render HTML/unsafe.

**Không làm:**

- Mở/scroll PDF đến trang.
- Highlight đoạn trong PDF.
- Link tải file.
- Citation inline tự động (LLM tự ghi `[S#]`; UI chỉ hiển thị danh sách).

## 3. File chính

```text
app/ui.py
tests/test_sources.py
```

## 4. Đặc tả

### 4.1 Chuẩn hoá

```python
from dataclasses import asdict, is_dataclass

def _as_dict(source) -> dict:
    if isinstance(source, dict):
        return source
    if is_dataclass(source):
        return asdict(source)
    return {
        "label": getattr(source, "label", ""),
        "file_name": getattr(source, "file_name", "tài liệu"),
        "page": getattr(source, "page", 0),
        "chunk_index": getattr(source, "chunk_index", -1),
        "text": getattr(source, "text", ""),
        "score": getattr(source, "score", 0.0),
    }
```

### 4.2 Dedupe

```python
def dedupe_sources(sources: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for s in sources:
        key = (s.get("file_name"), s.get("page"), s.get("chunk_index"))
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out
```

### 4.3 Render

```python
import streamlit as st

def render_sources(sources: list) -> None:
    items = dedupe_sources([_as_dict(s) for s in sources])
    if not items:
        return
    with st.expander(f"Nguồn ({len(items)})", expanded=False):
        for s in items:
            label = s.get("label") or "?"
            file_name = s.get("file_name") or "tài liệu"
            page = s.get("page") or "?"
            score = s.get("score")
            score_text = f" · điểm {score:.2f}" if isinstance(score, (int, float)) else ""
            st.markdown(f"**[{label}] {file_name} — trang {page}**{score_text}")
            text = (s.get("text") or "").strip()
            if text:
                snippet = text[:300] + ("…" if len(text) > 300 else "")
                st.caption(snippet)
```

**An toàn:** `st.markdown` với `file_name` có thể chứa `*`, `[`, `]`; escape:

```python
def _md_escape(text: str) -> str:
    for ch in "\\`*_{}[]()#+-.!|":
        text = text.replace(ch, "\\" + ch)
    return text
```

Hoặc dùng `st.write(f"[{label}] {file_name} — trang {page}")` (plain text) rồi `st.caption(snippet)`. Đơn giản và an toàn hơn. Chọn `st.write`.

### 4.4 Lưu vào session

S-18 lưu:

```python
sources=[_source_to_dict(s) for s in final_sources]
```

`_source_to_dict`:

```python
def _source_to_dict(s) -> dict:
    return {
        "label": s.label,
        "file_name": s.file_name,
        "page": s.page,
        "chunk_index": s.chunk_index,
        "text": s.text,
        "score": s.score,
    }
```

## 5. Trường hợp biên

- `sources=[]` → không render gì.
- Source thiếu `label` → hiển thị `[?]`.
- Source thiếu `page` → `trang ?`.
- `score` None/không phải số → bỏ phần điểm.
- Text rỗng → chỉ hiện header.
- Text rất dài → cắt 300 ký tự + `…`.
- Trùng nguồn do nhiều hit cùng chunk → dedupe.
- Nhiều nguồn (>10) → hiển thị tất cả trong expander; có thể cuộn.
- File name chứa markdown/HTML → dùng `st.write` plain text.
- Nguồn từ tài liệu đã xoá → S-12 clear chat; nếu còn, vẫn hiển thị như ảnh chụp lịch sử; ghi chú.
- Thứ tự: giữ thứ tự `sources` (đã theo `[S1]..`); nếu muốn score giảm dần, sort trước khi render.

## 6. Tiêu chí xong

- [ ] Hiển thị expander "Nguồn (N)".
- [ ] Mỗi nguồn có nhãn, tên file, trang, snippet.
- [ ] Dedupe đúng.
- [ ] Không render HTML/unsafe.
- [ ] Không crash với dict/None/thiếu field.
- [ ] Nguồn nhiều tài liệu hiển thị đủ.

## 7. Test

`tests/test_sources.py`:

- `test_dedupe_same_chunk`.
- `test_render_empty_noop` (gọi hàm, không exception).
- `test_as_dict_from_dataclass`.
- `test_as_dict_from_dict`.
- `test_missing_fields_defaults`.
- `test_snippet_truncated`.
- `test_no_html_escape` (kiểm tra dùng `st.write`/caption, không `unsafe_allow_html`).

## 8. Tham chiếu

- Kế hoạch §8.
- S-15, S-18, S-25.
