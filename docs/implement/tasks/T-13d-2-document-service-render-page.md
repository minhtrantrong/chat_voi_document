# T-13d-2 — `DocumentService.render_page`: kiểm tra quyền và cache

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13d (P1) — AC-13d.1, AC-13d.2 |
| Sprint | S4 |
| Tầng | APP |
| Ước lượng | 1d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-13d-1, T-05-1, T-01-1, F-05 |
| Chặn | T-13d-3, T-13d-4 |

## Bối cảnh

ADR-008: object private, app làm proxy; mỗi lần xem đều kiểm tra quyền. SADD §5.3.5: cache ảnh theo `(document_id, page, document_version)` tối đa 30 phút, chỉ trong process; không cache cross-user nếu private — được giải quyết bằng cách **luôn kiểm tra quyền trước khi tra cache**.

## Phạm vi

**Làm:** method `render_page(actor, doc_id, page, quote=None) -> PageImage`; cache tệp PDF trên đĩa và cache PNG trong bộ nhớ.

## Đặc tả

```python
@dataclass(frozen=True)
class PageImage:
    png: bytes; page: int; page_count: int; file_name: str

def render_page(self, actor, doc_id, page, quote=None) -> PageImage:
    with self._uow() as tx:
        doc = self._repo.get(tx, doc_id)
        if doc is None or not self._policy.can_view(actor, doc) or doc.status != READY:
            raise NotFound(ERR_DOC_404)                        # không quyền / đã xoá / chưa READY: như nhau
        if self._policy.needs_admin_audit(actor, doc):
            self._audit.record(tx, actor, DOCUMENT_VIEW_OTHER, "document", doc_id, {"page": page})
    if not 1 <= page <= (doc.page_count or 0): raise Invalid(ERR_DOC_422, {"reason": "page_out_of_range"})
    key = (doc.id, doc.version, page, sha1(quote or ""))
    if (png := self._png_cache.get(key)) is None:
        path = self._pdf_cache.get_or_fetch(doc.id, doc.version, doc.storage_key)   # tải từ S3 nếu chưa có
        png = self._pdf.render_page(path, page, quote)
        self._png_cache.put(key, png)
    self._telemetry.emit("citation_clicked", actor.user_id, page=page)              # xem T-13d-4
    return PageImage(png, page, doc.page_count, doc.file_name)
```

Cache:

| Cache | Nơi | Khoá | Giới hạn |
|---|---|---|---|
| `PdfFileCache` | `/tmp/cvd-cache/{doc_id}-{version}.pdf` | `(doc_id, version)` | LRU tổng 1 GB, TTL 30 phút, xoá khi hết hạn |
| `PngCache` | bộ nhớ process (`cachetools.TTLCache`) | `(doc_id, version, page, sha1(quote))` | 200 mục, TTL 30 phút |

- Tải PDF về cache bằng `get_to_tempfile` rồi `rename` nguyên tử (tránh hai thread cùng tải ghi đè nhau; dùng `threading.Lock` theo khoá).
- Dữ liệu ảnh **không** bao giờ được phục vụ qua URL công khai; UI nhận bytes và `st.image` nhúng trực tiếp.
- Tài liệu DELETING thì bản PDF trong cache vẫn có thể còn trên đĩa của container `web` tới khi hết TTL (purge chạy ở container worker nên không xoá được), nhưng không thể truy cập vì kiểm tra quyền và `deleted_at` chạy trước. Thêm một thread dọn cache mỗi 5 phút xoá tệp quá TTL. Dữ liệu này nằm trên volume tạm không backup.

## Tiêu chí xong

- [ ] Lần xem thứ hai cùng trang không tải S3, không render lại.
- [ ] Tài liệu vừa xoá mềm → `NotFound` ngay cả khi đã có trong cache.
- [ ] Trang 0 hoặc > page_count → `Invalid`.

## Test

`tests/integration/documents/test_render_page.py`; dòng `render_page` trong authz matrix (T-21-8).

## Tham chiếu

ADR-008 · SADD §5.3.5 · US-13d · TD-06
