# S-12 — UI sidebar: upload, danh sách, trạng thái, xoá

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01, US-04, US-05, US-06 |
| Phase | P1 |
| Tầng | UI |
| Ước lượng | 0,75d |
| Phụ thuộc | S-11 |
| Chặn | S-13, S-14, S-19, S-25 |
| Owner gợi ý | Full-stack |

## 1. Mục tiêu

Sidebar là nơi duy nhất quản lý tài liệu: kéo/thả PDF, thấy trạng thái xử lý, danh sách tài liệu và nút xoá có xác nhận. Main area để trống cho chat (S-18).

## 2. Phạm vi

**Làm:**

- `st.file_uploader` nhận nhiều PDF.
- Gọi `ingest_pdf` với progress (`st.status`/`st.progress`).
- Danh sách tài liệu: tên, số trang, dung lượng, trạng thái, ngày.
- Chip trạng thái: `Đang xử lý`, `Sẵn sàng`, `Lỗi`.
- Xoá có xác nhận 2 bước.
- Xoá đúng thứ tự: Qdrant → SQLite → file → clear chat session.
- Uploader nonce để không xử lý lại file khi rerun.
- Banner nếu Qdrant không sẵn sàng.

**Không làm:**

- Chat (S-18).
- Sửa tên tài liệu.
- Tải lại/xem PDF.
- Chọn nhiều tài liệu để xoá hàng loạt.

## 3. File chính

```text
app/main.py
app/ui.py          # tuỳ chọn: tách hàm render
tests/test_ui.py   # AppTest cơ bản
```

## 4. Đặc tả

### 4.1 Khởi tạo trang

```python
import streamlit as st
from app.config import get_settings
from app.db import init_db, list_documents, delete_document, get_document
from app.vector_store import health, delete_document as delete_points

st.set_page_config(page_title="Chat với tài liệu", page_icon="📄", layout="wide")
init_db()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploader_nonce" not in st.session_state:
    st.session_state.uploader_nonce = 0
if "confirm_delete_id" not in st.session_state:
    st.session_state.confirm_delete_id = None

if not health():
    st.warning("Qdrant chưa sẵn sàng. Chạy `docker compose up -d` rồi tải lại trang.")
```

> `health()` gọi Qdrant mỗi rerun; với demo local chấp nhận. Nếu chậm, cache 5s.

### 4.2 Upload

```python
with st.sidebar:
    st.header("Tài liệu")
    uploaded = st.file_uploader(
        "Tải PDF",
        type=["pdf"],
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_nonce}",
        help="Tối đa 25 MB, 400 trang mỗi tệp.",
    )

    if uploaded:
        for f in uploaded:
            with st.status(f"Đang xử lý {f.name}…", expanded=True) as status:
                bar = st.progress(0)
                try:
                    doc = ingest_pdf(
                        f.name,
                        f,
                        size_bytes=f.size,
                        progress=lambda stage, pct: bar.progress(pct),
                    )
                    status.update(label=f"Xong: {f.name}", state="complete")
                except Exception as exc:
                    status.update(label=f"Lỗi: {f.name}", state="error")
                    st.error(error_message(exc, f.name))  # S-14
        st.session_state.uploader_nonce += 1
        st.rerun()
```

**Vì sao nonce:** Streamlit giữ `UploadedFile` qua rerun; đổi `key` sau khi xử lý để lần rerun sau uploader rỗng, tránh ingest lặp.

### 4.3 Danh sách

```python
docs = list_documents()

if not docs:
    st.caption("Chưa có tài liệu. Tải PDF đầu tiên.")
else:
    for doc in docs:
        with st.container(border=True):
            st.markdown(f"**{doc.file_name}**")
            meta = []
            if doc.page_count:
                meta.append(f"{doc.page_count} trang")
            meta.append(format_bytes(doc.size_bytes))
            st.caption(" · ".join(meta))
            st.markdown(status_badge(doc), unsafe_allow_html=True)

            if doc.status == "ERROR":
                st.caption(f"Mã lỗi: {doc.error_code}")

            if st.button("Xoá", key=f"delete_{doc.id}"):
                st.session_state.confirm_delete_id = doc.id

            if st.session_state.confirm_delete_id == doc.id:
                st.warning(f"Xoá **{doc.file_name}**? Không hoàn tác.")
                c1, c2 = st.columns(2)
                if c1.button("Xác nhận", key=f"confirm_{doc.id}", type="primary"):
                    _delete_doc(doc)
                    st.session_state.confirm_delete_id = None
                    st.session_state.messages = []
                    st.rerun()
                if c2.button("Huỷ", key=f"cancel_{doc.id}"):
                    st.session_state.confirm_delete_id = None
                    st.rerun()
```

