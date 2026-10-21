# T-13d-4 — Telemetry `citation_clicked` và audit khi ADMIN xem tài liệu người khác

| Thuộc tính | Giá trị |
|---|---|
| Story | US-13d (P1); US-20 (đo lường); SADD §5.8.3 |
| Sprint | S4 |
| Tầng | APP |
| Ước lượng | 0.25d |
| Owner gợi ý | Backend 1 |
| Phụ thuộc | T-13d-2, F-05, F-06 |
| Chặn | — |

## Bối cảnh

Blueprint §3.6.2: telemetry `citation_clicked`. SADD §5.8.3: ADMIN đọc tài liệu không sở hữu **phải** ghi audit.

## Phạm vi

**Làm:** phân biệt "mở từ chip" và "điều hướng trang" để telemetry không bị đếm thừa; ghi audit.

## Đặc tả

- Thêm tham số `source: Literal["citation", "navigate"] = "citation"` vào `render_page`.
- Telemetry `citation_clicked {page}` (kèm `answer_id` nếu UI truyền vào) chỉ khi `source == "citation"` **và** là lần render đầu cho `cite_key` đó trong phiên (UI truyền `answer_id`; service nhận thêm `answer_id: UUID | None`).
- Audit `DOCUMENT_VIEW_OTHER` mỗi lần ADMIN render trang của tài liệu PRIVATE người khác; metadata `{"page": page}`.

## Tiêu chí xong

- [ ] Bấm chip 1 lần + bấm ▶ 3 lần → 1 sự kiện `citation_clicked`.
- [ ] ADMIN xem tài liệu private của B → có audit.

## Test

`tests/integration/documents/test_render_page_telemetry.py`.

## Tham chiếu

Blueprint §3.6.2 · SADD §5.8.3 · F-06 (whitelist `citation_clicked`)
