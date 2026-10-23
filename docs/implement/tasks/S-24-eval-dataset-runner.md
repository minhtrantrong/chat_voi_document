# S-24 — Bộ eval 20–30 câu và runner báo cáo

| Thuộc tính | Giá trị |
|---|---|
| Story | US-08, US-09 (chất lượng) |
| Phase | P3 |
| Tầng | TEST/TOOL |
| Ước lượng | 0,75d |
| Phụ thuộc | S-11, S-18 |
| Chặn | S-26 |
| Owner gợi ý | Backend |

## 1. Mục tiêu

Có bộ câu hỏi chuẩn + script chạy để đo 3 thứ: trả lời đúng trong tài liệu, tổng hợp nhiều tài liệu, và từ chối đúng khi ngoài phạm vi. Kết quả xuất JSON/Markdown để review trước demo.

## 2. Phạm vi

**Làm:**

- 3 PDF mẫu nhỏ, nội dung biết trước (tạo bằng script, không commit file lớn).
- Dataset 30 câu: 10 in-doc, 10 multi-doc, 10 out-of-scope.
- Runner `app/eval.py` (hoặc `scripts/eval.py`).
- Metrics + report JSON/Markdown.
- Chế độ `--reindex` để nạp lại PDF mẫu.
- Không chạy trong unit test mặc định (cần API/Qdrant).

**Không làm:**

- LLM-as-judge tự động.
- Đo latency/cost chi tiết (có thể thêm).
- Dataset tiếng Anh.
- Fine-tune.

## 3. File chính

```text
tests/eval/dataset.json
tests/eval/fixtures/hop-dong.pdf      # generated, có thể .gitignore
tests/eval/fixtures/bao-gia.pdf
tests/eval/fixtures/quy-dinh.pdf
tests/eval/generate_fixtures.py
app/eval.py
tests/test_eval_schema.py
```

## 4. Đặc tả

### 4.1 PDF mẫu (nội dung cố định)

**hop-dong.pdf**
- Bên A: Công ty Minh Phát.
- Bên B: Công ty Đông Á.
- Giá trị hợp đồng: 1.200.000.000 VNĐ.
- Hạn chót nộp hồ sơ: 30/11/2026.
- Thời hạn hợp đồng: 12 tháng kể từ 01/12/2026.
- Bảo hành: 24 tháng.

**bao-gia.pdf**
- Gói A: 450.000.000 VNĐ.
- Gói B: 620.000.000 VNĐ.
- Thời gian giao hàng gói A: 45 ngày.
- Thời gian giao hàng gói B: 60 ngày.
- Hiệu lực báo giá: 30 ngày.

**quy-dinh.pdf**
- Mật khẩu tối thiểu 12 ký tự.
- Bắt buộc xác thực hai yếu tố.
- Thời gian lưu log: 90 ngày.
- Sao lưu dữ liệu: hằng ngày, giữ 30 bản.
- Thời gian khôi phục mục tiêu (RTO): 4 giờ.

> Nội dung phải **không trùng** giữa các file để test multi-doc có ý nghĩa. Ví dụ câu "So sánh hạn chót nộp hồ sơ và hiệu lực báo giá" cần cả `hop-dong.pdf` + `bao-gia.pdf`.

### 4.2 Dataset schema

`tests/eval/dataset.json`:

```json
[
  {
    "id": "in-01",
    "type": "in_doc",
    "question": "Hạn chót nộp hồ sơ là ngày nào?",
    "expected_docs": ["hop-dong.pdf"],
    "expected_pages": [1],
    "must_contain": ["30/11/2026"],
    "must_not_contain": []
  },
  {
    "id": "multi-01",
    "type": "multi_doc",
    "question": "So sánh thời gian giao hàng của gói A và thời hạn hợp đồng.",
    "expected_docs": ["bao-gia.pdf", "hop-dong.pdf"],
    "expected_pages": [],
    "must_contain": ["45 ngày", "12 tháng"],
    "must_not_contain": []
  },
  {
    "id": "out-01",
    "type": "out_of_scope",
    "question": "Giá cổ phiếu VNM hôm nay là bao nhiêu?",
    "expected_docs": [],
    "expected_pages": [],
    "must_contain": [],
    "must_not_contain": ["VNM", "cổ phiếu"]
  }
]
```

**Quy ước:**

