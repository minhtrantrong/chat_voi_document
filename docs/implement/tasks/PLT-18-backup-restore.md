# PLT-18 — Backup, restore và diễn tập khôi phục

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S5, mục 5.8) |
| Sprint | S5 |
| Tầng | OPS |
| Ước lượng | 1.5d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | PLT-04 |
| Chặn | M5 |

## Bối cảnh

SADD §5.6.6: `pg_dump` hằng ngày 02:00 giữ 14 bản, MinIO mirror hằng ngày, backup mã hoá AES-256, RPO ≤ 24 h, RTO ≤ 4 h, diễn tập mỗi quý.

## Phạm vi

**Làm:** service `backup` trong compose, script backup/restore, mã hoá, metric thành công, diễn tập lần đầu có biên bản.

## Đặc tả

`deploy/backup/backup.sh` (chạy bằng cron trong container `postgres:16` + `mc`):

```text
1. ts=$(date +%Y%m%dT%H%M)
2. pg_dump -Fc -h postgres -U backup_ro cvd > /backups/db_$ts.dump
3. age -r "$BACKUP_PUBLIC_KEY" -o /backups/db_$ts.dump.age /backups/db_$ts.dump && rm db_$ts.dump
4. mc mirror --overwrite --remove local/cvd-documents backup-target/cvd-documents-mirror
5. Xoá bản .age cũ hơn 14 ngày
6. Ghi metric cvd_backup_last_success_timestamp (textfile collector) chỉ khi mọi bước thành công
```

- Khoá riêng `age` **không** nằm trên VM; lưu ở secret manager của Security.
- Đích backup ở ổ/bucket khác VM (theo hạ tầng G-06).
- Bật versioning cho bucket MinIO chính.

`deploy/backup/restore.sh <dump.age>`: giải mã → `createdb cvd_restore` → `pg_restore -d cvd_restore` → `alembic current` kiểm tra version → mirror ngược object về bucket restore → chạy `integrity.check` trên DB restore.

Diễn tập (ghi `docs/runbooks/restore_drill_<date>.md`): restore sang VM/DB mới, trỏ một instance web vào, đăng nhập, mở hội thoại cũ, bấm citation mở trang PDF. Đo thời gian từ lúc bắt đầu tới khi web dùng được.

## Tiêu chí xong

- [ ] Backup chạy tự động 3 ngày liên tiếp trên staging, metric thành công được cập nhật.
- [ ] Diễn tập restore thành công, RTO đo được ≤ 4 h, có biên bản.
- [ ] Mở thử tệp backup mà không có khoá: không đọc được.

## Tham chiếu

SADD §5.6.6, RUN-07 · NFR-OPS-02
