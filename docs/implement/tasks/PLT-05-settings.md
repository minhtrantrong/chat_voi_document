# PLT-05 — Cấu hình môi trường bằng pydantic-settings

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S0, mục 0.6) |
| Sprint | S0 |
| Tầng | OPS / INF |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | PLT-01 |
| Chặn | F-04, F-07, mọi adapter |

## Bối cảnh

ADR-011: **secret và hạ tầng** nằm trong env/secret manager; **giới hạn nghiệp vụ và feature flag** nằm trong bảng `app_config` (F-04). Task này chỉ làm phần env.

## Phạm vi

**Làm:** `app/config.py` với class `Settings`, validate và fail-fast; hàm `get_settings()`.

**Không làm:** đọc `app_config` (F-04).

## Đặc tả

```python
# app/config.py
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["local", "dev", "staging", "production"] = "production"
    app_base_url: AnyHttpUrl
    database_url: PostgresDsn                     # postgresql+psycopg://app_rw:...
    db_pool_size: int = 15
    db_statement_timeout_ms: int = 10_000
    redis_url: RedisDsn
    s3_endpoint: AnyHttpUrl
    s3_bucket: str = "cvd-documents"
    s3_access_key: SecretStr
    s3_secret_key: SecretStr
    oidc_issuer: AnyHttpUrl
    oidc_client_id: str
    oidc_client_secret: SecretStr
    oidc_redirect_uri: AnyHttpUrl
    streamlit_cookie_secret: SecretStr
    llm_provider: Literal["openai-compatible", "anthropic", "self-host", "fake"] = "openai-compatible"
    llm_base_url: AnyHttpUrl | None = None
    llm_model: str
    llm_api_key: SecretStr | None = None
    llm_timeout_s: float = 60
    llm_first_token_timeout_s: float = 10
    embedding_provider: Literal["openai-compatible", "self-host", "fake"]
    embedding_model: str
    embedding_dim: int = 1536
    embedding_batch_size: int = 64
    allow_external_ai: bool = False               # T-22-2
    otel_exporter_otlp_endpoint: AnyHttpUrl | None = None
    log_level: str = "INFO"
    # Giá trị seed mặc định cho app_config (F-04 dùng khi khởi tạo DB)
    max_upload_mb: int = 25
    max_pages: int = 400
    max_files_per_upload: int = 5

    @model_validator(mode="after")
    def _check(self) -> "Settings": ...
```

Quy tắc validate trong `_check`:

1. `len(streamlit_cookie_secret) >= 32`.
2. `embedding_dim == 1536` (khớp schema `vector(1536)`; đổi phải có migration).
3. `llm_provider != "fake"` thì `llm_base_url` và `llm_api_key` bắt buộc; tương tự với embedding.
4. `app_env == "production"` thì cấm `llm_provider == "fake"`.
5. Thiếu biến bắt buộc thì `ValidationError` liệt kê **tên** biến (không in giá trị).

`get_settings()` dùng `functools.lru_cache(maxsize=1)`. Secret chỉ đọc qua `.get_secret_value()` tại adapter, **không** truyền vào log hay `st.session_state`.

## Tiêu chí xong

- [ ] Khởi động `web`/`worker`/`ops` thiếu `DATABASE_URL` thì thoát mã ≠ 0 với thông báo nêu tên biến.
- [ ] `repr(get_settings())` không chứa giá trị secret (pydantic in `**********`).
- [ ] `.env.example` khớp đúng danh sách field.

## Test

`tests/unit/test_config.py`: thiếu biến bắt buộc; cookie secret ngắn; `embedding_dim=768` bị từ chối; production + fake LLM bị từ chối; repr không lộ secret.

## Tham chiếu

SADD §10.2, ADR-011, §5.8.6
