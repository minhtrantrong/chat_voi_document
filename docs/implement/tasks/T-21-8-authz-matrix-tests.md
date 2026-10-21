# T-21-8 — Authz matrix tự động cho mọi service

| Thuộc tính | Giá trị |
|---|---|
| Story | US-21 (P0) — AC-21.1; cũng phục vụ US-05, US-15, US-23 |
| Sprint | S1 (khung + identity/documents), mở rộng mỗi sprint khi thêm service |
| Tầng | TEST |
| Ước lượng | 1.5d (khung 1d + mở rộng 0.5d rải các sprint) |
| Owner gợi ý | QA/DevOps + Backend 2 |
| Phụ thuộc | T-21-3, F-07 |
| Chặn | PLT-14 |

## Bối cảnh

AC-21.1: người không được cấp quyền gọi trực tiếp service thì **0 truy cập thành công**. QA-06: người dùng A đoán `docId` của B thì 403/404. Kiểm tra quyền phải nằm ở application service (SADD §5.8.3), nên test gọi thẳng service, không qua UI.

## Phạm vi

**Làm:** `tests/security/test_authz_matrix.py`, fixture tạo dữ liệu chuẩn, test "mọi method public nhận Actor".

## Đặc tả

Fixture `authz_world` (integration, DB thật):

| Thực thể | Chủ | Ghi chú |
|---|---|---|
| `doc_a_private` | user A (END_USER) | PRIVATE, READY |
| `doc_b_private` | user B (END_USER) | PRIVATE, READY |
| `doc_b_shared` | user B | SHARED, READY |
| `doc_b_deleted` | user B | SHARED, DELETING |
| `conv_a`, `answer_a` | user A | có citation tới `doc_a_private` |
| `conv_b`, `answer_b` | user B | |

Ma trận (tham số hoá `pytest.mark.parametrize`), đối chiếu SADD §5.8.3 và C-11:

| Hành động | A trên tài nguyên của A | A trên private của B | A trên shared của B | A trên deleted | PM | ADMIN trên private của B |
|---|---|---|---|---|---|---|
| `documents.get` | OK | NotFound | OK | NotFound | như END_USER | OK + audit `document.view_other` |
| `documents.list` chứa | có | không | có | không | như END_USER | không (C-11) |
| `documents.delete` | OK | NotFound | Forbidden | NotFound | như END_USER | OK + audit `admin_override` |
| `documents.retry` | OK (khi ERROR) | NotFound | Forbidden | NotFound | như END_USER | OK |
| `documents.render_page` | OK | NotFound | OK | NotFound | như END_USER | OK + audit |
| `qa.ask` scope chứa id | OK | id bị bỏ khỏi scope | OK | id bị bỏ | — | — |
| `qa.get_answer / read_tokens / cancel` | OK | — | — | — | NotFound với answer của B | NotFound với answer của B |
| `conversations.get` | OK | — | — | — | NotFound với hội thoại của B | NotFound (SADD: không xem hội thoại người khác) |
| `feedback.upsert` trên answer B | — | — | — | — | NotFound | NotFound |
| `config.update` | Forbidden | — | — | — | Forbidden | OK |
| `audit.list` | Forbidden | — | — | — | OK | OK |

Test bổ sung:
- `test_every_public_service_method_takes_actor_first`: duyệt `Services` (F-11), với mỗi method public (không bắt đầu bằng `_`) kiểm tra tham số đầu tiên sau `self` có annotation `Actor` (danh sách ngoại lệ rõ ràng, ví dụ `IdentityService.resolve_actor`).
- `test_admin_reads_other_private_are_audited`.

Khi một service mới được thêm ở sprint sau, owner của service đó **phải** bổ sung dòng vào ma trận (ghi vào DoD của task đó).

## Tiêu chí xong

- [ ] Mọi ô có giá trị trong ma trận là một test case; 100% xanh.
- [ ] Test "Actor đầu tiên" xanh.
- [ ] Chạy trong job `integration` của CI.

## Tham chiếu

SADD §5.8.3, §7.2 QA-06, §7.4 · US-21 AC-21.1 · Implement_plan §14 C-11
