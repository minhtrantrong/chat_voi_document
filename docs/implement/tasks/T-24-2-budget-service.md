# T-24-2 — BudgetService: ngân sách token AI theo ngày

| Thuộc tính | Giá trị |
|---|---|
| Story | US-24 (P0); NFR-COST-01; QA-10 |
| Sprint | S3 (stub `exhausted_today() = False` đủ cho T-07-2), hoàn thiện S5 |
| Tầng | APP / INF |
| Ước lượng | 0.75d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | F-04, Redis client |
| Chặn | T-07-2, T-13-3, PLT-17 (metric chi phí) |

## Bối cảnh

QA-10: vượt ngân sách token ngày → chặn/giảm tần suất, thông báo; không vượt 120% ngân sách. `DAILY_TOKEN_BUDGET` mặc định 2.000.000 (toàn hệ thống).

## Phạm vi

**Làm:** `app/qa/budget.py::BudgetService`, adapter Redis, metric.

## Đặc tả

```python
class BudgetService:
    def add(self, prompt_tokens: int, completion_tokens: int, embedding_tokens: int = 0) -> None: ...
    def used_today(self) -> int: ...
    def exhausted_today(self) -> bool: ...     # used >= DAILY_TOKEN_BUDGET
```

- Khoá Redis `budget:{yyyymmdd theo giờ VN}`; `INCRBY` tổng token; `EXPIRE 172800` (2 ngày).
- `exhausted_today()` đọc giá trị (cache trong process 10 s để `ask` không gọi Redis quá nhiều).
- Vì kiểm tra trước khi hỏi còn câu đang chạy, tổng có thể vượt nhẹ; với 10 câu đồng thời × ~10k token = 100k (5% ngân sách) nên mục tiêu ≤ 120% luôn đạt.
- Ngưỡng cảnh báo 80%: log warn một lần mỗi ngày + metric.
- Metric gauge `cvd_daily_tokens` và `cvd_daily_token_budget` (cập nhật mỗi `add`) cho alert CostOverBudget (PLT-17).
- `DAILY_TOKEN_BUDGET = 0` nghĩa là **không giới hạn** (ghi rõ trong mô tả `app_config`).
- Thông điệp `error.ERR-BUDGET`: "Hệ thống đã đạt hạn mức sử dụng AI hôm nay. Vui lòng thử lại vào ngày mai hoặc liên hệ quản trị."
- Redis lỗi: `exhausted_today()` trả False (không chặn người dùng vì lỗi đo lường), log warn.

## Tiêu chí xong

- [ ] Đặt budget 1.000, sau khi dùng 1.000 token → `ask` trả `ERR_BUDGET`.
- [ ] Sang ngày mới (FrozenClock) → mở lại.

## Test

`tests/integration/qa/test_budget.py`.

## Tham chiếu

SADD §5.9.6, §7.2 QA-10, §7.3 NFR-COST-01, RISK-05 · US-24
