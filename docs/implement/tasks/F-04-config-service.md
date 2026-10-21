# F-04 — ConfigService: giới hạn nghiệp vụ và feature flag từ `app_config`

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng dùng chung (Implement_plan §15; Phần I §4 S1, mục 1.7) |
| Sprint | S1 |
| Tầng | DB / APP / INF |
| Ước lượng | 1.5d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | PLT-08, F-07 |
| Chặn | T-01-4, T-07-2, T-24-1, T-24-3, mọi chỗ đọc giới hạn/cờ |

## Bối cảnh

ADR-011: giới hạn nghiệp vụ và feature flag nằm trong DB, đọc qua cache TTL 30 s, admin sửa được mà không deploy. US-24: UI không hard-code giới hạn.

## Phạm vi

**Làm:**
- Migration `0002_seed_app_config` chèn các khoá ở bảng dưới (`ON CONFLICT DO NOTHING`).
- `app/admin/schemas.py`: `Limits`, `Flags`.
- `app/admin/service.py`: `ConfigService.limits()`, `flags()`, `get(key)`, `invalidate()`.
- Repository `AppConfigRepository` ở `app/infrastructure/db/`.

**Không làm:** form sửa config (T-24-3).

## Đặc tả

Khoá seed (mặc định lấy từ `Settings` nếu có, PLT-05):

| Khoá | Kiểu | Mặc định | Ràng buộc |
|---|---|---|---|
| `MAX_UPLOAD_MB` | int | 25 | 1–100 |
| `MAX_PAGES` | int | 400 | 1–2000 |
| `MAX_FILES_PER_UPLOAD` | int | 5 | 1–20 |
| `MAX_QUESTION_CHARS` | int | 2000 | 100–8000 |
| `RETRIEVAL_TOP_K` | int | 8 | 1–20 |
| `RETRIEVAL_MIN_SCORE` | float | 0.25 | 0–1 |
| `MAX_CHUNKS_PER_DOC` | int | 4 | 1–8 |
| `MAX_CONTEXT_TOKENS` | int | 8000 | 1000–32000 |
| `MAX_OUTPUT_TOKENS` | int | 1200 | 100–4000 |
| `HISTORY_TURNS` | int | 3 | 0–10 |
| `MIN_TEXT_CHARS_PER_PAGE` | int | 20 | 0–500 |
| `RATE_LIMIT_ASKS_PER_HOUR` | int | 30 | 1–1000 |
| `DAILY_TOKEN_BUDGET` | int | 2000000 | ≥ 0 |
| `CONVERSATION_RETENTION_DAYS` | int | 180 | 1–3650 |
| `DOCUMENT_DEFAULT_VISIBILITY` | str | "PRIVATE" | PRIVATE \| SHARED |
| `ACCESS_REQUEST_CONTACT` | str | "" | — |
| `FEATURE_SOURCE_VIEWER` | bool | true | — |
| `FEATURE_SCOPE_SELECT` | bool | true | — |
| `FEATURE_FEEDBACK` | bool | true | — |
| `FEATURE_QUERY_REWRITE` | bool | false | — |
| `FEATURE_SUMMARIZE` | bool | false | — |
| `FEATURE_SUGGESTIONS` | bool | false | — |
| `FEATURE_DOC_SHARING` | bool | false | — |

`value` lưu dạng jsonb (ví dụ `25`, `0.25`, `"PRIVATE"`, `true`). `description` ghi ý nghĩa bằng tiếng Việt.

```python
@dataclass(frozen=True)
class Limits:
    max_upload_mb: int; max_pages: int; max_files_per_upload: int; max_question_chars: int
    retrieval_top_k: int; retrieval_min_score: float; max_chunks_per_doc: int
    max_context_tokens: int; max_output_tokens: int; history_turns: int
    min_text_chars_per_page: int; rate_limit_asks_per_hour: int; daily_token_budget: int
    conversation_retention_days: int; default_visibility: Literal["PRIVATE", "SHARED"]
    access_request_contact: str

@dataclass(frozen=True)
class Flags:
    source_viewer: bool; scope_select: bool; feedback: bool; query_rewrite: bool
    summarize: bool; suggestions: bool; doc_sharing: bool

class ConfigService:
    def __init__(self, repo: AppConfigRepository, clock: Clock, ttl_s: float = 30): ...
    def limits(self) -> Limits: ...     # cache trong process, hết TTL thì đọc lại toàn bộ bảng 1 truy vấn
    def flags(self) -> Flags: ...
    def invalidate(self) -> None: ...
```

- Cache **trong process** dùng chung giữa các session là an toàn vì đây không phải dữ liệu phân quyền (khác với quy tắc cấm `st.cache_data`).
- Giá trị trong DB sai kiểu hoặc ngoài khoảng thì log error và dùng mặc định (không làm sập app).
- Thread-safe (`threading.Lock`), vì web chạy nhiều ScriptRunner thread.

## Tiêu chí xong

- [ ] Sau `alembic upgrade head` có đủ khoá trong bảng trên.
- [ ] Sửa trực tiếp `MAX_UPLOAD_MB` trong DB thì `limits()` trả giá trị mới sau ≤ 30 s.
- [ ] Giá trị rác (`"abc"` cho số) không làm lỗi, có log error.

## Test

- `tests/unit/admin/test_config_service.py` (repo giả + FrozenClock): cache hit/miss theo TTL; `invalidate`; giá trị sai kiểu.
- `tests/integration/db/test_app_config_seed.py`: seed đủ khoá, chạy lại migration không nhân đôi.

## Tham chiếu

ADR-011 · SADD §10.2 · Implement_plan §14 C-09, C-10, C-18 · US-24
