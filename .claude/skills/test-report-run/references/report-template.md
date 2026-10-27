# Mẫu report.md chuẩn

Mẫu này mở rộng mục §9 của từng test case. Giữ nguyên tên các trường in đậm: script `report_lint.py` dựa vào chúng (`**Kết quả tổng:**`, `**Agent / người test:**`, `**Ngày:**`, `**Môi trường:**`, `**Video:**`, bảng có cột `#` + `Kết quả`, bảng có cột `Bug ID`).

Bỏ phần nào không áp dụng, **trừ** bảng bug: không có bug thì vẫn giữ tiêu đề bảng và ghi một dòng "Không phát hiện bug".

````markdown
# Test Report — <ID>: <Tên test case>

- **Agent / người test:** <tên agent/model>, chạy cho <người yêu cầu> · **Ngày:** YYYY-MM-DD (HH:MM:SS–HH:MM:SS, giờ máy)
- **Môi trường:** OS: … · Python: … · Streamlit … · Qdrant image: `qdrant/qdrant:vX` (healthy) · LLM: `…` · Embedding: `…` (N chiều) · Browser: … (headed/headless, điều khiển qua …, viewport WxH)
- **App URL:** http://localhost:8501/
- **Lần chạy:** 1 (hoặc: Retest lần N của BUG-…, xem `_run-YYYY-MM-DD/`)
- **Kết quả tổng:** **PASS** | **FAIL** | **BLOCKED** — <1–3 câu: lý do chính dẫn tới kết quả; nêu ý nào đạt, ý nào không>

## Sai lệch so với tiền điều kiện / dữ liệu thử nghiệm

| Mục | Yêu cầu trong test case | Thực tế |
|---|---|---|
| … | … | … |

## Kết quả từng bước

| # | Bước | Kỳ vọng | Thực tế | Kết quả | Ảnh |
|---|---|---|---|---|---|
| 1 | … | … | <quan sát cụ thể: chữ trên UI, giá trị DB/Qdrant, ID> | **PASS** | [V01](screenshots/V01-….png) |
| 2 | … | … | … | **FAIL** (<lý do ngắn>) | [V02](screenshots/V02-….png) |

## Kết quả mong đợi tổng thể (mục 5)

| Tiêu chí | Kết quả |
|---|---|
| … | **Đạt** / **Đạt một phần**: … / **Không đạt**: … |

- **Video:** [./video.webm](video.webm): <độ dài> giây, <WxH>, <fps>. Quay liên tục từ trước bước 1 tới sau bước cuối; <cách hiển thị URL>.
- **Bug phát hiện:**

| Bug ID | Mô tả | Mức (S1–S4) | Ảnh |
|---|---|---|---|
| BUG-<CASE>-01 | <hiện tượng> — <kỳ vọng theo FR/AC nào> — <nguyên nhân nghi ngờ, file/hàm nếu biết> | S3 | [V02](screenshots/V02-….png) |
| OBS-<CASE>-02 | (Quan sát, ngoài phạm vi case) … | S4 | … |

## Ghi chú

- Không sửa code ứng dụng trong lúc test.
- Dữ liệu test: [test-data/](test-data/) (nếu có).
- Dữ liệu phát sinh sau test: <doc_id… còn trong SQLite/Qdrant/data/uploads>; trạng thái kho hiện tại.
- Muốn chạy lại đúng tiền điều kiện thì cần: …
````

## Biến thể cho EV-xx (bảng chấm)

Bảng bước thay bằng bảng chấm câu hỏi. Cột phán định là `Đúng/Sai`. Dòng Kết quả tổng phải ghi tỷ lệ và ngưỡng:

```markdown
- **Kết quả tổng:** **PASS** (9/10 đúng; ngưỡng ≥ 8 — QLT-01)

| # | Câu hỏi | Kỳ vọng | Thực tế | Đúng/Sai | Nguồn | Ảnh |
|---|---|---|---|---|---|---|
| 1 | … | … | <trích câu trả lời> | Đúng | hop-dong.pdf, trang 3 | [V02](screenshots/V02-cau-01.png) |
```

Câu sai phải có thêm một mục "Phân tích câu sai": truy hồi sai chunk, LLM bịa, hay nguồn sai.

## Biến thể cho PF-xx

Thêm bảng số đo: lần đo, giá trị, p50/p90 (nếu áp dụng), ngưỡng, cách đo (đồng hồ UI / log / script). Ghi rõ phần cứng và model, vì baseline phụ thuộc vào chúng.
