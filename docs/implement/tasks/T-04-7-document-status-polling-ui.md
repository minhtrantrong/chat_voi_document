# T-04-7 — UI tự cập nhật trạng thái tài liệu (fragment poll) và bật Composer

| Thuộc tính | Giá trị |
|---|---|
| Story | US-04 (P0) — AC-04.1, AC-04.2; US-07 — AC-07.2 |
| Sprint | S2 |
| Tầng | UI |
| Ước lượng | 1d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-05-2, T-05-3, F-11 |
| Chặn | T-07-4 (Composer dùng `docs.has_ready`) |

## Bối cảnh

AC-04.2: "Đang xử lý" chuyển "Sẵn sàng" **không cần tải lại trang**. ADR-005/C-02: dùng `@st.fragment(run_every=…)` đọc DB, không SSE. Blueprint §3.7.4: Composer tự bật khi có tài liệu sẵn sàng đầu tiên; banner "Đang xử lý n tài liệu…".

## Phạm vi

**Làm:** `render_document_panel` trong `app/ui/components/document_panel.py`: fragment có điều kiện, banner, cập nhật `K.DOCS_HAS_READY`.

## Đặc tả

```python
def render_document_panel(svc: Services, actor: Actor) -> None:
    render_upload_dropzone(svc, actor)                                  # T-01-6
    initial = svc.documents.list(actor, cursor=None, limit=st.session_state.get(K.DOCS_LIMIT, 50))
    st.session_state[K.DOCS_HAS_READY] = any(d.status == "READY" for d in initial.items)
    poll = any(d.status == "PROCESSING" for d in initial.items)

    @st.fragment(run_every=2.5 if poll else None)
    def _list() -> None:
        page = svc.documents.list(actor, cursor=None, limit=st.session_state.get(K.DOCS_LIMIT, 50))
        has_ready = any(d.status == "READY" for d in page.items)
        processing = sum(d.status == "PROCESSING" for d in page.items)
        if has_ready != st.session_state[K.DOCS_HAS_READY] or (poll and processing == 0):
            st.rerun()                        # rerun toàn app: bật/tắt Composer, dừng poll
        if processing:
            st.info(t("docs.processing_banner", n=processing))         # "Đang xử lý {n} tài liệu, thường mất vài phút"
        render_document_list(svc, actor, page)                          # T-05-3
    _list()
```

- `run_every` được tính mỗi lần script chạy: không có tài liệu PROCESSING thì fragment không poll.
- Tránh rerun vòng lặp: chỉ gọi `st.rerun()` khi trạng thái thực sự đổi so với lần chạy toàn app gần nhất.
- Tài liệu chuyển sang READY lần đầu: `st.toast(t("docs.ready", file_name=...))` (so sánh với danh sách id READY lưu trong `session_state`).
- Không gọi `check_session_timeout` trong fragment (T-21-4).
- Tải: 10 phiên × 1 truy vấn / 2.5 s là chấp nhận được; truy vấn dùng index `ix_documents_owner_status`.

## Tiêu chí xong

- [ ] Tải PDF: chip "Đang xử lý" ngay, sau khi worker xong chip tự chuyển "Sẵn sàng" mà không reload (AC-04.2).
- [ ] Khi chưa có tài liệu READY: Composer vô hiệu; tài liệu đầu tiên READY → Composer tự bật (AC-07.2 + Blueprint §3.7.4).
- [ ] Không có tài liệu PROCESSING: không có truy vấn định kỳ nào (kiểm bằng log/metric).

## Test

- `tests/unit/ui/test_document_panel.py` (AppTest, service giả trả PROCESSING rồi READY qua các lần gọi).
- `tests/e2e/test_status_autorefresh.py` (Playwright, worker thật với `FakeEmbedding`).

## Tham chiếu

US-04 · ADR-005 · SADD §5.7.1 (polling fragment) · Blueprint §3.6.1, §3.7.4 · Implement_plan §14 C-02
