# T-02-3 — Test tích hợp cho tải lên theo lô

| Thuộc tính | Giá trị |
|---|---|
| Story | US-02 (P1) — AC-02.1, AC-02.2 |
| Sprint | S2 |
| Tầng | TEST |
| Ước lượng | 0.5d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | T-02-1, T-03-4 (fixture PDF) |
| Chặn | — |

## Bối cảnh

Chứng minh AC của US-02 bằng test tự động chạy trên DB/MinIO thật (testcontainers).

## Phạm vi

**Làm:** `tests/integration/documents/test_batch_upload.py`.

## Đặc tả

| Test | Dữ liệu | Khẳng định |
|---|---|---|
| `test_batch_at_max_all_accepted` | 5 PDF hợp lệ khác nhau | 5 ACCEPTED; 5 bản ghi; 5 job; 5 object |
| `test_batch_with_invalid_does_not_block_valid` | `text.pdf`, `text2.pdf`, `fake.docx`, `encrypted.pdf`, `text.pdf` (bản sao) | 2 ACCEPTED, 2 REJECTED (`PDF_NOT_PDF`, `PDF_ENCRYPTED`), 1 DUPLICATE; thứ tự kết quả trùng thứ tự đầu vào |
| `test_batch_over_max_rejected_whole` | 6 PDF | `Invalid(ERR_DOC_413)`; 0 bản ghi, 0 object |
| `test_batch_storage_fail_one_file` | storage giả lỗi ở tệp thứ 2 | tệp 1, 3 ACCEPTED; tệp 2 REJECTED với `corr_id` |

## Tiêu chí xong

- [ ] 4 test xanh trong CI job `integration`.

## Tham chiếu

US-02 · T-02-1
