# T-12-1 — Định dạng bộ câu hỏi vàng và validator schema

| Thuộc tính | Giá trị |
|---|---|
| Story | US-12 — Câu trả lời đạt chất lượng đã cam kết (P0) — AC-12.1 |
| Sprint | S3 (đầu sprint, để BA/chuyên gia soạn song song) |
| Tầng | TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | — |
| Chặn | T-12-2, T-08-4, T-14-3, gate G-04 (PO/BA soạn theo định dạng này) |

## Bối cảnh

DEP-002: bộ ≥ 30 câu hỏi mẫu do chuyên gia nghiệp vụ cung cấp, có đáp án chuẩn + doc/page. Cần định dạng rõ ràng để BA soạn mà không cần dev.

## Phạm vi

**Làm:** `tests/eval/schema.py` (pydantic), `tests/eval/golden_v1.yaml` (bản tạm 30 câu trên PDF công khai nếu G-04 chưa có — IR-07), `tests/eval/README.md` hướng dẫn BA.

## Đặc tả

```python
class ExpectedCitation(BaseModel):
    file: str                 # tên tệp trong tests/eval/docs/
    page: int                 # trang bắt đầu từ 1

class EvalItem(BaseModel):
    id: str                   # "Q01"
    type: Literal["in_doc", "multi_doc", "out_of_scope", "counter_factual", "followup", "lang_en", "injection"]
    question: str
    history: list[str] = []   # các câu hỏi trước (follow-up); hệ thống tự hỏi lần lượt
    scope: list[str] = []     # tên tệp giới hạn phạm vi (rỗng = tất cả)
    expected_answer: str | None = None
    must_include: list[str] = []
    must_not_include: list[str] = []
    expected_citations: list[ExpectedCitation] = []
    expected_outcome: Literal["ANSWERED", "NOT_FOUND"] = "ANSWERED"
    expected_lang: Literal["vi", "en"] | None = None
    notes: str = ""

class EvalDataset(BaseModel):
    version: str
    documents: list[str]
    items: list[EvalItem]
    @model_validator(mode="after")
    def _check(self): ...     # id duy nhất; out_of_scope ⇒ expected_outcome NOT_FOUND và không expected_citations;
                              # multi_doc ⇒ ≥ 2 file khác nhau trong expected_citations; mọi file có trong documents
```

Phân bổ tối thiểu (validator cảnh báo nếu thiếu): 10 `in_doc`, 6 `multi_doc`, 6 `out_of_scope`, 4 `counter_factual`, 2 `followup`, 2 `lang_en`; bộ `injection` riêng ≥ 20 mục (T-12-6).

CLI: `python -m app.eval validate tests/eval/golden_v1.yaml`.

`tests/eval/README.md` (cho BA): cách đặt PDF vào `tests/eval/docs/`, cách viết từng loại câu, ví dụ YAML, cách chạy validate.

## Tiêu chí xong

- [ ] `validate` báo lỗi rõ ràng (số dòng/khoá) cho YAML sai.
- [ ] Có bộ tạm 30 câu chạy được.
- [ ] BA xác nhận README đủ để tự soạn.

## Tham chiếu

US-12 · SADD §5.5.3 (Bộ eval tối thiểu) · Implement_plan §17 US-12, §2 G-04
