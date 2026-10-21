# T-05-4 — Test phân quyền cho danh sách và chi tiết tài liệu

| Thuộc tính | Giá trị |
|---|---|
| Story | US-05 (P0) — AC-05.2 |
| Sprint | S2 |
| Tầng | TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | T-05-2, T-21-8 (khung matrix) |
| Chặn | — |

## Bối cảnh

Bổ sung các dòng `documents.list` / `documents.get` vào authz matrix và test riêng cho AC-05.2.

## Phạm vi

**Làm:** test trong `tests/security/test_authz_matrix.py` + `tests/integration/documents/test_list_visibility.py`.

## Đặc tả

| Test | Khẳng định |
|---|---|
| `test_list_hides_other_users_private` | A không thấy `doc_b_private` |
| `test_list_shows_shared` | A thấy `doc_b_shared` |
| `test_list_hides_deleting` | Không ai thấy `doc_b_deleted` |
| `test_get_other_private_not_found` | `documents.get(A, doc_b_private)` → `NotFound` (không phải `Forbidden`) |
| `test_admin_get_other_private_audited` | ADMIN `get` → OK + 1 dòng audit `document.view_other` |
| `test_admin_list_same_as_user` | Danh sách chính của ADMIN không chứa private của B (C-11) |
| `test_list_does_not_leak_count` | Tổng số trang/next_cursor không phụ thuộc tài liệu private của người khác |

## Tiêu chí xong

- [ ] 7 test xanh.

## Tham chiếu

US-05 · SADD §5.8.3 · T-21-8
