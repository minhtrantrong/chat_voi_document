# T-20-1 — Rà soát điểm phát sự kiện telemetry

| Thuộc tính | Giá trị |
|---|---|
| Story | US-20 — Biết mỗi người đặt bao nhiêu câu hỏi mỗi tuần (P0) |
| Sprint | S3 (rà soát lần 1), S4 (lần 2 khi đủ tính năng) |
| Tầng | APP / TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 2 |
| Phụ thuộc | F-06; các task phát sự kiện |
| Chặn | T-20-4 |

## Bối cảnh

Sự kiện được phát rải rác trong nhiều task. Task này bảo đảm **đủ** và **đúng** theo bảng ở F-06 / Implement_plan §20.

## Phạm vi

**Làm:** checklist + test tự động "mỗi sự kiện được phát ở luồng tương ứng".

## Đặc tả

| Sự kiện | Phát ở task | Kiểm tra |
|---|---|---|
| `question_submitted` | T-07-2 | 1 lần mỗi `ask` thành công, có `answer_id` |
| `answer_first_token` | T-13-3 | 1 lần khi có token đầu |
| `answer_completed` | T-13-3, T-11-1 | ANSWERED/NOT_FOUND/ABORTED |
| `answer_stopped` | T-13-5 | mỗi lần cancel |
| `answer_error` | T-13-3, T-13-8 | ERROR |
| `citation_clicked` | T-13d-4 | lần mở đầu từ chip |
| `feedback_submitted` | T-19-1 | mỗi upsert |
| `document_uploaded` / `document_ready` / `document_failed` / `document_deleted` | T-01-4, T-04-4, T-06-2 | — |

Test `tests/integration/telemetry/test_event_coverage.py`: chạy luồng đầy đủ (upload → ready → ask → stream → cancel một câu → feedback → delete) với Fake providers, đếm sự kiện theo loại, so với số mong đợi; kiểm tra không sự kiện nào có prop ngoài whitelist.

## Tiêu chí xong

- [ ] Test xanh; bảng trên được đánh dấu đủ.

## Tham chiếu

US-20 · F-06 · Blueprint §3.7.2