- `type`: `in_doc` | `multi_doc` | `out_of_scope`.
- `expected_docs`: tên file phải xuất hiện trong `sources` (ít nhất 1; multi_doc yêu cầu ≥2).
- `expected_pages`: nếu có, ít nhất 1 source đúng page.
- `must_contain`: tất cả keyword phải có trong answer (so khớp không dấu, lowercase).
- `must_not_contain`: không được có trong answer.
- Out-of-scope: `not_found=True` và `sources=[]`.

### 4.3 Runner

```python
# app/eval.py
def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return " ".join(text.split())

def run(dataset_path: Path, *, reindex: bool = False) -> dict:
    # 1. (tuỳ chọn) ingest 3 PDF mẫu nếu reindex
    # 2. Với mỗi item:
    #    answer, sources, not_found = answer_question(q, [])
    #    đánh giá
    # 3. Tổng hợp metrics + ghi report
```

**Đánh giá:**

```python
def score_item(item, answer, sources, not_found) -> dict:
    ans = normalize(answer)
    src_docs = {s.file_name for s in sources}
    src_pages = {s.page for s in sources}
    if item["type"] == "out_of_scope":
        ok = not_found and not sources
    else:
        doc_ok = (
            len(src_docs & set(item["expected_docs"])) >= 1
            if item["type"] == "in_doc"
            else len(src_docs & set(item["expected_docs"])) >= 2
        )
        page_ok = True
        if item.get("expected_pages"):
            page_ok = bool(src_pages & set(item["expected_pages"]))
        content_ok = all(normalize(k) in ans for k in item.get("must_contain", []))
        forbidden_ok = all(normalize(k) not in ans for k in item.get("must_not_contain", []))
        ok = doc_ok and page_ok and content_ok and forbidden_ok
    return {"id": item["id"], "type": item["type"], "ok": ok, ...}
```

### 4.4 Metrics

```json
{
  "total": 30,
  "in_doc": {"passed": 8, "total": 10},
  "multi_doc": {"passed": 8, "total": 10},
  "out_of_scope": {"passed": 9, "total": 10},
  "source_hit": {"passed": 18, "total": 20},
  "overall": {"passed": 25, "total": 30}
}
```

**Ngưỡng demo (từ kế hoạch §9.3):**

- in_doc ≥ 8/10.
- multi_doc ≥ 8/10.
- out_of_scope ≥ 9/10.
- source_hit ≥ 9/10 câu in/multi.

### 4.5 CLI

```bash
# Nạp lại PDF mẫu + chạy
python -m app.eval --dataset tests/eval/dataset.json --reindex --out eval_report

# Chạy lại không nạp
python -m app.eval --dataset tests/eval/dataset.json --out eval_report
```

Output:
- `eval_report.json` chi tiết từng câu.
- `eval_report.md` bảng tóm tắt + các câu fail.

### 4.6 Danh sách 30 câu mẫu

> PDF mẫu 1 trang, nên `expected_pages` có thể để `[1]` hoặc bỏ trống. `must_contain` nên chọn keyword ổn định, tránh phụ thuộc cách diễn đạt.

**In-doc (10 câu)**

| ID | Câu hỏi | File | Keyword |
|---|---|---|---|
| in-01 | Hạn chót nộp hồ sơ là ngày nào? | hop-dong | 30/11/2026 |
| in-02 | Giá trị hợp đồng là bao nhiêu? | hop-dong | 1.200.000.000 |
| in-03 | Bên A là công ty nào? | hop-dong | Minh Phát |
| in-04 | Thời hạn hợp đồng là bao lâu? | hop-dong | 12 tháng |
| in-05 | Thời gian bảo hành là bao lâu? | hop-dong | 24 tháng |
| in-06 | Gói A có giá bao nhiêu? | bao-gia | 450.000.000 |
| in-07 | Gói B giao hàng trong bao lâu? | bao-gia | 60 ngày |
| in-08 | Báo giá có hiệu lực bao lâu? | bao-gia | 30 ngày |
| in-09 | Mật khẩu tối thiểu bao nhiêu ký tự? | quy-dinh | 12 ký tự |
| in-10 | Log được lưu trong bao lâu? | quy-dinh | 90 ngày |

**Multi-doc (10 câu)**

