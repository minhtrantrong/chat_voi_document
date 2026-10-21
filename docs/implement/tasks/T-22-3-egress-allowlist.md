# T-22-3 — Egress allowlist cho container ứng dụng

| Thuộc tính | Giá trị |
|---|---|
| Story | US-22 (P0) |
| Sprint | S1 (staging), xác nhận lại ở S5 (production) |
| Tầng | OPS |
| Ước lượng | 0.5d |
| Owner gợi ý | QA/DevOps (phối hợp IT) |
| Phụ thuộc | PLT-04, G-06 |
| Chặn | PLT-14 |

## Bối cảnh

SADD §5.6.3 và §5.8.6: worker chỉ được gọi ra Internet tới domain IdP, LLM, Embedding (và observability nếu ở ngoài). Mọi đích khác bị chặn.

## Phạm vi

**Làm:** cấu hình chặn egress trên VM, tài liệu danh sách domain, test kiểm chứng.

## Đặc tả

Cách làm khuyến nghị (chọn theo hạ tầng IT cho phép):

| Phương án | Mô tả |
|---|---|
| A — Proxy egress | Thêm container `squid` (hoặc proxy của tổ chức) với ACL `dstdomain`; đặt `HTTPS_PROXY` cho `web`/`worker-*`; network `app` không có route trực tiếp ra ngoài (`internal: true`), chỉ `squid` nằm ở network có Internet |
| B — Firewall VM | `nftables`/`ufw` trên VM chặn outbound 443 trừ IP/domain được phép (khó khi provider dùng CDN đổi IP) |

Khuyến nghị **A** vì lọc theo domain.

Allowlist (`deploy/egress/allowlist.txt`):
- Domain IdP (`OIDC_ISSUER` host)
- Domain LLM (`LLM_BASE_URL` host)
- Domain Embedding
- (Tuỳ chọn) registry image, chỉ khi deploy

httpx client trong adapter phải tôn trọng `HTTPS_PROXY` (mặc định có, kiểm tra `trust_env=True`). boto3 tới MinIO nội bộ phải **bỏ qua** proxy (`NO_PROXY=minio,postgres,redis`).

## Tiêu chí xong

- [ ] Từ container `worker-answer`: `curl https://example.com` bị chặn; `curl https://<llm host>` thành công.
- [ ] Web vẫn đăng nhập được (IdP qua proxy), upload được (MinIO không qua proxy).

## Test

`deploy/egress/test_egress.sh` chạy trong container, kiểm tra 2 trường hợp trên; được gọi ở PLT-14.

## Tham chiếu

SADD §5.6.3, §5.8.6 · US-22
