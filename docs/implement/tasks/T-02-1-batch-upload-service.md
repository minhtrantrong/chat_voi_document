# T-02-1 — Tải lên theo lô: giới hạn số tệp và xử lý song song

| Thuộc tính | Giá trị |
|---|---|
| Story | US-02 — Tải lên nhiều PDF cùng lúc (P1) — AC-02.1, AC-02.2 |
| Sprint | S2 |
| Tầng | APP |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-01-4 |
| Chặn | T-02-2, T-02-3 |

## Bối cảnh

AC-02.1: chọn đúng số tệp tối đa thì tất cả được tiếp nhận. AC-02.2: tệp lỗi không chặn tệp hợp lệ, tối đa 3 tệp song song. Quyết định **C-13**: vượt số tệp tối đa thì từ chối **cả lô**.

## Phạm vi

**Làm:** phần đầu của `DocumentService.upload` (kiểm tra số tệp, chạy song song).

## Đặc tả

```python
def upload(self, actor, files, idempotency_key):
    limits = self._config.limits()
    if len(files) > limits.max_files_per_upload:
        raise Invalid(ErrorCode.ERR_DOC_413, {"max": limits.max_files_per_upload, "actual": len(files)})
    if len(files) == 1:
        return [self._safe_upload_one(actor, files[0], limits)]
    with ThreadPoolExecutor(max_workers=3, thread_name_prefix="upload") as pool:
        return list(pool.map(lambda f: self._safe_upload_one(actor, f, limits), files))   # map giữ thứ tự
```

- `_safe_upload_one` bọc `_upload_one` trong try/except: mọi exception (kể cả không mong đợi) thành `UploadResult(REJECTED, error_code=None, error_params={"corr_id": ...})` và log exception. Không exception nào thoát ra làm hỏng các tệp khác.
- Mỗi luồng dùng UoW riêng (không chia sẻ connection).
- Contextvar `corr_id` phải được copy sang thread (`contextvars.copy_context().run`).
- Chuỗi lỗi cho lô vượt giới hạn: `error.ERR-DOC-413` dạng "Tối đa {max} tệp mỗi lần, bạn đã chọn {actual}" — nếu chuỗi này khác với lỗi "tệp vượt dung lượng" thì dùng khoá riêng `upload.too_many_files`.

## Tiêu chí xong

- [ ] 5 tệp (= tối đa) đều hợp lệ → 5 `ACCEPTED` (AC-02.1).
- [ ] 6 tệp → `Invalid(ERR_DOC_413)`, không tệp nào được lưu.
- [ ] Lô có tệp lỗi → các tệp khác vẫn `ACCEPTED` (AC-02.2).
- [ ] Không bao giờ có hơn 3 upload chạy cùng lúc (kiểm bằng storage giả đếm đồng thời).

## Test

Xem T-02-3; thêm `tests/unit/documents/test_upload_concurrency.py` với storage giả có `sleep`.

## Tham chiếu

US-02 · SADD §5.3.2 · Blueprint §3.8 (Tải lên) · Implement_plan §14 C-13
