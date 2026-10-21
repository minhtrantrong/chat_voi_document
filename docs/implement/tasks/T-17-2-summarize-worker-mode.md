# T-17-2 — Chế độ `summarize` trong worker trả lời (P2)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-17 (P2) — AC-17.1 |
| Sprint | S4 — chỉ khi còn dung lượng |
| Tầng | WRK |
| Ước lượng | 1d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-17-1, T-13-3, T-10-1 |
| Chặn | T-17-4 |

## Bối cảnh

AC-17.1: tóm tắt phản ánh đúng, không thêm nội dung ngoài tài liệu. Vẫn áp dụng citation-first (ADR-007).

## Phạm vi

**Làm:** nhánh `mode == "summarize"` trong `handle_answer`, prompt `prompts/summarize.v1.md`.

## Đặc tả

Lấy ngữ cảnh (thay cho vector search):

```text
chunks = chunks_repo.list_by_document(doc_id, order by chunk_index)          # cùng điều kiện READY/chưa xoá/quyền
n = len(chunks); k = min(12, n)
picked = [chunks[round(i * (n - 1) / max(k - 1, 1))] for i in range(k)]   # rải đều toàn tài liệu
cắt theo MAX_CONTEXT_TOKENS như PromptBuilder
```

`prompts/summarize.v1.md`: giữ đúng các quy tắc của `qa_answer.v1` (chỉ dùng ngữ cảnh, marker `[S#]` bắt buộc) và yêu cầu: "Tóm tắt 5–8 ý chính của tài liệu, mỗi ý một gạch đầu dòng kèm marker nguồn. Không thêm nhận xét."

- Sau khi sinh: chạy `CitationValidator` như bình thường; không có citation → NOT_FOUND với thông điệp "Không thể tóm tắt tài liệu này" (segment do hệ thống tạo).
- `prompt_version` lưu `summarize.v1@hash`.

## Tiêu chí xong

- [ ] Tóm tắt `text.pdf` ra 5–8 gạch đầu dòng, mỗi dòng có chip trích dẫn.

## Test

`tests/integration/qa/test_summarize_mode.py` (FakeLLM).

## Tham chiếu

US-17 · ADR-007 · SADD §10.3
