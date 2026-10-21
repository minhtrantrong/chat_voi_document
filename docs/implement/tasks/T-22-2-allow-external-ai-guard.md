# T-22-2 — Khoá an toàn `ALLOW_EXTERNAL_AI` cho adapter LLM/Embedding

| Thuộc tính | Giá trị |
|---|---|
| Story | US-22 (P0) |
| Sprint | S1 (áp vào adapter khi T-04-3, T-08-3 được làm) |
| Tầng | INF |
| Ước lượng | 0.25d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | PLT-05 |
| Chặn | — |

## Bối cảnh

Khi G-01 chưa được duyệt, hệ thống **không được** gửi dữ liệu ra provider ngoài, kể cả do cấu hình nhầm. Cần một khoá kỹ thuật "fail closed".

## Phạm vi

**Làm:** hàm factory `build_llm(settings)` và `build_embedding(settings)` ở `app/infrastructure/{llm,embedding}/factory.py` kiểm tra khoá.

## Đặc tả

```python
def build_llm(s: Settings) -> LLMPort:
    if s.llm_provider == "fake":
        return FakeLLM.from_env()
    if s.llm_provider in EXTERNAL_PROVIDERS and not s.allow_external_ai:
        raise RuntimeError("ALLOW_EXTERNAL_AI=false: từ chối khởi tạo LLM provider bên ngoài")
    return OpenAICompatibleLLM(...)
```

- `EXTERNAL_PROVIDERS = {"openai-compatible", "anthropic"}`; `self-host` (trong mạng nội bộ) không bị chặn.
- Áp dụng cho **mọi** môi trường, không chỉ production: dev/staging dùng `fake` hoặc dữ liệu giả với `ALLOW_EXTERNAL_AI=true` được bật có chủ đích.
- Log info ở khởi động: `ai_provider_configured provider=... external=... allowed=...` (không log key).
- `/readyz` (PLT-06) thêm check `ai_config` trả `fail: external_ai_not_allowed` khi rơi vào trường hợp bị chặn, để lỗi lộ ra sớm.

## Tiêu chí xong

- [ ] `ALLOW_EXTERNAL_AI=false` + provider `openai-compatible`: worker không khởi động, thông báo rõ.
- [ ] `ALLOW_EXTERNAL_AI=true`: khởi động bình thường.
- [ ] Ghi vào `docs/ops/environment.md` (PLT-20): chỉ bật sau khi có văn bản G-01.

## Test

`tests/unit/infrastructure/test_ai_factory.py`: 4 tổ hợp provider × cờ.

## Tham chiếu

US-22 · ADR-009 · SADD §5.8.6 (LLM)
