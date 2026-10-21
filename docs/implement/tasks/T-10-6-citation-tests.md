# T-10-6 — Test invariant citation và chỉ số citation precision

| Thuộc tính | Giá trị |
|---|---|
| Story | US-10 (P0) — AC-10.1, AC-10.2 |
| Sprint | S3 |
| Tầng | TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | AI/Backend |
| Phụ thuộc | T-13-3 (finalize), T-12-3 (chỉ số eval) |
| Chặn | — |

## Bối cảnh

AC-10.1: 100% đoạn thông tin có trích dẫn. AC-10.2: trích dẫn trỏ đúng tài liệu và trang (≥ MET-003). Invariant SADD §5.4.5: `Answer.ANSWERED ⇒ ≥ 1 citation`.

## Phạm vi

**Làm:** test integration trên luồng thật (worker + FakeLLM) và bảo đảm chỉ số eval được tính.

## Đặc tả

| Test | Cách làm | Khẳng định |
|---|---|---|
| `test_answered_has_citation_on_every_informative_segment` | FakeLLM `echo_sources` trả 2 đoạn, mỗi đoạn một marker | Mọi segment `cited=True`, mỗi segment ≥ 1 citation |
| `test_invalid_marker_dropped` | FakeLLM trả `[S9]` không tồn tại + `[S1]` | Chỉ citation của S1 được lưu |
| `test_no_marker_retry_then_not_found` | FakeLLM `no_markers` cả hai lần | outcome NOT_FOUND, `error_code=CITATION_INVALID`, 0 citation, stream có sự kiện `reset` |
| `test_citation_page_matches_chunk` | tài liệu `text.pdf`, câu hỏi về ngày ở trang 2 | citation `page == 2`, `quote` chứa "30/11/2026" |
| `test_db_invariant_answered_has_citation` | truy vấn sau mọi test | `SELECT ... ANSWERED không có citation` trả 0 dòng |

Eval (T-12-3) tính `citation_precision` = số citation khớp `expected_citations` (cùng file, cùng trang) / tổng citation; mục tiêu ≥ MET-003 ở PLT-16.

## Tiêu chí xong

- [ ] 5 test xanh trong CI.

## Tham chiếu

US-10 · SADD §5.4.5 · T-12-3
