# T-13c-3 — Test phạm vi: 100% trích dẫn thuộc tài liệu đã chọn

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13c (P1) — AC-13c.1 |
| Sprint | S3 |
| Tầng | TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | T-13c-2, T-09-1, T-13-3 |
| Chặn | — |

## Bối cảnh

AC-13c.1: chỉ chọn 1 tài liệu làm phạm vi → 100% trích dẫn chỉ trỏ tới tài liệu đó.

## Phạm vi

**Làm:** test integration chạy qua worker thật với FakeEmbedding/FakeLLM.

## Đặc tả

| Test | Dữ liệu | Khẳng định |
|---|---|---|
| `test_scope_single_doc_citations_only_that_doc` | 2 tài liệu cùng chủ đề "hạn chót" (A, B), scope = [A], 10 câu hỏi khác nhau | Mọi citation của mọi câu trả lời có `document_id == A` |
| `test_scope_ignores_foreign_ids` | scope = [A, doc_private_của_user_khác] | Retrieval chỉ dùng A |
| `test_scope_all_deleted_returns_no_ready` | scope = [A], A bị xoá trước khi hỏi | `ask` → `ERR_NO_READY_DOC` |
| `test_scope_empty_means_all` | scope = [] | Có citation từ cả A và B (khi cả hai liên quan) |

## Tiêu chí xong

- [ ] 4 test xanh.

## Tham chiếu

US-13c AC-13c.1
