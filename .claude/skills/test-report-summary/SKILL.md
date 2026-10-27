---
name: test-report-summary
description: Tổng hợp các test_reports/<ID>/report.md thành Test Summary Report (IEEE 829) cho một chu kỳ C2/C3/C4 hoặc toàn bộ — tỷ lệ pass theo nhóm, sổ bug hợp nhất S1–S4, đánh giá exit criteria test plan §7.0, khuyến nghị Go/No-go. Dùng khi người dùng nói "tổng hợp kết quả test", "báo cáo cycle C2", "test summary report", "đã đủ điều kiện sang C3 chưa", "bug list hiện tại".
---

# test-report-summary — Báo cáo tổng hợp chu kỳ kiểm thử

Đầu vào: chu kỳ (`C2`, `C3`, `C4`) hoặc `all`. Nếu người dùng không nói rõ, chọn chu kỳ cao nhất đang có report và nói rõ lựa chọn đó.
Đầu ra: `test_reports/_summary/<CYCLE>-summary-<YYYY-MM-DD>.md`, kèm vài dòng tóm tắt trong chat.

## Bước 1 — Thu thập dữ liệu

```bash
python .claude/skills/test-report-check/scripts/report_lint.py --all --catalog --json > "<scratchpad>/reports.json"
```

`--catalog` lấy cả các case chưa có report, khi đó `overall = MISSING`. Mỗi phần tử có `case_id, title, group, priority, cycle, overall, steps_*, bugs[], issues[]`.

Đọc thêm:
- [docs/testing/testcases/README.md](../../../docs/testing/testcases/README.md) §4: danh sách case thuộc từng chu kỳ. Chọn case theo bảng này, đừng dựa vào trường `cycle` (trường đó có thể ghi "C3→C4").
- [docs/testing/TestPlan_Simple_Qdrant.md](../../../docs/testing/TestPlan_Simple_Qdrant.md) §4.7 (§7.0 Pass/Fail + exit criteria), §4.8 (§8.0 Suspension), §5 (traceability FR ↔ case).
- Report nào có `issues` mức ERROR: vẫn đưa vào, nhưng đánh dấu "report chưa đạt chuẩn" và nêu trong phần Variances.
- Với case FAIL, đọc đoạn "Kết quả tổng" và bảng bug trong report gốc để tóm tắt lý do chính xác, không tự suy diễn.
- Nếu có kết quả pytest (C1, D-03): chạy `uv run pytest -q` khi người dùng đồng ý (cần Qdrant cho integration), hoặc ghi "chưa có bằng chứng".

## Bước 2 — Hợp nhất bug

- Gộp bug từ mọi report. Bug cùng ID xuất hiện nhiều lần (có "(lặp lại)") gom thành một dòng, liệt kê mọi case gặp phải.
- Hai ID khác nhau nhưng mô tả cùng một hiện tượng: gộp và ghi chú "có thể trùng". Không tự đổi ID trong report gốc.
- Trạng thái: mặc định **Open**. **Closed** chỉ khi có lần retest PASS chứng minh (report mới của case đó, hoặc ghi chú retest). **Ngoài phạm vi sản phẩm** dành cho bug dữ liệu test, ví dụ fixture sai.
- Sắp xếp theo mức S1 → S4, rồi theo ID.

## Bước 3 — Đánh giá exit criteria

Đối chiếu từng tiêu chí §7.0 với bằng chứng, mỗi tiêu chí một dòng: **Đạt / Không đạt / Chưa có bằng chứng**. Tối thiểu gồm:

| Tiêu chí | Cách xác định |
|---|---|
| ST-01…06 pass 100% | `overall` của 6 case |
| Biên ST-07…18 pass hoặc bug đã ghi kèm mức | FAIL nào cũng phải có bug S1–S4 |
| 0 traceback UI | không bug/quan sát nào nhắc tới traceback/`stException` |
| Eval đạt ngưỡng QLT-01…04 | tỷ lệ trong report EV-01…04 |
| 100% SEC pass | SEC-01…04 |
| PF-04 từ chối nhanh; PF-01…03 không timeout | PF-xx |
| Không bug S1/S2 mở | sổ bug |
| pytest xanh | output pytest, nếu có |

Chỉ đánh giá các tiêu chí thuộc phạm vi chu kỳ đang tổng hợp. Tiêu chí của chu kỳ sau thì ghi "Ngoài phạm vi C<n>".

**Khuyến nghị**:
- **Go**: mọi tiêu chí trong phạm vi Đạt.
- **Go có điều kiện**: chỉ còn bug S3/S4 hoặc FAIL do dữ liệu test. Liệt kê điều kiện cụ thể.
- **No-go**: còn bug S1/S2 mở, case bắt buộc FAIL do app, hoặc thiếu bằng chứng cho case bắt buộc.

## Bước 4 — Viết báo cáo

Dùng mẫu [references/summary-template.md](references/summary-template.md). Yêu cầu:
- Mọi con số phải lấy từ dữ liệu bước 1. Ghi rõ mẫu số, ví dụ "2/9 case đã chạy, 0/2 PASS".
- Link tương đối tới từng `../<ID>/report.md`.
- Không sao chép nguyên bảng bước. Mỗi case chỉ 1 dòng lý do.
- Các con số nên tính bằng một script Python ngắn chạy trên `reports.json`, không đếm tay.

Sau khi ghi file: chạy lại phép đếm một lần để đối chiếu, rồi báo trong chat: kết quả khuyến nghị, số liệu chính, top bug S1–S3, và link tới file summary. Tài liệu này để chia sẻ với QA/Dev/PO; nếu người dùng muốn gửi đi, hãy đề nghị xuất bản thành trang chia sẻ.
