# T-23-1 — Job `integrity.check` hằng ngày

| Thuộc tính | Giá trị |
|---|---|
| Story | US-23 — Dữ liệu đã xoá không còn bị dùng (P0); SADD §5.4.5 |
| Sprint | S4 |
| Tầng | WRK |
| Ước lượng | 0.75d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | F-08, F-09, PLT-12 (lịch), PLT-06 (metric) |
| Chặn | PLT-17 (alert IntegrityViolation) |

## Bối cảnh

SADD §5.4.5: kiểm tra định kỳ document READY không có chunk, answer ANSWERED không có citation, citation trỏ document không tồn tại. Bổ sung kiểm tra liên quan xoá để bảo đảm US-23.

## Phạm vi

**Làm:** handler `@handles("integrity.check")`, payload `{"runDate": ...}`, max_attempts 1.

## Đặc tả

| Check | SQL (đếm) | Ý nghĩa |
|---|---|---|
| `ready_without_chunks` | `SELECT count(*) FROM documents d WHERE d.status='READY' AND NOT EXISTS (SELECT 1 FROM document_chunks c WHERE c.document_id=d.id)` | Vi phạm invariant READY ⇒ ≥ 1 chunk |
| `answered_without_citation` | `SELECT count(*) FROM answers a WHERE a.outcome='ANSWERED' AND NOT EXISTS (SELECT 1 FROM answer_segments s JOIN citations c ON c.segment_id=s.id WHERE s.answer_id=a.id)` | Vi phạm DR-02 |
| `chunks_of_deleted_docs` | `SELECT count(*) FROM document_chunks c JOIN documents d ON d.id=c.document_id WHERE d.deleted_at IS NOT NULL AND d.status='DELETED'` | Purge sót |
| `deleting_stuck` | `SELECT count(*) FROM documents WHERE status='DELETING' AND deleted_at < now() - interval '24 hours'` | Purge kẹt |
| `citation_flag_lag` | `SELECT count(*) FROM citations c JOIN documents d ON d.id=c.document_id WHERE d.status='DELETED' AND c.deleted=false` | Purge chưa đánh dấu citation |
| `pending_answers_stale` | `SELECT count(*) FROM answers WHERE outcome='PENDING' AND created_at < now() - interval '1 hour'` | Reaper không kết thúc answer |

- Mỗi check ghi `INTEGRITY_VIOLATIONS.labels(check).set(n)`; `n > 0` thì log error `integrity_violation check=… count=…` (không log ID cụ thể quá 20 cái).
- Không tự sửa dữ liệu (chỉ phát hiện); runbook RUN-04 hướng dẫn xử lý.
- Metric gauge chỉ có ý nghĩa trong process worker-ingest; Prometheus scrape :9103.

## Tiêu chí xong

- [ ] Tạo dữ liệu lỗi giả cho từng check → gauge tương ứng > 0.
- [ ] DB sạch → mọi gauge = 0.

## Test

`tests/integration/jobs/test_integrity_check.py`.

## Tham chiếu

SADD §5.4.5, §5.7.4 · US-23
