# S-25 — Checklist kiểm thử thủ công

| Thuộc tính | Giá trị |
|---|---|
| Story | US-01…US-09 (nghiệm thu) |
| Phase | P3 |
| Tầng | TEST |
| Ước lượng | 0,25d |
| Phụ thuộc | S-12…S-21 |
| Chặn | S-26 |
| Owner gợi ý | QA/Full-stack |

## 1. Mục tiêu

Có checklist ngắn (**45–60 phút**) để một người không phải tác giả code chạy hết 6 luồng chính + các trạng thái biên, ghi pass/fail và bug. Đây là cổng trước demo.

## 2. Phạm vi

**Làm:**

- Checklist theo bước, có dữ liệu mẫu gợi ý.
- Ghi rõ **kỳ vọng** và **cách xác minh**.
- Bao phủ: upload, lỗi, chat, not-found, multi-doc, delete, restart, Qdrant down, no-ready.
- Xuất file `docs/testing/manual-checklist.md` (task này tạo).
- Ghi lại môi trường: OS, browser, model, ngày.

**Không làm:**

- Test tự động (S-22/S-23).
- Test bảo mật/penetration (không auth).
- Test tải/đa người dùng.

## 3. File chính

```text
docs/testing/manual-checklist.md   # output
tests/eval/fixtures/               # dùng PDF mẫu S-24
```

## 4. Checklist

### 4.1 Chuẩn bị

| # | Bước | Kỳ vọng | Kết quả |
|---|---|---|---|
| 0.1 | `docker compose up -d` | Qdrant healthy | ☐ |
| 0.2 | `cp .env.example .env`, điền key/model | Không lỗi cú pháp | ☐ |
| 0.3 | `streamlit run app/main.py` | Mở `localhost:8501`, không exception | ☐ |
| 0.4 | Mở DevTools/terminal | Không có traceback khi tải trang | ☐ |

### 4.2 Luồng 1 — Upload một PDF

| # | Bước | Kỳ vọng | Kết quả |
|---|---|---|---|
| 1.1 | Kéo `hop-dong.pdf` vào uploader | Hiện progress/trạng thái "Đang xử lý" | ☐ |
| 1.2 | Chờ xử lý | Tài liệu xuất hiện, chip **Sẵn sàng** | ☐ |
| 1.3 | Kiểm tra số trang/dung lượng | Đúng với PDF | ☐ |
| 1.4 | Kiểm tra `data/uploads/` | Có file `{doc_id}.pdf` | ☐ |
| 1.5 | Kiểm tra Qdrant dashboard | Collection `document_chunks` có point | ☐ |
| 1.6 | Refresh trang | Tài liệu vẫn còn trong danh sách | ☐ |

### 4.3 Luồng 2 — Upload nhiều PDF + một file lỗi

| # | Bước | Kỳ vọng | Kết quả |
|---|---|---|---|
| 2.1 | Chọn `hop-dong.pdf`, `bao-gia.pdf`, `fake.docx` | `fake.docx` bị chặn/không nhận | ☐ |
| 2.2 | Chọn thêm PDF scan | Row **Lỗi** mã `PDF_NO_TEXT` | ☐ |
| 2.3 | Kiểm tra 2 PDF hợp lệ | Cả 2 **Sẵn sàng**, không bị dừng bởi file lỗi | ☐ |
| 2.4 | Xoá file lỗi | Biến mất khỏi danh sách | ☐ |
| 2.5 | Tải lại cùng PDF | Tạo tài liệu mới (không dedupe) — đúng thiết kế | ☐ |

### 4.4 Luồng 3 — Chat trong tài liệu

| # | Bước | Kỳ vọng | Kết quả |
|---|---|---|---|
| 3.1 | Hỏi "Hạn chót nộp hồ sơ là ngày nào?" | Trả lời `30/11/2026`, có `[S1]` | ☐ |
| 3.2 | Mở expander "Nguồn" | Đúng `hop-dong.pdf`, trang 1 | ☐ |
| 3.3 | Hỏi tiếp "Bên A là công ty nào?" | Trả lời đúng, giữ ngữ cảnh hội thoại | ☐ |
| 3.4 | Hỏi câu dài/tiếng Việt có dấu | Không lỗi encoding | ☐ |
| 3.5 | Kiểm tra streaming | Câu trả lời hiện dần, không treo | ☐ |

### 4.5 Luồng 4 — Ngoài phạm vi

| # | Bước | Kỳ vọng | Kết quả |
|---|---|---|---|
| 4.1 | Hỏi "Giá cổ phiếu VNM hôm nay?" | Đúng thông báo "Không tìm thấy thông tin…" | ☐ |
| 4.2 | Kiểm tra nguồn | Không hiển thị nguồn | ☐ |
| 4.3 | Hỏi "Thủ đô nước Pháp?" | NOT_FOUND, không bịa | ☐ |
| 4.4 | Hỏi câu nửa đúng/nửa ngoài | Không bịa phần ngoài; nếu không đủ → NOT_FOUND | ☐ |

