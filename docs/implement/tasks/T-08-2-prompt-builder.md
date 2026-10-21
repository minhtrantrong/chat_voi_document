# T-08-2 — PromptBuilder: dựng ngữ cảnh có đánh số nguồn và cắt theo ngân sách token

| Thuộc tính | Giá trị |
|---|---|
| Story | US-08 (P0); US-09, US-13b, US-14 |
| Sprint | S3 |
| Tầng | APP |
| Ước lượng | 1d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-08-1, T-09-1 (kiểu `RetrievedChunk`), T-04-2 (Tokenizer), T-11-3 (`detect_lang`) |
| Chặn | T-13-3 |

## Bối cảnh

SADD §5.3.4: context block đánh số `[S1]…`; tối đa 6 chunk lõi + lân cận ≤ 8; `MAX_CONTEXT_TOKENS` 8000; không cấp tool cho LLM (§5.8.5).

## Phạm vi

**Làm:** `app/qa/prompt.py::PromptBuilder`.

## Đặc tả

```python
@dataclass(frozen=True)
class Source:
    label: int                     # 1..n, khớp marker [S{label}]
    chunk: RetrievedChunk          # document_id, file_name, page, chunk_index, anchor, text, score

@dataclass(frozen=True)
class BuiltPrompt:
    messages: list[ChatMessage]    # [{"role":"system",...}, {"role":"user",...}]
    sources: dict[int, Source]
    prompt_tokens_est: int
    lang: Literal["vi", "en"]

class PromptBuilder:
    def build(self, question: str, chunks: list[RetrievedChunk], history: list[Turn],
              *, strict: bool = False) -> BuiltPrompt: ...
```

Quy tắc dựng:
1. `lang = detect_lang(question)`; `not_found_sentence` theo ngôn ngữ (T-11-3).
2. Ngữ cảnh: lặp chunk theo thứ tự (điểm giảm dần), mỗi nguồn:
   ```
   [S{i}] {file_name} — tr. {page}
   {text}
   ```
   Dừng khi tổng token (ước bằng Tokenizer) vượt `MAX_CONTEXT_TOKENS - token(system) - token(question) - token(history) - MAX_OUTPUT_TOKENS`.
3. `history`: tối đa `HISTORY_TURNS` lượt (T-14-1 cung cấp), dạng `Người dùng: …\nTrợ lý: …`; không có thì chuỗi `(không có)`.
4. Làm sạch dữ liệu chèn vào prompt: thay mọi chuỗi `<<<NGU_CANH>>>` / `<<<HET_NGU_CANH>>>` xuất hiện **trong chunk hoặc câu hỏi** bằng `<<<…>>>` đã vô hiệu (chống thoát delimiter — prompt injection).
5. `strict=True` dùng template `qa_answer_strict.v1`.
6. Tham số gọi LLM (truyền riêng, không nằm trong prompt): `temperature=0.1`, `max_tokens=MAX_OUTPUT_TOKENS`, không có `tools`.

## Tiêu chí xong

- [ ] 10 chunk 1.500 token mỗi chunk → chỉ giữ số chunk vừa ngân sách, `sources` khớp marker trong ngữ cảnh.
- [ ] Chunk chứa `<<<HET_NGU_CANH>>>` không làm đóng ngữ cảnh sớm.
- [ ] Câu hỏi tiếng Anh → `lang="en"` và câu not-found tiếng Anh.

## Test

`tests/unit/qa/test_prompt_builder.py`.

## Tham chiếu

SADD §5.3.4 (Prompt và citation), §5.8.5, §10.3 · RISK-09
