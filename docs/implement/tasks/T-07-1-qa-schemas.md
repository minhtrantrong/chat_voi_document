# T-07-1 — DTO và domain của hỏi đáp: AskCommand, AnswerHandle, AnswerDTO

| Thuộc tính | Giá trị |
|---|---|
| Story | US-07 — Hỏi bằng câu tự nhiên (P0); dùng chung toàn E2 |
| Sprint | S3 (làm ngày đầu sprint, hoặc cuối S2 để UI làm trước trên dữ liệu giả) |
| Tầng | DOM / APP |
| Ước lượng | 0.25d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | F-01, F-02 |
| Chặn | Mọi task S3 của E2 |

## Bối cảnh

Hợp đồng `QaService` ở SADD §5.7.2. Cố định DTO sớm để Backend 1 làm UI stream trên `FakeLLM` song song với AI/Backend làm pipeline (Implement_plan §23.1).

## Phạm vi

**Làm:** `app/qa/schemas.py`, `app/qa/domain.py` (enum outcome, state machine Answer/Message).

## Đặc tả

```python
class AnswerOutcome(StrEnum): PENDING; ANSWERED; NOT_FOUND; ERROR; ABORTED
TERMINAL_OUTCOMES = frozenset({ANSWERED, NOT_FOUND, ERROR, ABORTED})
class MessageState(StrEnum): STREAMING; COMPLETE; INTERRUPTED
MESSAGE_STATE_FOR = {ANSWERED: COMPLETE, NOT_FOUND: COMPLETE, ABORTED: INTERRUPTED, ERROR: INTERRUPTED}

@dataclass(frozen=True)
class AskCommand:
    conversation_id: UUID | None; question: str; scope_doc_ids: list[UUID]; idempotency_key: str

@dataclass(frozen=True)
class AnswerHandle:
    answer_id: UUID; conversation_id: UUID

@dataclass(frozen=True)
class StreamEvent:
    id: str; type: Literal["status", "token", "reset", "done"]; data: str; seq: int

@dataclass(frozen=True)
class TokenBatch:
    events: list[StreamEvent]; last_id: str

@dataclass(frozen=True)
class CitationDTO:
    id: UUID; document_id: UUID; doc_name: str; page: int; anchor: str; quote: str; deleted: bool

@dataclass(frozen=True)
class SegmentDTO:
    ord: int; text: str; cited: bool; citations: list[CitationDTO]

@dataclass(frozen=True)
class AnswerDTO:
    id: UUID; conversation_id: UUID; question: str; outcome: AnswerOutcome
    message_state: MessageState; segments: list[SegmentDTO]; error_code: str | None
    created_at: datetime; completed_at: datetime | None; my_feedback: Literal["HELPFUL", "NOT_HELPFUL"] | None
    @property
    def is_terminal(self) -> bool: return self.outcome in TERMINAL_OUTCOMES
```

Thêm `FakeQaService` trong `tests/fakes/qa.py`: phát sự kiện stream theo kịch bản (dùng cho UI task T-13-6/T-13-7 trước khi pipeline thật xong).

## Tiêu chí xong

- [ ] Mypy strict xanh; hợp đồng được Tech Lead + 2 owner (AI, BE1) đồng ý trong PR.
- [ ] `FakeQaService` có ít nhất 4 kịch bản: answered, not_found, error, slow stream.

## Tham chiếu

SADD §5.3.8, §5.7.2 · Implement_plan §17
