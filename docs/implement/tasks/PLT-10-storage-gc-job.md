# PLT-10 — Job `storage.gc`: dọn object mồ côi trong storage

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S2, mục 2.9) |
| Sprint | S2 |
| Tầng | WRK |
| Ước lượng | 0.75d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-01-1, F-08, F-09, PLT-12 (lịch chạy) |
| Chặn | — |

## Bối cảnh

Trong luồng upload (T-01-4), object được `put` **trước** transaction. Nếu transaction lỗi hoặc thua race checksum thì object bị mồ côi (SADD §5.3.2). Job này dọn chúng.

## Phạm vi

**Làm:** handler `storage.gc` với payload `{"olderThanHours": 24, "runDate": "YYYY-MM-DD"}`, đăng ký vào `HANDLERS`, max_attempts 2.

**Không làm:** xoá object của tài liệu đã DELETED (purge T-06-3 làm việc đó; GC chỉ là lưới an toàn).

## Đặc tả

```text
handler storage.gc(job):
  cutoff = clock.now() - hours(payload.olderThanHours)
  for page in storage.list(prefix="documents/", page_size=1000):     # list_objects_v2, có ContinuationToken
      candidates = [o for o in page if o.last_modified < cutoff]
      ids = [parse_doc_id(o.key) for o in candidates]                # "documents/{uuid}/original.pdf"
      known = docs_repo.storage_keys_present(ids)                    # tập key có trong documents với status <> 'DELETED'
      for o in candidates:
          if o.key not in known:
              storage.delete(o.key); deleted += 1
  log.info("storage_gc_done", scanned=..., deleted=...)
```

- Thêm `list(prefix, page_size) -> Iterator[list[ObjectInfo(key, last_modified, size)]]` vào `ObjectStoragePort` (bổ sung cho T-01-1).
- Key không đúng định dạng thì **bỏ qua và log warn**, không xoá.
- Giới hạn xoá tối đa 1.000 object mỗi lần chạy (an toàn khi có lỗi logic); vượt thì log warn để người vận hành xem.

## Tiêu chí xong

- [ ] Object mồ côi cũ hơn 24 h bị xoá; object mồ côi mới hơn 24 h được giữ.
- [ ] Object của tài liệu PROCESSING/READY/ERROR/DELETING không bao giờ bị xoá.
- [ ] Chạy lại cùng `runDate` không gây lỗi (idempotent).

## Test

`tests/integration/jobs/test_storage_gc.py` (MinIO testcontainer, Clock giả): tạo 4 object (mồ côi cũ, mồ côi mới, của tài liệu READY, của tài liệu DELETED cũ), chạy job, kiểm tra còn lại đúng 2 object đầu tiên không bị xoá sai.

## Tham chiếu

SADD §5.3.2 (ghi chú), §5.7.4
