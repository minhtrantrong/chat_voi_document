# F-11 — Bootstrap service cho UI và quản lý session_state

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng dùng chung (Implement_plan §15) |
| Sprint | S1 |
| Tầng | UI / wiring |
| Ước lượng | 1d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | F-04…F-08, PLT-07 |
| Chặn | Mọi UI task |

## Bối cảnh

UI không được import hạ tầng (PLT-02). Mọi service được dựng một lần mỗi process trong `app/bootstrap.py` và lấy qua `get_services()`. `st.session_state` chỉ giữ trạng thái giao diện (SADD P-01), với tiền tố module (§5.7.1).

## Phạm vi

**Làm:** `app/bootstrap.py`, `app/ui/state.py` (`get_actor`, `run_safely`, hằng khoá state, `new_corr_id`).

## Đặc tả

```python
# app/bootstrap.py
@dataclass(frozen=True)
class Services:
    identity: IdentityService; documents: DocumentService; qa: QaService
    conversations: ConversationService; feedback: FeedbackService
    config: ConfigService; audit: AuditService; telemetry: TelemetryService; admin: AdminService

@st.cache_resource(show_spinner=False)
def get_services() -> Services: ...      # dựng engine, redis client, s3 client, adapter, service
```

- Service nào chưa làm thì dùng bản stub ném `NotImplementedError` để UI vẫn import được.
- `get_services` cũng gọi `start_metrics_server(9101)` (PLT-06).
- Không cache gì liên quan tới người dùng trong `cache_resource`.

```python
# app/ui/state.py
class K:                                   # khoá session_state, tránh gõ sai
    AUTH_ACTOR = "auth.actor"; AUTH_DRAFT_BANNER = "auth.draft"
    DOCS_UPLOAD_NONCE = "docs.upload_nonce"; DOCS_PROCESSED_NONCE = "docs.processed_nonce"
    DOCS_UPLOAD_ERRORS = "docs.upload_errors"; DOCS_HAS_READY = "docs.has_ready"; DOCS_LIMIT = "docs.limit"
    CHAT_CONV_ID = "chat.conversation_id"; CHAT_ACTIVE_ANSWER = "chat.active_answer_id"
    CHAT_LAST_ID = "chat.last_id"; CHAT_BUF = "chat.buf"; CHAT_PHASE = "chat.phase"; CHAT_DONE = "chat.done"
    CHAT_SCOPE = "chat.scope"; CHAT_STARTED_AT = "chat.started_at"
    SOURCE_DOC = "source.doc_id"; SOURCE_PAGE = "source.page"; SOURCE_QUOTE = "source.quote"
    SOURCE_CITE_KEY = "source.citation_key"; FB_PENDING = "fb.pending"

def get_actor() -> Actor:                  # đọc K.AUTH_ACTOR; chưa có thì gọi identity.resolve_actor(st.user)
def new_corr_id() -> str:                  # gán contextvar corr_id đầu mỗi lần chạy script (PLT-09)
def run_safely(fn: Callable[[], T], *, on_error_toast: bool = True) -> T | None:
    """Bắt AppError → hiển thị error_text(err) (st.error hoặc st.toast);
       Exception khác → log.exception + hiển thị ERR_INTERNAL kèm corr_id; trả None."""
def reset_chat_state(keep_scope: bool = True) -> None   # dùng cho "Hội thoại mới" (T-16-1)
```

Quy tắc: **không** lưu token, secret, nội dung PDF vào `session_state`; câu trả lời đang stream (`chat.buf`) là ngoại lệ được phép vì chỉ hiển thị cho chính người dùng và mất khi đóng phiên.

## Tiêu chí xong

- [ ] Rerun trang 100 lần: `get_services()` chỉ dựng một lần (đếm bằng log).
- [ ] `run_safely` với `NotFound` hiển thị đúng chuỗi; với `ValueError` hiển thị mã tra cứu và log có stack trace.
- [ ] lint-imports xanh (UI chỉ import `app.bootstrap`, không import `app.infrastructure`).

## Test

`tests/unit/ui/test_state.py` (AppTest + service giả).

## Tham chiếu

SADD §4.1, §4.3 P-01, §4.5, §5.7.1
