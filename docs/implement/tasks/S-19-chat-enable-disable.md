# S-19 — Bật/tắt chat theo trạng thái tài liệu

| Thuộc tính | Giá trị |
|---|---|
| Story | US-07 |
| Phase | P2 |
| Tầng | UI |
| Ước lượng | 0,25d |
| Phụ thuộc | S-12, S-18 |
| Chặn | S-25 |
| Owner gợi ý | Full-stack |

## 1. Mục tiêu

Người dùng chỉ có thể hỏi khi có ít nhất một tài liệu `READY`. Khi chưa có, UI giải thích rõ vì sao và hướng dẫn upload; không để người dùng gõ câu hỏi rồi mới báo lỗi.

## 2. Phạm vi

**Làm:**

- Tính `docs = list_documents()` **một lần** mỗi rerun, truyền cho sidebar và chat.
- `has_ready = any(d.status == READY for d in docs)`.
- `st.chat_input(..., disabled=not has_ready)`.
- Empty state theo 3 trường hợp:
  1. Chưa có tài liệu.
  2. Có tài liệu nhưng đang xử lý (hiếm vì sync).
  3. Có tài liệu nhưng tất cả lỗi.
- Không hiển thị input khi disabled (hoặc disabled + help text).
- Sau upload/delete, rerun tự cập nhật.

**Không làm:**

- Không chặn theo quyền (không auth).
- Không chọn tài liệu cụ thể (future).
- Không disable khi Qdrant down (chat sẽ báo lỗi khi gửi); có thể thêm sau.

## 3. File chính

```text
app/main.py
app/ui.py
tests/test_ui_state.py
```

## 4. Đặc tả

### 4.1 Tính trạng thái

```python
docs = list_documents()
ready_docs = [d for d in docs if d.status == "READY"]
has_ready = bool(ready_docs)
```

### 4.2 Empty state

```python
if not docs:
    st.info("Tải PDF đầu tiên ở thanh bên để bắt đầu hỏi.")
elif not ready_docs:
    if any(d.status == "PROCESSING" for d in docs):
        st.info("Tài liệu đang được xử lý. Đợi hoàn tất rồi hỏi.")
    else:
        st.warning(
            "Chưa có tài liệu sẵn sàng. Kiểm tra lỗi ở thanh bên, "
            "xoá tệp lỗi và tải lại PDF khác."
        )
```

### 4.3 Chat input

```python
question = st.chat_input(
    "Hỏi về nội dung tài liệu…",
    disabled=not has_ready,
)
```

Streamlit hiển thị input mờ; có thể thêm caption:

```python
if not has_ready:
    st.caption("Chat sẽ bật khi có ít nhất một tài liệu xử lý thành công.")
```

### 4.4 Truyền docs

Tránh gọi `list_documents()` nhiều nơi gây lệch trạng thái:

```python
docs = list_documents()
render_sidebar(docs)       # S-12, nhận docs
render_chat(docs)          # S-18, nhận docs
```

Nếu S-12/S-18 hiện tự gọi, refactor nhẹ để nhận tham số. Không cần cache phức tạp.

## 5. Trường hợp biên

- 0 tài liệu → info + input disabled.
- 1 tài liệu `ERROR` → warning + disabled.
- 1 tài liệu `PROCESSING` (nếu có) → info + disabled.
- 1 `READY` + 1 `ERROR` → input bật; lỗi vẫn hiển thị sidebar.
- Tài liệu `READY` bị xoá trong lúc chat → rerun, input disabled nếu không còn; lịch sử chat bị clear bởi S-12.
- Upload đang chạy (sync) → UI chờ; sau rerun trạng thái cập nhật.
- Qdrant down nhưng có READY → input vẫn bật; gửi sẽ báo `QDRANT_UNAVAILABLE`. Có thể disable nếu `health()` false; ghi chú tương lai.
- Nhiều session cùng lúc → mỗi session thấy docs chung (không auth); chấp nhận.

## 6. Tiêu chí xong

- [ ] 0 tài liệu → input disabled + thông điệp "Tải PDF đầu tiên".
- [ ] Chỉ có tài liệu lỗi → input disabled + hướng dẫn.
- [ ] Có ít nhất 1 READY → input bật.
- [ ] Xoá tài liệu cuối → input disabled ngay sau rerun.
- [ ] Không gọi `list_documents()` lặp lại không cần thiết.
- [ ] Không hiển thị chat input khi chưa có tài liệu (hoặc disabled rõ ràng).

## 7. Test

- AppTest: seed DB 0 doc → chat input disabled.
- AppTest: seed 1 doc ERROR → disabled + warning.
- AppTest: seed 1 doc READY → enabled.
- Manual: upload → input bật; xoá → tắt.

## 8. Tham chiếu

- Kế hoạch §8 trạng thái UI.
- S-12, S-18, S-25.
