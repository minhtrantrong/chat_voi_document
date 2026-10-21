# PLT-11 — Bộ fuzz test cho upload và ingestion

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S2, mục 2.10) |
| Sprint | S2 |
| Tầng | TEST |
| Ước lượng | 1d |
| Owner gợi ý | QA/DevOps |
| Phụ thuộc | T-01-4, T-04-4, F-10 |
| Chặn | PLT-14 |

## Bối cảnh

NFR-SEC-03 và SADD §5.8.7: PDF độc hại không được làm sập `web` hoặc `worker`; job phải kết thúc ở ERROR/DLQ.

## Phạm vi

**Làm:** script sinh corpus, test pytest marker `fuzz`, chạy nightly (PLT-03).

**Không làm:** DAST (PLT-14).

## Đặc tả

`tests/security/fuzz/generate_corpus.py` sinh vào `tests/fixtures/fuzz/` (không commit tệp > 1 MB; tệp lớn sinh lúc chạy):

| Mẫu | Cách tạo | Kết quả mong đợi |
|---|---|---|
| Tệp rỗng 0 byte | `b""` | REJECTED `PDF_NOT_PDF` |
| Chỉ header `%PDF-1.7` | 9 byte | REJECTED `PDF_CORRUPT` |
| PDF cắt cụt 50% | lấy `text.pdf` cắt đôi | REJECTED `PDF_CORRUPT` hoặc ERROR |
| Đuôi `.pdf`, nội dung ZIP/DOCX | đổi tên | REJECTED `PDF_NOT_PDF` |
| PDF có stream nén cực lớn ("zip bomb") | object `FlateDecode` giải nén ra > 2 GB | ERROR trong ≤ 300 s, worker còn sống |
| PDF 10.000 trang rỗng | PyMuPDF `new_page` lặp | REJECTED `PDF_TOO_MANY_PAGES` |
| PDF mã hoá AES-256 | PyMuPDF `save(encryption=...)` | REJECTED `PDF_ENCRYPTED` |
| PDF có JavaScript/Launch action | thêm `/OpenAction` JS | READY bình thường (không thực thi gì) |
| Tên tệp Unicode, emoji, `../../etc/passwd.pdf`, 255 ký tự | đặt `file_name` | Lưu nguyên tên làm metadata; `storage_key` vẫn do hệ thống sinh |
| Trang có 1 triệu ký tự | text dài | READY, chunk đúng giới hạn token |

Test `tests/security/test_upload_fuzz.py` (`@pytest.mark.fuzz`): với từng mẫu gọi `DocumentService.upload`; mẫu được nhận thì chạy handler ingest **thật** qua sandbox; khẳng định:
1. Process test (đóng vai web/worker) không crash.
2. Kết quả khớp cột "mong đợi".
3. Bộ nhớ process cha tăng không quá 200 MB (đo `resource.getrusage`).

## Tiêu chí xong

- [ ] `pytest -m fuzz tests/security` xanh trên Linux CI.
- [ ] Job nightly chạy bộ fuzz và báo kết quả.
- [ ] Mẫu nào gây crash thì phải có bug ticket + fix trước M2.

## Tham chiếu

SADD §5.8.4, §5.8.7, NFR-SEC-03 · F-10
