# Index test case — browser-executable (37 file)

Được sinh từ [`TestPlan_Simple_Qdrant.md`](../TestPlan_Simple_Qdrant.md) (TP-CVD-004 v1.0, mục 4.6).

Mỗi file trong thư mục này là **một test case**, thực thi qua trình duyệt tại **http://localhost:8501/**. Artifact của mỗi case lưu vào thư mục riêng `./test_reports/<MÃ TEST CASE>/`.

## 1. Quy tắc chung cho mọi test case

- **App URL:** http://localhost:8501/ — mọi bằng chứng trạng thái app phải thể hiện trang này.
- **Artifact:** `./test_reports/<ID>/` gồm `report.md`, `video.webm` (hoặc `.mp4`), `screenshots/V01-….png`.
- **Bằng chứng:** mỗi bước có mã Vxx phải có 1 ảnh tương ứng.
- **Video:** quay liên tục từ trước bước đầu đến hết các bước; trên khung hình thấy rõ URL trên thanh địa chỉ; không cắt giữa chừng.
- **Report:** điền bảng Kỳ vọng vs Thực tế vs PASS/FAIL cho từng bước + bảng bug; template ghi sẵn ở mục 9 mỗi file test case.
- Gặp bug: **không sửa ứng dụng trong lúc test** — chỉ ghi nhận + chụp bằng chứng.

## 2. Tiền điều kiện môi trường (áp dụng mọi case)

```bash
docker compose up -d                       # Qdrant
cp .env.example .env                       # điền key/model
uv run streamlit run app/main.py           # app tại http://localhost:8501/
```

Bộ fixtures PDF adversarial + dataset eval: `tests/eval/fixtures/` (danh sách A-01…A-12 xem test plan mục 6-A).

## 3. Danh mục test case (37 file)