### 4.4 Hàm xoá

```python
def _delete_doc(doc):
    try:
        delete_points(doc.id)          # Qdrant trước
    except Exception:
        st.error("Không xoá được dữ liệu vector. Thử lại sau.")
        return
    delete_document(doc.id)            # SQLite
    try:
        doc.stored_path.unlink(missing_ok=True)
    except OSError:
        st.warning("Đã xoá metadata nhưng không xoá được tệp gốc.")
```

**Thứ tự quan trọng:** nếu xoá Qdrant lỗi, **không** xoá DB/file để tránh mồ côi; người dùng thử lại.

### 4.5 Format dung lượng

```python
def format_bytes(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024**2:
        return f"{n / 1024:.0f} KB"
    return f"{n / 1024**2:.1f} MB"
```

Dùng cho metadata dưới tên tài liệu. Không cần thư viện ngoài.

### 4.6 Trạng thái

```python
STATUS_LABEL = {
    "PROCESSING": ("Đang xử lý", "#b45309"),
    "READY": ("Sẵn sàng", "#15803d"),
    "ERROR": ("Lỗi", "#b91c1c"),
}

def status_badge(doc) -> str:
    label, color = STATUS_LABEL[doc.status]
    return f'<span style="color:{color};font-weight:600">{label}</span>'
```

Có thể dùng `st.success`/`st.warning`/`st.error` thay HTML; HTML gọn hơn. Không dùng `unsafe_allow_html` với dữ liệu người dùng chưa escape — `file_name` phải escape nếu chèn HTML. Đơn giản hơn: dùng `st.caption` + emoji:

```python
STATUS_EMOJI = {"PROCESSING": "⏳", "READY": "✅", "ERROR": "❌"}
st.caption(f"{STATUS_EMOJI[doc.status]} {STATUS_LABEL[doc.status]}")
```

## 5. Trường hợp biên

- Uploader trả file > giới hạn → S-11 raise trước khi lưu; UI báo.
- Nhiều file cùng lúc → S-13 xử lý; S-12 chỉ cần loop.
- Xoá tài liệu đang `PROCESSING` → trong app sync, không xảy ra; nếu có, vẫn xoá được row/point.
- File gốc đã bị xoá tay → `unlink(missing_ok=True)` không lỗi.
- Qdrant down khi xoá → báo lỗi, giữ row.
- Tên file chứa HTML → không chèn HTML trực tiếp; nếu dùng markdown, escape.
- Danh sách dài → `st.container` đủ; không cần phân trang.
- Rerun sau upload → nonce tránh ingest lặp.
- `init_db()` lỗi quyền ghi → báo lỗi rõ, dừng trang.

## 6. Tiêu chí xong

- [ ] Upload 1 PDF → thấy trạng thái xử lý, sau đó `Sẵn sàng`.
- [ ] Danh sách hiển thị tên, số trang, dung lượng, trạng thái.
- [ ] Xoá có xác nhận; sau xoá không còn trong danh sách.
- [ ] Xoá Qdrant lỗi → row vẫn còn, có thông báo.
- [ ] Uploader không xử lý lặp sau rerun.
- [ ] Qdrant down → banner cảnh báo, không crash.
- [ ] Không có chat input ở task này (S-19).

## 7. Test

- AppTest: render sidebar có text "Tài liệu", "Tải PDF".
- AppTest với DB seed 1 doc READY → thấy tên tài liệu.
- Manual: upload/xoá/confirm/cancel.
- Unit: `format_bytes`, `status_badge` (nếu tách hàm).

## 8. Tham chiếu

- Kế hoạch §8, §7.5.
- S-11, S-13, S-14, S-19.
