# T-03-3 — UI tài liệu lỗi: chip "Lỗi", lý do, Thử lại / Xoá

| Thuộc tính | Giá trị |
|---|---|
| Story | US-03 (P0) — AC-03.3; US-04 — AC-04.3 |
| Sprint | S2 |
| Tầng | UI |
| Ước lượng | 0.5d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-03-1, T-05-3 (DocumentItem), T-04-6 (retry) |
| Chặn | — |

## Bối cảnh

Thiết kế [05-main-conversation.html](../../design/html_design/05-main-conversation.html): tệp `spec-ky-thuat.pdf` ở cột trái có chip "Lỗi", lý do, "Thử lại" / "Xoá". Quyết định **C-14**: chỉ lỗi tạm thời mới có "Thử lại".

## Phạm vi

**Làm:** nhánh `status == ERROR` trong `document_item` (T-05-3).

## Đặc tả

```python
if d.status == "ERROR":
    st.markdown(f"⚠ **{t('status.error')}**")                 # icon + nhãn (không chỉ màu)
    st.caption(error_text_short(d.error_code))                  # khoá doc.error_short.*
    cols = st.columns(2)
    if d.can_retry and cols[0].button(t("common.retry"), key=f"retry:{d.id}"):
        run_safely(lambda: svc.documents.retry(actor, d.id)); st.rerun()
    if d.can_delete and cols[1].button(t("doc.delete"), key=f"del:{d.id}"):
        open_delete_dialog(d)                                   # T-06-5
```

- Nút "Xoá" gọi dialog của T-06-5 (S4). Trong S2–S3, khi `DocumentService.delete` chưa có, **ẩn** nút Xoá bằng kiểm tra `hasattr`/cờ tạm `docs.delete_enabled`; AC-03.3 chỉ cần chip + lý do, AC-04.3 (nút Xoá) được nghiệm thu lại ở S4.
- `DocumentDTO.can_retry` do service tính: `status == ERROR and error_code in RETRYABLE_DOC_ERRORS and (is_owner or admin)`.
- Checkbox phạm vi (US-13c) bị `disabled` với tài liệu lỗi.
- Retry thành công: chip chuyển "Đang xử lý" ngay sau rerun và fragment poll bắt đầu chạy (T-04-7).

## Tiêu chí xong

- [ ] Tài liệu `PDF_NO_TEXT`: thấy chip Lỗi + lý do + chỉ nút Xoá.
- [ ] Tài liệu `EMBED_FAILED`: có cả Thử lại và Xoá; bấm Thử lại chuyển sang Đang xử lý.

## Test

`tests/unit/ui/test_document_item_error.py` (AppTest với DTO giả).

## Tham chiếu

US-03, US-04 · Blueprint §3.5.3 (StatusChip) · Implement_plan §14 C-14
