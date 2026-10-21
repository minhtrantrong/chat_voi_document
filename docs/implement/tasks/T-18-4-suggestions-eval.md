# T-18-4 — Kiểm chứng gợi ý trả lời được có trích dẫn (P2)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-18 (P2) — AC-18.1 |
| Sprint | S4–S5 — chỉ khi tính năng được làm |
| Tầng | TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-18-2, T-12-2 |
| Chặn | Quyết định bật cờ `FEATURE_SUGGESTIONS` |

## Bối cảnh

AC-18.1: mỗi gợi ý khi hỏi đều có câu trả lời kèm trích dẫn.

## Phạm vi

**Làm:** lệnh `python -m app.eval suggestions` chạy toàn bộ gợi ý của các tài liệu eval như câu hỏi.

## Đặc tả

- Với mỗi tài liệu trong bộ eval: đọc gợi ý → hỏi từng câu với `scope=[tài liệu đó]` → ghi outcome và số citation.
- Đạt khi 100% gợi ý cho `ANSWERED` với ≥ 1 citation.
- Ghi kết quả vào `docs/implement/eval_log.md`.

## Tiêu chí xong

- [ ] Có báo cáo; PO quyết định bật cờ dựa trên kết quả.

## Tham chiếu

US-18 AC-18.1 · T-12-2
