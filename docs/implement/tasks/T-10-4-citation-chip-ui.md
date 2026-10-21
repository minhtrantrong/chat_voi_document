# T-10-4 — CitationChip: hiển thị `[Tên tệp, tr. N]` và các trạng thái

| Thuộc tính | Giá trị |
|---|---|
| Story | US-10 (P0) — AC-10.1; US-13d — AC-13d.2; US-23 |
| Sprint | S3 |
| Tầng | UI |
| Ước lượng | 1d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-07-1 (`CitationDTO`), F-03, F-04 (cờ `source_viewer`) |
| Chặn | T-10-5, T-13d-3 |

## Bối cảnh

Blueprint §3.5.3 bảng CitationChip: mặc định, hover/focus (tooltip tên đầy đủ), đã chọn, tài liệu đã xoá, chữ thuần khi cờ tắt. SADD §5.7.1: chip là `st.button` có key ổn định `cite:{answer_id}:{segment_ord}:{idx}`.

## Phạm vi

**Làm:** `app/ui/components/citation_chip.py` gồm `citation_row(answer_id, segment)` và hàm gộp nhãn.

## Đặc tả

Gộp citation trong một segment trước khi hiển thị (`group_citations`):
- Cùng `document_id` và các trang liên tiếp → một chip `tr. 7–8`; trang không liên tiếp → chip riêng.
- Giữ citation đầu tiên của nhóm để mở khung Nguồn (trang nhỏ nhất).

```python
def citation_row(answer_id: UUID, seg: SegmentDTO, flags: Flags) -> None:
    groups = group_citations(seg.citations)
    cols = st.columns(len(groups) or 1, gap="small")
    for idx, g in enumerate(groups):
        label = f"{truncate_middle(g.doc_name, 24)} · {page_label(g.pages)}"     # "hop-dong.pdf · tr. 7"
        key = f"cite:{answer_id}:{seg.ord}:{idx}"
        with cols[idx]:
            if not flags.source_viewer:
                st.caption(f"[{g.doc_name}, {page_label(g.pages)}]")            # chữ thuần, không bấm được
            elif g.deleted:
                st.button(f"~~{truncate_middle(g.doc_name, 24)}~~ · {t('cite.deleted')}",
                          key=key, disabled=True, help=t("cite.deleted_help"))  # "Tài liệu đã bị xoá"
            else:
                selected = st.session_state.get(K.SOURCE_CITE_KEY) == key
                st.button(label, key=key, help=g.doc_name, type="primary" if selected else "secondary",
                          on_click=open_source, args=(g.first, key))             # T-13d-3
```

- `page_label([7]) == "tr. 7"`, `page_label([7, 8]) == "tr. 7–8"`.
- `open_source(c, key)`: đặt `K.SOURCE_DOC/PAGE/QUOTE/CITE_KEY`; telemetry `citation_clicked` được service phát khi render trang (T-13d-4).
- Nhãn chip không dùng `unsafe_allow_html`; tên tệp đi qua `escape_md` trừ phần `~~` do ta thêm.

## Tiêu chí xong

- [ ] Chip đúng định dạng "tên · tr. N", tooltip tên đầy đủ.
- [ ] Citation có `deleted=True` hiển thị gạch ngang + "Tài liệu đã bị xoá", không bấm được (AC-13d.2).
- [ ] Cờ `FEATURE_SOURCE_VIEWER=false` hiển thị `[Tên tệp, tr. N]` dạng chữ.
- [ ] Key chip ổn định qua các lần rerun.

## Test

`tests/unit/ui/test_citation_chip.py` (AppTest + unit cho `group_citations`, `page_label`).

## Tham chiếu

Blueprint §3.5.3 (CitationChip), §3.4 · SADD §5.7.1 · US-10, US-13d · Implement_plan §14 C-03