| File | Test case | Nhóm | Chu kỳ | Ưu tiên | Artifact |
|---|---|---|---|---|---|
| [`ST-01`](ST-01-upload-one-pdf.md) | Upload 1 PDF hợp lệ | System | C2 | High | `./test_reports/ST-01/` |
| [`ST-02`](ST-02-upload-many-with-invalid.md) | Upload nhiều PDF + file lỗi + trùng tên | System | C2 | High | `./test_reports/ST-02/` |
| [`ST-03`](ST-03-chat-in-scope.md) | Chat trong phạm vi tài liệu | System | C3 | High | `./test_reports/ST-03/` |
| [`ST-04`](ST-04-chat-out-of-scope-not-found.md) | Chat ngoài phạm vi → NOT_FOUND | System | C3 | High | `./test_reports/ST-04/` |
| [`ST-05`](ST-05-chat-multi-document.md) | Chat tổng hợp đa tài liệu | System | C3 | High | `./test_reports/ST-05/` |
| [`ST-06`](ST-06-delete-document.md) | Xoá tài liệu (cascade + hiệu lực chat) | System | C3 | High | `./test_reports/ST-06/` |
| [`ST-07`](ST-07-empty-state-chat-disabled.md) | Trạng thái rỗng — chat vô hiệu | System (edge) | C2 | Medium | `./test_reports/ST-07/` |
| [`ST-08`](ST-08-only-error-docs-chat-disabled.md) | Chỉ có tài liệu Lỗi — chat vô hiệu | System (edge) | C3 | Medium | `./test_reports/ST-08/` |
| [`ST-09`](ST-09-qdrant-down-no-crash.md) | Qdrant dừng — app không crash | System (edge) | C3 | Medium | `./test_reports/ST-09/` |
| [`ST-10`](ST-10-qdrant-recovery-reupload.md) | Qdrant bật lại — bình thường | System (edge) | C3 | Medium | `./test_reports/ST-10/` |
| [`ST-11`](ST-11-invalid-llm-api-key.md) | Sai API key — không lộ | System (edge) | C3 | High | `./test_reports/ST-11/` |
| [`ST-12`](ST-12-oversize-rejected.md) | > 25 MB bị từ chối | System (edge) | C2 | Medium | `./test_reports/ST-12/` |
| [`ST-13`](ST-13-too-many-pages-rejected.md) | > 400 trang bị từ chối | System (edge) | C2 | Medium | `./test_reports/ST-13/` |
| [`ST-14`](ST-14-encrypted-pdf-rejected.md) | PDF mã hoá bị từ chối | System (edge) | C2 | Medium | `./test_reports/ST-14/` |
| [`ST-15`](ST-15-scanned-pdf-rejected.md) | PDF scan bị từ chối | System (edge) | C2 | High | `./test_reports/ST-15/` |
| [`ST-16`](ST-16-refresh-clears-chat-history.md) | Refresh mất lịch sử chat | System (edge) | C2 | Medium | `./test_reports/ST-16/` |
| [`ST-17`](ST-17-long-unicode-filename.md) | Tên file dài/Unicode | System (edge) | C2 | Medium | `./test_reports/ST-17/` |
| [`ST-18`](ST-18-qdrant-restart-data-persisted.md) | Qdrant restart — dữ liệu còn | System (edge) | C3→C4 | High | `./test_reports/ST-18/` |
| [`UI-01`](UI-01-status-chips.md) | Chip trạng thái | UI | C3 | High | `./test_reports/UI-01/` |
| [`UI-02`](UI-02-chat-input-enable-disable.md) | Chat bật/tắt theo READY | UI | C3 | High | `./test_reports/UI-02/` |
| [`UI-03`](UI-03-vietnamese-error-messages.md) | Thông báo lỗi tiếng Việt | UI | C3 | High | `./test_reports/UI-03/` |
| [`UI-04`](UI-04-sources-expander.md) | Expander Nguồn | UI | C3 | High | `./test_reports/UI-04/` |
| [`UI-05`](UI-05-chat-history-in-session.md) | Lịch sử chat đa lượt | UI | C3 | Medium | `./test_reports/UI-05/` |
| [`UI-06`](UI-06-layout-with-long-names.md) | Layout tên file dài | UI | C3 | Medium | `./test_reports/UI-06/` |
| [`UI-07`](UI-07-disclaimer-bar.md) | Dòng nhắc «AI có thể sai…» | UI | C3 | Medium | `./test_reports/UI-07/` |
| [`SEC-01`](SEC-01-no-key-or-stack-trace-leak.md) | Không lộ key/stack trace | Security | C3 | High | `./test_reports/SEC-01/` |
| [`SEC-02`](SEC-02-no-content-in-logs.md) | Không log nội dung | Security | C3 | High | `./test_reports/SEC-02/` |
| [`SEC-03`](SEC-03-malicious-filename-xss-path-traversal.md) | Tên file độc hại | Security | C3 | High | `./test_reports/SEC-03/` |
| [`SEC-04`](SEC-04-safe-deployment-no-auth.md) | Triển khai no-auth an toàn | Security | C3 | High | `./test_reports/SEC-04/` |
| [`PF-01`](PF-01-ingest-latency.md) | Thời gian ingest → READY | Performance | C3 | Medium | `./test_reports/PF-01/` |
| [`PF-02`](PF-02-p90-first-token.md) | p50/p90 chữ đầu tiên | Performance | C3 | Medium | `./test_reports/PF-02/` |
| [`PF-03`](PF-03-qdrant-search-latency.md) | Độ trễ search Qdrant | Performance | C3 | Medium | `./test_reports/PF-03/` |
| [`PF-04`](PF-04-fast-rejection-at-bounds.md) | Từ chối nhanh tại biên | Performance | C3 | Medium | `./test_reports/PF-04/` |
| [`EV-01`](EV-01-in-scope-accuracy.md) | 10 câu trong tài liệu ≥ 8/10 | Eval RAG | C3→C4 | High | `./test_reports/EV-01/` |
| [`EV-02`](EV-02-multi-doc-synthesis.md) | 10 câu đa tài liệu ≥ 8/10 | Eval RAG | C3→C4 | High | `./test_reports/EV-02/` |
| [`EV-03`](EV-03-not-found-accuracy.md) | 10 câu ngoài phạm vi ≥ 9/10 | Eval RAG | C3→C4 | High | `./test_reports/EV-03/` |
| [`EV-04`](EV-04-source-accuracy.md) | Nguồn đúng ≥ 90% | Eval RAG | C3→C4 | High | `./test_reports/EV-04/` |

## 4. Thứ tự chạy đề xuất

| Chu kỳ | Sau milestone | Test case |
|---|---|---|
| **C2 — System partial** | M2 (S-14 xong) | ST-01, ST-02, ST-07, ST-12, ST-13, ST-14, ST-15, ST-16, ST-17 |
| **C3 — System full + Eval** | M3 (S-21 xong) | ST-03…06, ST-08…11, ST-18, UI-01…07, SEC-01…04, PF-01…04, EV-01…04 |
| **C4 — Regression** | M4 (S-26 xong) | chạy lại ST-01, ST-06, ST-18 + EV-01…04 |

## 5. Phạm vi không tạo file (reference)

- UT-01…13, IT-01…12 (pytest): giữ trong test plan mục 4.6.1–4.6.2, là tiền điều kiện cho C2/C3; không thực thi qua trình duyệt.
- UAT-01…11: nghiệm thu được thể hiện qua ST + EV (ánh xạ xem test plan mục 4.6.4).

## 6. Tài liệu liên quan

- Test plan: [`TestPlan_Simple_Qdrant.md`](../TestPlan_Simple_Qdrant.md)
- Kế hoạch triển khai: [`Implement_plan_Simple_Qdrant.md`](../../implement/Implement_plan_Simple_Qdrant.md)
- Checklist thủ công: Task S-25 — output `docs/testing/manual-checklist.md`
- Mã lỗi + thông báo chuẩn: test plan mục 6-C
