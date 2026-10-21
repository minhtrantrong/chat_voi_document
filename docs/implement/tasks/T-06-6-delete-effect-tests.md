# T-06-6 — Test hiệu lực xoá với hỏi đáp (AC-06.2)

| Thuộc tính | Giá trị |
|---|---|
| Story | US-06 (P0) — AC-06.1, AC-06.2; US-23 |
| Sprint | S4 |
| Tầng | TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | T-06-2, T-06-3, T-13-3 |
| Chặn | — |

## Bối cảnh

AC-06.2: sau khi xoá, câu hỏi từng được trả lời từ tài liệu đó **không** chứa thông tin hay trích dẫn từ tài liệu đã xoá — phải đúng **ngay sau commit**, kể cả khi purge chưa chạy.

## Phạm vi

**Làm:** `tests/integration/qa/test_deleted_doc_not_retrieved.py`, `tests/integration/documents/test_delete_visibility.py`.

## Đặc tả

| Test | Bước | Khẳng định |
|---|---|---|
| `test_deleted_doc_not_retrieved_before_purge` | Tài liệu X chứa "Mã dự án là ZETA-4421" → hỏi → có citation tới X → xoá X → **không chạy worker purge** → hỏi lại | outcome NOT_FOUND hoặc ANSWERED không có citation tới X; câu trả lời không chứa "ZETA-4421" (FakeLLM `echo_sources` chỉ có thể nói điều có trong context) |
| `test_deleted_doc_not_retrieved_after_purge` | như trên nhưng chạy purge | như trên + 0 chunk của X |
| `test_delete_hides_from_all_lists` | A chia sẻ X; B thấy X; A xoá X | `list(B)` không có X |
| `test_old_answer_citation_marked_deleted` | sau khi xoá | `get_answer(answer cũ)` có citation `deleted=True`, text câu trả lời cũ giữ nguyên |
| `test_reupload_after_delete` | xoá X rồi upload lại đúng tệp | tạo tài liệu mới (partial unique cho phép) |

## Tiêu chí xong

- [ ] 5 test xanh.

## Tham chiếu

US-06 AC-06.2 · SADD §5.3.6 (Hiệu lực tức thời) · BRU-006
