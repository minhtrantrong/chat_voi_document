# PLT-13 — Rà soát trợ năng và khả năng giãn chữ của UI

| Thuộc tính | Giá trị |
|---|---|
| Nhóm | Nền tảng (Phần I §4 S4, mục 4.10) |
| Sprint | S4 |
| Tầng | UI / TEST |
| Ước lượng | 1d |
| Owner gợi ý | QA/DevOps + Backend 1 |
| Phụ thuộc | Các UI task của S2–S4 đã xong |
| Chặn | M4 |

## Bối cảnh

Blueprint §3.5.3, §3.6.5, §3.8 yêu cầu: trạng thái có biểu tượng + nhãn (không chỉ màu), thao tác được bằng bàn phím, chịu giãn chữ +30%. Streamlit lo phần lớn ARIA; task này kiểm tra những gì ta tự thêm. Phím tắt Esc/Ctrl+K không làm trong MVP (C-08).

## Phạm vi

**Làm:** chạy axe-core qua Playwright trên các màn hình SCR-01…SCR-10, sửa lỗi mức serious/critical do code của ta gây ra; checklist thủ công.

**Không làm:** sửa lỗi bên trong component lõi của Streamlit (ghi nhận, báo upstream nếu nặng).

## Đặc tả

Checklist thủ công:

| # | Kiểm tra | Màn hình |
|---|---|---|
| 1 | Chip trạng thái có icon + chữ (◐ Đang xử lý / ✔ Sẵn sàng / ⚠ Lỗi) | SCR-03/04/05 |
| 2 | Chip trích dẫn đã xoá có chữ "Tài liệu đã bị xoá", không chỉ gạch ngang | SCR-05 |
| 3 | Tab qua được: TopBar → danh sách tài liệu → Composer → chip → khung Nguồn | SCR-05 |
| 4 | Mọi nút icon-only có `help=` (tooltip) mô tả | Tất cả |
| 5 | Độ tương phản chữ ≥ 4.5:1 với theme ở PLT-07 | Tất cả |
| 6 | Với `vi_long.py` (chuỗi dài hơn 30%, T-13b-3) không có chữ bị cắt mất nghĩa hoặc nút bị đẩy ra ngoài | SCR-02…SCR-09 |
| 7 | Thông báo trạng thái quan trọng dùng `st.toast`/`st.info` (được đọc bởi screen reader) | Upload, xoá, feedback |

Tự động: `tests/e2e/test_a11y.py` dùng `axe-playwright-python` trên từng màn hình; fail nếu có vi phạm `serious`/`critical` không nằm trong `tests/e2e/a11y_allowlist.yaml` (allowlist chỉ chứa lỗi của Streamlit core, mỗi mục có lý do).

## Tiêu chí xong

- [ ] Checklist 7 mục đạt, có ảnh chụp minh hoạ.
- [ ] `test_a11y.py` xanh.
- [ ] Nợ trợ năng còn lại ghi vào backlog với mã `TD-UX-xx`.

## Tham chiếu

Blueprint §3.5.3, §3.6.5, §3.8 · Implement_plan §14 C-08
