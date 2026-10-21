# T-24-1 — UI đọc mọi giới hạn từ cấu hình

| Thuộc tính | Giá trị |
|---|---|
| Story | US-24 — Giới hạn rõ số tài liệu và người dùng đồng thời (P0) |
| Sprint | S2–S3 (áp dụng khi làm dropzone và composer) |
| Tầng | UI / TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | F-04, T-01-6, T-07-4 |
| Chặn | — |

## Bối cảnh

US-24: giới hạn hiển thị ở vùng kéo-thả, thông báo lỗi tải lên và bộ đếm ký tự; UI **đọc giá trị từ cấu hình**, không hard-code (Blueprint dùng `GET /api/config`; trong Streamlit là `ConfigService.limits()`).

## Phạm vi

**Làm:** rà soát mọi chỗ hiển thị/kiểm tra giới hạn; test chống hard-code.

## Đặc tả

| Nơi | Giá trị | Nguồn |
|---|---|---|
| Caption dropzone | MB, trang, số tệp | `limits.max_upload_mb`, `max_pages`, `max_files_per_upload` |
| Thông báo lỗi upload | giới hạn trong chuỗi | `error_params` do service điền từ `limits` |
| Composer | `max_chars`, caption "Tối đa n ký tự" | `limits.max_question_chars` |
| Thông báo rate limit | số giây chờ | `retry_after` từ service |
| `server.maxUploadSize` của Streamlit | MAX_UPLOAD_MB + 5 | **ngoại lệ**: cấu hình tĩnh (C-04); ghi chú trong `docs/ops/environment.md` rằng đổi `MAX_UPLOAD_MB` lớn hơn 25 cần đổi cả biến này và restart web |

Test `tests/unit/ui/test_no_hardcoded_limits.py`: quét `app/ui/**` tìm hằng số `25`, `400`, `5` (khi đi cùng chữ "MB", "trang", "tệp") và `2000` → fail.

## Tiêu chí xong

- [ ] Đổi `MAX_UPLOAD_MB=20`, `MAX_QUESTION_CHARS=1000` trong DB → sau ≤ 30 s caption, thông báo, `max_chars` đều đổi mà không deploy.

## Test

AppTest với ConfigService giả trả giá trị khác mặc định; test quét mã ở trên.

## Tham chiếu

US-24 · Blueprint §3.5.4 · ADR-011 · Implement_plan §14 C-04
