# S-02 — Qdrant bằng Docker Compose

| Thuộc tính | Giá trị |
|---|---|
| Story | Nền tảng |
| Phase | P0 |
| Tầng | INFRA |
| Ước lượng | 0,25d |
| Phụ thuộc | S-01 |
| Chặn | S-05, S-10, S-23 |
| Owner gợi ý | Backend/DevOps |

## 1. Mục tiêu

Có Qdrant chạy local bằng một lệnh, dữ liệu vector được giữ qua restart nhờ Docker volume, và có healthcheck để app biết Qdrant sẵn sàng.

## 2. Phạm vi

**Làm:**

- `docker-compose.yml` với service `qdrant`.
- Port `6333` (HTTP/REST) và `6334` (gRPC).
- Volume `qdrant_data`.
- Healthcheck dùng endpoint `/healthz`.
- README ghi lệnh `docker compose up -d`, `down`, `logs`.

**Không làm:**

- Chưa tạo collection (S-05).
- Chưa cấu hình auth/TLS cho Qdrant.
- Chưa deploy production.

## 3. File chính

```text
docker-compose.yml
```

## 4. Đặc tả

```yaml
services:
  qdrant:
    image: qdrant/qdrant:v1.12.4
    container_name: chat-voi-document-qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD-SHELL", "bash -c ':> /dev/tcp/127.0.0.1/6333' || exit 1"]
      interval: 10s
      timeout: 3s
      retries: 5
      start_period: 10s

volumes:
  qdrant_data:
```

> Nếu image không có `bash`, thay healthcheck bằng `wget -qO- http://localhost:6333/healthz` hoặc bỏ healthcheck và dùng `curl` từ host. Kiểm tra lại sau khi pull image.

### 4.1 Lệnh vận hành

```bash
docker compose up -d
docker compose ps
docker compose logs -f qdrant
curl -s http://localhost:6333/healthz
# Dashboard: http://localhost:6333/dashboard
docker compose down          # giữ volume
docker compose down -v       # XOÁ dữ liệu vector
```

## 5. Trường hợp biên

- Port 6333/6334 bị chiếm → đổi mapping hoặc dừng service đang dùng; README ghi cách kiểm tra.
- Docker chưa chạy → lệnh báo lỗi rõ.
- Volume cũ có collection sai dimension → S-05 báo lỗi và hướng dẫn xoá/recreate.
- `down -v` xoá dữ liệu → README cảnh báo rõ.
- Máy không có Docker → ghi phương án chạy Qdrant binary/cloud (ngoài phạm vi task).

## 6. Tiêu chí xong

- [ ] `docker compose up -d` chạy service `healthy`.
- [ ] `curl http://localhost:6333/healthz` trả 200.
- [ ] Dashboard mở được.
- [ ] Restart container → volume vẫn còn (kiểm tra sau khi S-05 tạo collection).
- [ ] `docker compose down` không xoá volume.
- [ ] README có cảnh báo `down -v`.

## 7. Test

| Test | Cách kiểm |
|---|---|
| Health | `curl -f http://localhost:6333/healthz` |
| Volume | Tạo collection ở S-05, `docker compose restart`, collection vẫn còn |
| Port conflict | Chạy 2 instance → instance thứ hai báo lỗi bind port |

## 8. Tham chiếu

- Kế hoạch §3.2, §5.2, §11.
- S-05, S-10, S-23.
