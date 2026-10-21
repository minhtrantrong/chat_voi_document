# F-06 — TelemetryService: sự kiện không chứa nội dung

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng dùng chung (Implement_plan §15; Phần I §4 S1, mục 1.8) |
| Sprint | S1 |
| Tầng | APP / INF |
| Ước lượng | 1d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | PLT-08, F-07 |
| Chặn | T-20-1, mọi điểm phát sự kiện |

## Bối cảnh

US-20 và PRD 5.2: telemetry phục vụ MET-004 nhưng **không** chứa nội dung câu hỏi/trả lời. Theo C-02, sự kiện phát ở server (Python), không từ trình duyệt.

## Phạm vi

**Làm:** `TelemetryService.emit`, whitelist sự kiện và props, ghi bảng `telemetry_events`.

**Không làm:** view báo cáo (T-20-2), điểm phát cụ thể (các task story).

## Đặc tả

```python
EVENT_PROPS: Final[dict[str, frozenset[str]]] = {
    "question_submitted": frozenset({"conversation_id", "is_followup", "scope_count", "question_len"}),
    "answer_first_token": frozenset({"first_token_ms"}),
    "answer_completed":   frozenset({"outcome", "total_ms", "segment_count", "citation_count"}),
    "answer_stopped":     frozenset(),
    "answer_error":       frozenset({"error_code"}),
    "citation_clicked":   frozenset({"page"}),
    "feedback_submitted": frozenset({"value", "has_reason"}),
    "document_uploaded":  frozenset({"document_id", "size_bytes", "page_count"}),
    "document_ready":     frozenset({"document_id", "duration_ms"}),
    "document_failed":    frozenset({"document_id", "error_code"}),
    "document_deleted":   frozenset({"document_id"}),
}

class TelemetryService:
    def emit(self, event: str, user_id: UUID | None, *, answer_id: UUID | None = None,
             tx: UnitOfWork | None = None, **props: object) -> None: ...
```

Quy tắc:
1. `event` không có trong `EVENT_PROPS` thì bỏ, log warn `telemetry_unknown_event`.
2. Props có khoá ngoài whitelist thì bỏ khoá đó, log warn `telemetry_dropped_prop` (chỉ log tên khoá).
3. Giá trị props chỉ được là `int | float | bool | str` ngắn (≤ 64 ký tự, dùng cho ID/enum); UUID chuyển thành `str`.
4. Có `tx` thì ghi trong transaction đó; không có thì tự mở transaction ngắn. Mọi exception khi ghi đều bị bắt và log warn: **telemetry không bao giờ làm hỏng luồng chính**.
5. `answer_id` ghi vào cột `telemetry_events.answer_id` (cần cho view US-20).

## Tiêu chí xong

- [ ] Prop `question="..."` bị loại, không vào DB.
- [ ] DB lỗi khi `emit` thì caller không nhận exception.
- [ ] Mypy strict xanh.

## Test

`tests/unit/telemetry/test_service.py` (repo giả ném lỗi; prop lạ; event lạ); `tests/integration/telemetry/test_emit.py` (ghi thật, có `answer_id`).

## Tham chiếu

US-20 · Implement_plan §20 (bảng sự kiện) · Blueprint §3.7.2 · SADD §5.4.4
