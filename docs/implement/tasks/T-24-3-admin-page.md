# T-24-3 — Trang Quản trị: cấu hình, feature flag, audit, job DEAD

| Thuộc tính | Giá trị |
|---|---|
| Story | US-24 (P0); SADD §5.7.1 `/admin` |
| Sprint | S5 |
| Tầng | APP / UI |
| Ước lượng | 2d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | F-04, F-05, F-08, PLT-07 |
| Chặn | — |

## Bối cảnh

SADD §5.7.1: `/admin` (ADMIN) gồm `ConfigForm`, `AuditTable`; §5.3.7: DLQ — admin retry thủ công; §5.8.3: PM xem audit (read-only), chỉ ADMIN sửa config.

## Phạm vi

**Làm:** `AdminService` (`app/admin/service.py`) và `app/ui/pages/admin.py` với 3 tab.

## Đặc tả

`AdminService`:

```python
def list_config(self, actor) -> list[ConfigEntryDTO]: ...                  # ADMIN, PM (đọc)
def update_config(self, actor, key: str, value: Any) -> ConfigEntryDTO:     # chỉ ADMIN
    # validate theo bảng ràng buộc F-04 (kiểu + khoảng); sai → Invalid(ERR_DOC_422, {"key", "reason"})
    # UPDATE app_config SET value, version = version + 1, updated_by, updated_at WHERE key=:k AND version=:expected
    # audit CONFIG_UPDATE {key, old, new}; sau commit config.invalidate()
def list_dead_jobs(self, actor, limit=50) -> list[JobDTO]: ...              # chỉ ADMIN; không trả payload thô, chỉ type, id tài liệu/answer, last_error, attempts, updated_at
def retry_job(self, actor, job_id: int) -> None: ...                        # chỉ ADMIN; DEAD → QUEUED, attempts=0, run_at=now(); audit JOB_RETRY
```

Trang (`st.tabs([t("admin.config"), t("admin.audit"), t("admin.jobs")])`):

| Tab | Nội dung | Quyền |
|---|---|---|
| Cấu hình | Nhóm "Giới hạn" (number_input với min/max theo F-04), "Truy hồi & AI", "Lưu trữ", "Tính năng" (toggle cho `FEATURE_*`). Mỗi khoá có mô tả. Nút "Lưu" theo từng nhóm (`st.form`), hiện thay đổi trước khi lưu | ADMIN sửa; PM chỉ xem (widget `disabled`) |
| Nhật ký | `st.dataframe` audit: thời gian, người (display_name), hành động, đối tượng, metadata; lọc theo hành động/ngày; phân trang | ADMIN, PM |
| Job lỗi | Bảng job DEAD + nút "Chạy lại" từng dòng (`key=f"job.retry:{id}"`), xác nhận trước khi chạy | ADMIN |

- Mọi kiểm tra quyền ở `AdminService`, trang chỉ ẩn/disable thêm. END_USER vào `/admin` (gõ URL) → page không có trong navigation (PLT-07) **và** service ném `Forbidden`.
- Khoá bảo mật (secret) **không** có trong `app_config` nên không hiển thị.
- Optimistic locking bằng `version`: hai admin sửa cùng lúc → người sau nhận thông báo "Cấu hình đã thay đổi, tải lại".

## Tiêu chí xong

- [ ] ADMIN đổi `RATE_LIMIT_ASKS_PER_HOUR` → có audit với giá trị cũ/mới; giới hạn mới có hiệu lực ≤ 30 s.
- [ ] Giá trị ngoài khoảng → báo lỗi, không lưu.
- [ ] PM xem được audit, không sửa được config; END_USER bị chặn.
- [ ] Chạy lại job DEAD → job QUEUED, có audit.

## Test

`tests/integration/admin/test_admin_service.py`; AppTest `tests/unit/ui/test_admin_page.py` (3 role); dòng `config.update`/`audit.list` trong authz matrix.

## Tham chiếu

SADD §5.3.7 (DLQ), §5.7.1, §5.8.3, ADR-011 · F-04, F-05