| ID | Câu hỏi | File kỳ vọng | Keyword |
|---|---|---|---|
| multi-01 | So sánh thời gian giao hàng gói A và thời hạn hợp đồng. | bao-gia + hop-dong | 45 ngày, 12 tháng |
| multi-02 | Tổng giá trị hợp đồng và giá gói B là bao nhiêu? | hop-dong + bao-gia | 1.200.000.000, 620.000.000 |
| multi-03 | Bên A là ai và log được lưu bao lâu? | hop-dong + quy-dinh | Minh Phát, 90 ngày |
| multi-04 | Bảo hành bao lâu và dữ liệu được sao lưu thế nào? | hop-dong + quy-dinh | 24 tháng, 30 bản |
| multi-05 | Gói A giao trong bao lâu và RTO là bao nhiêu? | bao-gia + quy-dinh | 45 ngày, 4 giờ |
| multi-06 | Hiệu lực báo giá và yêu cầu mật khẩu là gì? | bao-gia + quy-dinh | 30 ngày, 12 ký tự |
| multi-07 | So sánh thời hạn hợp đồng và hiệu lực báo giá. | hop-dong + bao-gia | 12 tháng, 30 ngày |
| multi-08 | Bên B là ai và gói B giá bao nhiêu? | hop-dong + bao-gia | Đông Á, 620.000.000 |
| multi-09 | Gói B giao bao lâu và log lưu bao lâu? | bao-gia + quy-dinh | 60 ngày, 90 ngày |
| multi-10 | Bảo hành bao lâu và RTO là bao nhiêu? | hop-dong + quy-dinh | 24 tháng, 4 giờ |

**Out-of-scope (10 câu)**

| ID | Câu hỏi |
|---|---|
| out-01 | Giá cổ phiếu VNM hôm nay là bao nhiêu? |
| out-02 | Thủ đô nước Pháp là gì? |
| out-03 | Thời tiết Hà Nội ngày mai thế nào? |
| out-04 | Tổng thống Mỹ hiện tại là ai? |
| out-05 | Cách nấu phở bò? |
| out-06 | Giá vàng SJC hôm nay? |
| out-07 | Đội nào vô địch World Cup 2022? |
| out-08 | Bitcoin hôm nay bao nhiêu? |
| out-09 | Dân số Việt Nam năm 2026? |
| out-10 | Ai phát minh ra điện thoại? |

## 5. Trường hợp biên

- Chưa `--reindex` và Qdrant rỗng → tất cả fail; runner cảnh báo "chưa có tài liệu".
- API key thiếu → dừng với thông báo rõ.
- Rate limit → dừng hoặc retry; ghi lỗi từng câu, không làm hỏng cả report.
- Câu trả lời đúng ý nhưng khác số (`1.2 tỷ` vs `1.200.000.000`) → `must_contain` có thể fail; chọn keyword linh hoạt hoặc thêm `aliases`.
- Tiếng Việt có dấu/không dấu → normalize NFD + bỏ Mn.
- Nguồn đúng file nhưng sai trang → `expected_pages` fail; với PDF 1 trang, page=1.
- Multi-doc nhưng model chỉ dùng 1 file → fail (đúng mục tiêu).
- Out-of-scope nhưng retrieval vẫn có hit → model có thể trả lời; fail nếu không NOT_FOUND.
- Dataset sai schema → `test_eval_schema.py` bắt.
- PDF mẫu bị xoá → `--reindex` báo lỗi; tạo lại bằng script.

## 6. Tiêu chí xong

- [ ] 30 câu đúng schema, không trùng id.
- [ ] 3 PDF mẫu tạo được bằng script.
- [ ] Runner chạy được, xuất JSON + Markdown.
- [ ] Metrics đúng công thức.
- [ ] Có ít nhất 10 câu out-of-scope.
- [ ] Báo cáo chỉ rõ câu fail + lý do.
- [ ] Không chạy tự động trong `pytest` mặc định.

## 7. Test

`tests/test_eval_schema.py`:

- `test_dataset_schema` (id unique, type hợp lệ, fields bắt buộc).
- `test_normalize_vietnamese`.
- `test_score_item_in_doc`.
- `test_score_item_multi_doc`.
- `test_score_item_out_of_scope`.
- `test_report_counts`.

## 8. Tham chiếu

- Kế hoạch §9.1, §9.3.
- S-11, S-18, S-22, S-26.