### 4.6 Luồng 5 — Nhiều tài liệu

| # | Bước | Kỳ vọng | Kết quả |
|---|---|---|---|
| 5.1 | Upload `bao-gia.pdf` + `quy-dinh.pdf` | READY | ☐ |
| 5.2 | Hỏi "So sánh thời gian giao hàng gói A và thời hạn hợp đồng" | Trả lời cần cả `bao-gia.pdf` + `hop-dong.pdf` | ☐ |
| 5.3 | Mở nguồn | Có ≥ 2 tài liệu | ☐ |
| 5.4 | Hỏi câu chỉ liên quan `quy-dinh.pdf` | Nguồn đúng file, không lẫn | ☐ |
| 5.5 | Kiểm tra giới hạn chunk/tài liệu | Không có tài liệu nào chiếm toàn bộ nguồn (nếu đủ hit) | ☐ |

### 4.7 Luồng 6 — Xoá tài liệu

| # | Bước | Kỳ vọng | Kết quả |
|---|---|---|---|
| 6.1 | Bấm Xoá `hop-dong.pdf` | Hiện xác nhận | ☐ |
| 6.2 | Bấm Huỷ | Tài liệu vẫn còn | ☐ |
| 6.3 | Bấm Xoá → Xác nhận | Tài liệu biến mất | ☐ |
| 6.4 | Kiểm tra Qdrant | Không còn point `doc_id` đó | ☐ |
| 6.5 | Kiểm tra `data/uploads/` | File đã xoá | ☐ |
| 6.6 | Hỏi lại câu trước | Không còn nguồn `hop-dong.pdf`; lịch sử chat đã clear | ☐ |
| 6.7 | Xoá tài liệu cuối | Chat input disabled + thông báo upload | ☐ |

### 4.8 Trạng thái biên

| # | Bước | Kỳ vọng | Kết quả |
|---|---|---|---|
| 4.8.1 | Chưa upload gì, mở trang | Chat disabled + "Tải PDF đầu tiên" | ☐ |
| 4.8.2 | Chỉ có tài liệu lỗi | Chat disabled + hướng dẫn | ☐ |
| 4.8.3 | Dừng Qdrant, refresh | Banner "Qdrant chưa sẵn sàng", không crash | ☐ |
| 4.8.4 | Bật Qdrant lại, upload | Hoạt động lại | ☐ |
| 4.8.5 | Sai API key, hỏi | Thông báo cấu hình/thử lại, không lộ key | ☐ |
| 4.8.6 | Upload file > 25 MB | Báo vượt dung lượng, không lưu | ☐ |
| 4.8.7 | Upload PDF > 400 trang | Báo vượt số trang | ☐ |
| 4.8.8 | Upload PDF mã hoá | Báo `PDF_ENCRYPTED` | ☐ |
| 4.8.9 | Upload PDF scan | Báo `PDF_NO_TEXT`, không READY | ☐ |
| 4.8.10 | Refresh khi đang chat | Lịch sử mất (đúng thiết kế), tài liệu còn | ☐ |
| 4.8.11 | Tên file dài/Unicode | Hiển thị không vỡ layout, không XSS | ☐ |
| 4.8.12 | Qdrant restart | Tài liệu vẫn search được (volume) | ☐ |

## 5. Ghi nhận

```text
Môi trường:
- OS/browser:
- Python:
- Model LLM/Embedding:
- Qdrant image:
- Ngày/người test:

Kết quả: __/__ pass
Bug phát hiện:
| ID | Mô tả | Mức độ | Task liên quan |
|---|---|---|---|
```

## 6. Tiêu chí xong

- [ ] Tất cả mục **bắt buộc** (4.2–4.7) pass.
- [ ] Các mục biên 4.8.1–4.8.12 pass hoặc có bug được ghi nhận.
- [ ] Không có traceback trên UI.
- [ ] Không có dữ liệu nhạy cảm trong log.
- [ ] Bug P0/P1 được tạo task riêng trước demo.

## 7. Cách chạy checklist

1. Dùng một venv/máy sạch nếu có thể; không dùng dữ liệu thật.
2. Chạy theo thứ tự 4.1 → 4.8; đánh dấu ☐/☑.
3. Với mỗi mục fail, ghi mã lỗi + ảnh chụp màn hình + log terminal.
4. Ghi lại môi trường ở §5.
5. Mục bắt buộc fail → không demo; tạo bug/task sửa trước.

## 8. Tham chiếu

- Kế hoạch §9.2.
- S-12…S-21, S-24.
