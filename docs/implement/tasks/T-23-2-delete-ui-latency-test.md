# T-23-2 — E2E: tài liệu biến khỏi UI ≤ 1 s sau khi xoá

| Thuộc tính | Giá trị |
|---|---|
| Story | US-23 (P0) — CN-10 |
| Sprint | S4 |
| Tầng | TEST |
| Ước lượng | 0.25d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | T-06-5 |
| Chặn | — |

## Bối cảnh

US-23: tài liệu biến mất khỏi UI ≤ 1 s (CN-10).

## Phạm vi

**Làm:** kịch bản Playwright trong `tests/e2e/test_delete_latency.py`.

## Đặc tả

1. Đăng nhập, upload `text.pdf`, chờ READY.
2. Mở menu ⋯ → Xoá → trong dialog bấm "Xoá" và ghi `t0`.
3. Chờ phần tử `[data-testid] chứa "text.pdf"` trong cột Tài liệu biến mất, ghi `t1`.
4. Khẳng định `t1 - t0 ≤ 1000 ms` (chạy 5 lần, lấy p80).

## Tiêu chí xong

- [ ] Test xanh trên CI e2e.

## Tham chiếu

US-23 · Blueprint CN-10
