# PLT-08 — Schema cơ sở dữ liệu và migration Alembic

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S1, mục 1.1) |
| Sprint | S1 |
| Tầng | DB |
| Ước lượng | 2d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | PLT-04 (role DB), PLT-05 |
| Chặn | F-04, F-07, F-08, mọi repository |

## Bối cảnh

DDL tham chiếu ở SADD §10.1. Alembic là nguồn sự thật; migration phải chạy được trên DB trống và DB có dữ liệu, và có `downgrade`.

## Phạm vi

**Làm:** `alembic init migrations`, `env.py` đọc URL từ env `MIGRATOR_DATABASE_URL`, migration `0001_initial` theo DDL, kèm các sửa lỗi nêu dưới.

**Không làm:** seed `app_config` (F-04 làm migration `0002`), bảng `document_suggestions` (T-18-1).

## Đặc tả

Migration `0001_initial` tạo đúng các bảng/chỉ mục/trigger ở SADD §10.1: extension `vector`, `pgcrypto`, `citext`, `pg_trgm`; bảng `users`, `documents`, `document_chunks`, `conversations`, `messages`, `answers`, `answer_segments`, `citations`, `feedback`, `app_config`, `jobs`, `audit_log`, `telemetry_events`; mọi index (gồm HNSW `m=16, ef_construction=64` và các partial unique); hàm + trigger `touch_updated_at`.

**Sửa so với DDL tham chiếu (bắt buộc):**

| # | Vấn đề trong DDL | Sửa |
|---|---|---|
| 1 | Trigger `trg_documents_touch` cập nhật `updated_at` nhưng bảng `documents` **không có** cột này, nên mọi `UPDATE documents` sẽ lỗi | Thêm `updated_at timestamptz NOT NULL DEFAULT now()` vào `documents` |
| 2 | Khoá chính dùng `gen_random_uuid()` (v4), trong khi SADD §5.4.2 yêu cầu UUIDv7 | Giữ default v4 làm dự phòng; **ứng dụng luôn tự sinh UUIDv7** (F-01 `new_id()`) khi insert |
| 3 | `REVOKE UPDATE, DELETE ON audit_log FROM app_rw` lỗi nếu role chưa tồn tại | Bọc trong `DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname='app_rw') THEN ... END IF; END $$` và cấp `GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES` cho `app_rw` **trước**, rồi mới REVOKE trên `audit_log` |
| 4 | Thiếu chỉ mục cho reaper và tra cứu theo hội thoại | Thêm `ix_jobs_running_locked ON jobs(locked_at) WHERE status='RUNNING'` và `ix_telemetry_event_time ON telemetry_events(event, created_at)` |

Thêm `GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_rw` (cho `bigserial`).

`downgrade()`: drop theo thứ tự ngược phụ thuộc; **không** drop extension (có thể dùng chung).

**Quy ước migration cho cả đội** (ghi vào `migrations/README.md`):
- Đặt tên `NNNN_<mô_tả>.py`, một migration cho một thay đổi logic.
- Theo mô hình expand → migrate → contract; không xoá cột trong cùng release với code ngừng dùng cột đó.
- Không dùng autogenerate mà không review: phải kiểm tra index HNSW và partial index thủ công.

## Tiêu chí xong

- [ ] `alembic upgrade head` trên DB trống thành công; `alembic downgrade base` rồi `upgrade head` lại thành công.
- [ ] `UPDATE documents SET status='READY' WHERE ...` chạy được (xác nhận sửa #1).
- [ ] Với kết nối `app_rw`: `UPDATE audit_log ...` báo lỗi quyền; `INSERT` thành công.
- [ ] `\d document_chunks` có index HNSW `vector_cosine_ops`.

## Test

`tests/integration/db/test_migrations.py` (testcontainers `pgvector/pgvector:pg16`):
- upgrade → downgrade → upgrade.
- Insert một dòng mỗi bảng theo đúng FK; UPDATE `documents` kích hoạt trigger và `updated_at` thay đổi.
- Role `app_rw` không UPDATE/DELETE được `audit_log`.
- Partial unique `ux_documents_owner_checksum`: hai tài liệu chưa xoá cùng `(owner, checksum)` thì lỗi; đặt `deleted_at` cho cái đầu thì cái thứ hai chèn được.

## Tham chiếu

SADD §5.4, §5.4.6, §10.1
