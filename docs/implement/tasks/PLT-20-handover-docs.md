# PLT-20 — Tài liệu bàn giao vận hành và người dùng

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S5, mục 5.10) |
| Sprint | S5 |
| Tầng | OPS / Tài liệu |
| Ước lượng | 1.5d |
| Owner gợi ý | Tech Lead (điều phối), mỗi owner module viết phần của mình |
| Phụ thuộc | PLT-17, PLT-18, PLT-19 |
| Chặn | Go-live |

## Bối cảnh

SADD §9.3 và §10.6 yêu cầu tài liệu vận hành bàn giao cho Ops và tài liệu SADD/ADR cập nhật theo thực tế triển khai.

## Phạm vi

**Làm:**

| Tài liệu | Nội dung | Người viết |
|---|---|---|
| `README.md` | Chạy local, cấu trúc repo, quy tắc code, chạy test, eval | Tech Lead |
| `docs/ops/environment.md` | Bảng biến môi trường + khoá `app_config` + ý nghĩa + giá trị production | Backend 2 |
| `docs/ops/operations.md` | Kiến trúc triển khai thực tế, port, deploy/rollback, backup/restore, xoay secret 90 ngày | QA/DevOps |
| `docs/runbooks/*` | (từ PLT-17) | QA/DevOps |
| `docs/user/huong_dan_su_dung.md` | Hướng dẫn người dùng 1–2 trang có ảnh: tải lên, hỏi, kiểm tra trích dẫn, đánh giá, giới hạn | Backend 1 + PO |
| SADD | Cập nhật: C-01…C-18, mã lỗi mới (C-16), sửa DDL (PLT-08), đánh dấu sơ đồ 4+1 là "reference" (§10.7) | Tech Lead |

## Tiêu chí xong

- [ ] Một người Ops không tham gia dự án làm theo `operations.md` deploy được bản staging và restore được backup.
- [ ] Một người dùng thử làm theo hướng dẫn hoàn thành luồng hỏi đáp mà không cần hỏi thêm.
- [ ] SADD có mục lịch sử phiên bản mới.

## Tham chiếu

SADD §9.3, §10.6, §10.7
