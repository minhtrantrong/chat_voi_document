# T-20-4 — Kịch bản kiểm thử số câu hỏi theo tuần (AC-20.1)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-20 (P0) — AC-20.1 |
| Sprint | S3 |
| Tầng | TEST |
| Ước lượng | 0.75d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | T-20-1, T-20-2, T-20-3 |
| Chặn | — |

## Bối cảnh

AC-20.1: với dữ liệu sử dụng một tuần trong kịch bản kiểm thử, số câu hỏi theo từng người khớp 100%, câu lỗi AI không tính.

## Phạm vi

**Làm:** `tests/integration/telemetry/test_weekly_questions.py`.

## Đặc tả

Dữ liệu (FrozenClock trong tuần 2026-W45, chạy qua `QaService` + worker với FakeLLM có thể điều khiển outcome):

| User | ANSWERED | NOT_FOUND | ABORTED | ERROR | Mong đợi |
|---|---|---|---|---|---|
| U1 | 5 | 1 | 1 | 1 | 7 |
| U2 | 3 | 2 | 0 | 1 | 5 |
| U3 | 2 | 0 | 1 | 0 | 3 |
| **Tổng** | | | | | **15** |

Thêm: 1 câu của U1 vào tuần trước (không được tính vào W45); 1 câu bị `ERR_RATE_LIMIT` (không tạo answer, không tính).

Khẳng định:
- `SELECT * FROM v_weekly_questions WHERE week_start = '2026-11-02'` trả đúng 3 dòng với số mong đợi.
- CLI T-20-3 xuất đúng các số đó.
- Không event nào chứa nội dung câu hỏi (kiểm `props`).

## Tiêu chí xong

- [ ] Test xanh.

## Tham chiếu

US-20 AC-20.1
