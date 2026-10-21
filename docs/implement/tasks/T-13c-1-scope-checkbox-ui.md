# T-13c-1 — Checkbox chọn phạm vi tài liệu

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13c — Giới hạn câu hỏi vào một số tài liệu (P1) |
| Sprint | S3 |
| Tầng | UI |
| Ước lượng | 0.75d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-05-3, F-04 (cờ `scope_select`) |
| Chặn | T-07-5 (`selected_scope_ids`) |

## Bối cảnh

Thiết kế SCR-03/SCR-05: hộp chọn ở mỗi tài liệu "Sẵn sàng"; tài liệu Đang xử lý/Lỗi bị vô hiệu; danh sách `scopeDocIds` gửi kèm câu hỏi.

## Phạm vi

**Làm:** checkbox trong `document_item`, state `K.CHAT_SCOPE`, hàm `selected_scope_ids()`, caption phạm vi trên Composer.

## Đặc tả

```python
# trong document_item(d)
if flags.scope_select:
    scope: dict[str, bool] = st.session_state.setdefault(K.CHAT_SCOPE, {})
    key = str(d.id)
    if d.selectable and key not in scope: scope[key] = True                 # tài liệu mới READY → mặc định chọn
    st.checkbox(t("scope.include"), value=scope.get(key, False), key=f"scope:{d.id}",
                disabled=not d.selectable, label_visibility="collapsed",
                on_change=lambda: scope.__setitem__(key, st.session_state[f"scope:{d.id}"]))

def selected_scope_ids(ready_ids: list[UUID]) -> list[UUID]:
    scope = st.session_state.get(K.CHAT_SCOPE, {})
    chosen = [i for i in ready_ids if scope.get(str(i), True)]
    return [] if len(chosen) == len(ready_ids) else chosen                 # chọn hết → [] nghĩa là "tất cả"
```

- Caption trên Composer: chọn hết → `t("scope.all", n=n)` "Đang hỏi trên tất cả {n} tài liệu sẵn sàng"; chọn một phần → `t("scope.some", k=k, n=n)` "Đang hỏi trên {k}/{n} tài liệu"; chọn 0 → `st.warning(t("scope.none"))` "Chọn ít nhất một tài liệu sẵn sàng" và Composer bị vô hiệu.
- Cờ tắt: không hiển thị checkbox, luôn gửi `[]`.
- "Hội thoại mới" giữ nguyên phạm vi (T-16-1).

## Tiêu chí xong

- [ ] Tài liệu PROCESSING/ERROR có checkbox bị vô hiệu.
- [ ] Bỏ chọn một tài liệu → câu hỏi kế tiếp gửi đúng danh sách còn lại.
- [ ] Bỏ chọn hết → Composer vô hiệu, có cảnh báo.

## Test

`tests/unit/ui/test_scope_select.py` (AppTest).

## Tham chiếu

US-13c · Blueprint SCR-03/05 · Implement_plan §14 C-18
