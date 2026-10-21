# PLT-14 — Kiểm thử bảo mật trước release

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S5, mục 5.3) |
| Sprint | S5 |
| Tầng | TEST / OPS |
| Ước lượng | 2d |
| Owner gợi ý | QA/DevOps + Tech Lead |
| Phụ thuộc | T-21-8 (authz matrix), PLT-11 (fuzz), T-12-6 (prompt injection), T-22-3, T-22-4 |
| Chặn | M5 |

## Bối cảnh

Điều kiện release: 0 lỗi Critical/High (SADD §5.8.7, §10.6). Task này tổng hợp các kiểm thử bảo mật và chạy thêm DAST/SAST.

## Phạm vi

**Làm:** ZAP baseline trên staging, Semgrep SAST, Trivy image + fs, `pip-audit`, kiểm tra header/cookie, rà soát STRIDE, tổng hợp báo cáo.

**Không làm:** viết lại authz matrix, fuzz, prompt injection (đã có task riêng; ở đây chỉ chạy và đưa vào báo cáo).

## Đặc tả

| Hạng mục | Công cụ / cách làm | Ngưỡng đạt |
|---|---|---|
| DAST | `zap-baseline.py -t https://staging… -c deploy/security/zap.conf` (đăng nhập bằng script Playwright để lấy cookie) | 0 High; Medium phải có giải trình |
| SAST | `semgrep --config p/python --config p/secrets` + `ruff` rule `S` | 0 finding mức ERROR chưa xử lý |
| Image / dependency | `trivy image`, `trivy fs`, `pip-audit --strict` | 0 Critical/High |
| Header | `curl -I`: HSTS, `X-Content-Type-Options`, `Referrer-Policy`, CSP `frame-ancestors 'none'` | Đủ |
| Cookie | Trình duyệt dev tools: cookie phiên `Secure`, `HttpOnly`, `SameSite=Lax` | Đủ |
| XSRF | Gửi request websocket/upload không có token XSRF | Bị từ chối |
| Authz matrix | `pytest tests/security/test_authz_matrix.py` | 100% |
| Fuzz | `pytest -m fuzz` | 100% |
| Prompt injection | `python -m app.eval run --only injection` | 0 lần lộ system prompt / làm theo chỉ dẫn |
| Log nội dung | T-22-4 (canary) | 0 lần xuất hiện |
| Egress | T-22-3 | Domain ngoài allowlist bị chặn |
| Bí mật trong repo | `gitleaks detect` | 0 |

Rà soát STRIDE: đối chiếu từng dòng SADD §5.8.1 với bằng chứng (test/config), ghi vào báo cáo.

Báo cáo: `docs/security/security_test_report_<date>.md` gồm bảng trên, finding, quyết định xử lý, người duyệt (Security).

## Tiêu chí xong

- [ ] Báo cáo hoàn chỉnh, Security ký duyệt.
- [ ] Mọi Critical/High đã sửa và chạy lại xác nhận.

## Tham chiếu

SADD §5.8, §10.6 · OWASP ASVS 4.0
