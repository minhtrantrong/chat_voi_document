# T-12-4 — Chấm tay bởi chuyên gia: xuất và nhập bảng chấm

| Thuộc tính | Giá trị |
|---|---|
| Story | US-12 (P0) — AC-12.1 (accuracy ≥ MET-002 do chuyên gia chấm) |
| Sprint | S3 (công cụ), S5 (chấm chính thức) |
| Tầng | TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-12-2 |
| Chặn | PLT-16 |

## Bối cảnh

AC-12.1: chuyên gia nghiệp vụ chấm điểm, tỉ lệ đúng ≥ MET-002 (`[TBD: OQ-002]`, mặc định 80%).

## Phạm vi

**Làm:** `python -m app.eval export-grading --run <dir>` và `python -m app.eval grade --run <dir> --import grading.csv`.

## Đặc tả

`grading.csv` (UTF-8 có BOM để Excel mở đúng tiếng Việt), mỗi item một dòng:

| Cột | Nội dung |
|---|---|
| `id`, `type`, `question` | từ dataset |
| `expected_answer` | từ dataset |
| `answer` | câu trả lời (segment nối bằng xuống dòng) |
| `citations` | `hop-dong.pdf tr.7; phu-luc-B.pdf tr.2` |
| `outcome` | ANSWERED / NOT_FOUND / ERROR |
| `grade` | **chuyên gia điền**: `CORRECT` / `PARTIAL` / `WRONG` |
| `citation_ok` | **chuyên gia điền**: `Y` / `N` (trích dẫn có đúng chỗ chứa thông tin không) |
| `comment` | tuỳ chọn |

`grade`: đọc CSV, kiểm tra mọi dòng có `grade`, tính `accuracy = CORRECT / tổng` (PARTIAL tính 0.5 nếu PO đồng ý — cấu hình `--partial-weight`, mặc định 0), `human_citation_accuracy`; ghi `grading_summary.json` cạnh `summary.json`.

## Tiêu chí xong

- [ ] Mở `grading.csv` bằng Excel hiển thị đúng tiếng Việt.
- [ ] Thiếu cột `grade` ở dòng nào thì báo id dòng đó.

## Test

`tests/unit/eval/test_grading.py`.

## Tham chiếu

US-12 AC-12.1 · PRD MET-002 · OQ-002
