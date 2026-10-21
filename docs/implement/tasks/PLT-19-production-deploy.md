# PLT-19 — Triển khai staging/production: blue/green và rollback

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S5, mục 5.9) |
| Sprint | S5 (bản staging tự động: S1) |
| Tầng | OPS |
| Ước lượng | 2d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | PLT-03, PLT-04, PLT-06 |
| Chặn | M5, go-live |

## Bối cảnh

SADD §5.5.4 và §5.6.7: image bất biến theo SHA, migration chạy trước và backward-compatible, blue/green bằng hai bộ container sau Caddy, rollback bằng chuyển traffic.

## Phạm vi

**Làm:**
- S1: workflow deploy staging tự động sau khi merge `main` (pull image + `compose up`).
- S5: `deploy/deploy.sh`, `deploy/rollback.sh`, cấu hình Caddy cho hai upstream, smoke test, bước phê duyệt thủ công cho production.

## Đặc tả

`deploy/compose.prod.yaml` định nghĩa hai nhóm `blue` và `green` (`web-blue`, `worker-answer-blue`, `worker-ingest-blue`; tương tự `-green`), dùng chung `postgres/redis/minio`.

`deploy/deploy.sh <sha>`:

```text
1. Xác định màu đang chạy (đọc deploy/active_color) → màu mới = màu còn lại
2. docker pull registry/cvd-app:<sha>
3. Chạy migrate: docker compose run --rm migrate (image mới). Lỗi → dừng, KHÔNG đổi traffic
4. TAG=<sha> docker compose up -d web-<new> worker-answer-<new> worker-ingest-<new>
5. Chờ /readyz và /_stcore/health của màu mới OK (timeout 120 s)
6. Smoke: deploy/smoke.sh --target <new> (đăng nhập bằng user test, upload PDF nhỏ, hỏi 1 câu với FakeLLM nếu staging)
7. Đổi upstream Caddy (caddy reload với file sinh từ template) → ghi active_color
8. Dừng worker màu cũ (để không claim job), giữ web màu cũ 24 h
```

Lưu ý worker: hai bộ worker cùng chạy trong một thời gian ngắn là an toàn vì job queue dùng `SKIP LOCKED`; nhưng **migration phải backward-compatible** để worker cũ không lỗi.

`deploy/rollback.sh`: đổi Caddy về màu cũ, khởi động lại worker màu cũ, dừng màu mới. Không rollback DB (migration là expand-only); nếu migration hỏng dữ liệu thì theo RUN-02 + restore (PLT-18).

Phiên Streamlit đang mở sẽ mất khi đổi màu (websocket ngắt) → deploy production ngoài giờ hành chính, có thông báo trước.

## Tiêu chí xong

- [ ] Staging tự cập nhật sau mỗi merge `main` trong ≤ 10 phút.
- [ ] Diễn tập trên staging: deploy SHA mới → rollback → deploy lại, không mất dữ liệu, không job nào kẹt.
- [ ] Production yêu cầu phê duyệt thủ công (GitHub Environments) trước bước 3.

## Tham chiếu

SADD §5.5.4, §5.6.7, ADR-012
