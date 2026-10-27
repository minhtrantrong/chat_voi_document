# Mẫu Test Summary Report (IEEE 829-2008 §11, rút gọn)

````markdown
# Test Summary Report — Chu kỳ <C2|C3|C4|Toàn bộ>

| Mục | Giá trị |
|---|---|
| Mã báo cáo | TSR-CVD-<CYCLE>-<YYYYMMDD> |
| Test plan | [TP-CVD-004](../../docs/testing/TestPlan_Simple_Qdrant.md) v1.0 |
| Phạm vi | <danh sách case theo README §4> |
| Thời gian thực thi | <ngày report sớm nhất> → <muộn nhất> |
| Người lập / ngày | <agent/người> · YYYY-MM-DD |
| **Khuyến nghị** | **Go / Go có điều kiện / No-go**: <1 câu> |

## 1. Tóm tắt

<3–5 câu dành cho PO: đã chạy bao nhiêu case, bao nhiêu PASS, vấn đề lớn nhất, quyết định đề xuất.>

| Chỉ số | Giá trị |
|---|---|
| Case trong phạm vi | N |
| Đã chạy | x/N |
| PASS / FAIL / BLOCKED | a / b / c |
| Chưa chạy (MISSING) | d |
| Bước PASS (tổng) | p/q |
| Bug mở theo mức | S1: · S2: · S3: · S4: |

## 2. Kết quả theo nhóm

| Nhóm | Phạm vi | Đã chạy | PASS | FAIL | BLOCKED | Chưa chạy |
|---|---|---|---|---|---|---|
| System (luồng chính ST-01…06) | | | | | | |
| System (biên ST-07…18) | | | | | | |
| UI | | | | | | |
| Security | | | | | | |
| Performance | | | | | | |
| Eval RAG | | | | | | |

## 3. Kết quả từng case

| Case | Tên | Ưu tiên | Kết quả | Bước PASS | Bug | Lý do chính | Report |
|---|---|---|---|---|---|---|---|
| ST-01 | … | High | **FAIL** | 4/6 | S3×1, S4×2 | <1 dòng; nêu app sai hay dữ liệu/tiền điều kiện sai> | [report](../ST-01/report.md) |

## 4. Sổ bug hợp nhất

| Bug ID | Mức | Mô tả ngắn | Gặp ở case | Loại | Trạng thái |
|---|---|---|---|---|---|
| BUG-ST02-01 | S3 | … | ST-02 | Sản phẩm | Open |
| BUG-ST01-01 | S3 | Fixture hop-dong.pdf 1 trang thay vì 32 | ST-01, ST-02 | Dữ liệu test | Open |

## 5. Đánh giá exit criteria (test plan §7.0)

| # | Tiêu chí | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | … | Đạt / Không đạt / Chưa có bằng chứng / Ngoài phạm vi | … |

## 6. Sai lệch (Variances)

- Sai lệch môi trường/tiền điều kiện lặp lại giữa các case, ví dụ kho không trống, công cụ quay không thấy thanh địa chỉ.
- Report chưa đạt chuẩn (còn ERROR từ `report_lint.py`).
- Thay đổi so với kế hoạch (case bỏ qua, chạy khác thứ tự).

## 7. Đánh giá tổng thể và rủi ro

<Mức độ tin cậy vào chất lượng, vùng chưa được kiểm, rủi ro nếu đi tiếp (liên hệ §15.0 Risks).>

## 8. Hành động tiếp theo

| # | Việc | Người phụ trách | Điều kiện xong |
|---|---|---|---|
| 1 | Fix + retest BUG-… | Dev / QA | Report retest PASS |

## 9. Phê duyệt

| Vai trò | Họ tên | Quyết định | Ngày |
|---|---|---|---|
| QA | | | |
| Product Owner | | | |
````
