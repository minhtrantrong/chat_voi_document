# T-20-3 — CLI báo cáo số câu hỏi theo tuần

| Thuộc tính | Giá trị |
|---|---|
| Story | US-20 (P0) |
| Sprint | S3 |
| Tầng | OPS |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | T-20-2 |
| Chặn | — |

## Bối cảnh

US-20: không có UI người dùng; màn hình báo cáo cho quản lý nằm ngoài MVP. PM cần lấy số liệu MET-004.

## Phạm vi

**Làm:** subcommand `python -m app.ops report weekly-questions`.

## Đặc tả

```
python -m app.ops report weekly-questions --week 2026-W45 [--format csv|table] [--out file.csv]
python -m app.ops report weekly-questions --from 2026-11-01 --to 2026-11-30
```

Cột đầu ra: `week_start, user_id, display_name, questions`. Thêm dòng tổng.

- Chạy trên máy chủ (`docker compose exec ops python -m app.ops report …`), dùng DB role đọc.
- `display_name`: cần **PO/Security xác nhận** việc xuất tên người dùng; mặc định xuất `user_id_hash` (`hash_id`), cờ `--with-names` mới xuất tên và ghi audit `report.export` (thêm vào `AuditAction`).
- Tuần ISO (`2026-W45`) chuyển thành `week_start` thứ Hai theo giờ Việt Nam.

## Tiêu chí xong

- [ ] CSV mở bằng Excel đúng tiếng Việt (UTF-8 BOM).
- [ ] `--with-names` ghi audit.

## Test

`tests/integration/ops/test_weekly_report.py`.

## Tham chiếu

US-20 · PRD 5.2 · SADD §5.4.2 (PII)
