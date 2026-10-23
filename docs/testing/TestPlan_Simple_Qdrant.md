# Kế hoạch Kiểm thử (Master Test Plan) — Ứng dụng "Upload PDF & Chat với AI" (Qdrant)

| Mục | Giá trị |
|---|---|
| Mã tài liệu | **TP-CVD-004** |
| Phiên bản / Trạng thái | 1.0 / Draft |
| Ngày | 2026-10-23 |
| Chuẩn áp dụng | **IEEE 829-2008** — Software Test Documentation |
| Nguồn yêu cầu | [Implement_plan_Simple_Qdrant.md](../implement/Implement_plan_Simple_Qdrant.md) (IMP-CVD-003 v1.0) · [PRD.md](../requirements/PRD.md) (PRD-CVD-001 v0.1) · [User_Stories.md](../requirements/User_Stories.md) (US-CVD-001 v0.1, US-01…US-09 rút gọn) · [SADD.md](../design/SADD.md) (tham khảo) · [UIUX_Blueprint_Design.md](../design/UIUX_Blueprint_Design.md) (tham khảo) · [Task breakdown](../implement/tasks/README.md) S-01…S-26 |
| Phạm vi | Một trang Streamlit: upload PDF → extract → chunk → embed → Qdrant → chat có nguồn; xoá tài liệu |
| Đối tượng đọc | QA, Developer, Product Owner |

> **Điều chỉnh so với template IEEE 829 gốc:** ứng dụng là monolith Streamlit **không có REST API công khai, không auth, không SSE/worker**. Do đó mục "API Testing" của template được thay bằng **kiểm thử adapter/giao diện thành phần** (Qdrant client, Embedding API, LLM API qua OpenAI-compatible); mục "Security/Accessibility" được thu gọn theo đúng phạm vi demo của IMP-CVD-003. Mọi cắt giảm đều ghi rõ ở §5.0 (Features Not to be Tested).

---

## 1. Tóm tắt

Kế hoạch này định nghĩa chiến lược kiểm thử cho bản triển khai đơn giản hoá (IMP-CVD-003): 4 cấp kiểm thử (Unit, Integration, System/Manual, Acceptance), chạy song song theo 26 task S-01…S-26, với 3 trọng tâm rủi ro cao nhất:

1. **Chất lượng RAG** — câu trả lời đúng nội dung, có nguồn đúng tài liệu/trang, không bịa, từ chối đúng khi ngoài phạm vi (đo bằng bộ eval 30 câu, ngưỡng §9.3 của IMP).
2. **Tính toàn vẹn dữ liệu** — pipeline ingest chạy đúng trạng thái `PROCESSING → READY/ERROR`, upsert Qdrant idempotent, xoá cascade triệt để (SQLite + Qdrant + disk + lịch sử chat).
3. **Độ bền biên** — file lỗi/đặc biệt (mã hoá, scan, >25 MB, >400 trang, hỏng) bị từ chối đúng lý do mà không chặn file khác, không crash UI.

---

## 2. Phân tích tài liệu đầu vào

### 2.1 Danh mục tài liệu đầu vào

| Loại tài liệu | Tên | Phiên bản | Nguồn | Thông tin chính |
|---|---|---|---|---|
| **SRS/PRD** | PRD-CVD-001 | 0.1 | BA (Minh Tran) | Yêu cầu chức năng US-01…US-24, AC Given-When-Then, NFR, cổng phát hành G-01…G-19 |
| **User Stories** | US-CVD-001 | 0.1 | Product | AC chi tiết US-01…US-09 (bản rút gọn áp dụng), màn hình SCR-01…SCR-11 |
| **SAD (IEEE 1016-2009)** | SADD-CVD-001 | 1.0 | Architecture | **Tham khảo** — kiến trúc đầy đủ (PostgreSQL/Redis/MinIO/OIDC) đã bị IMP-CVD-003 đơn giản hoá; dùng để đối chiếu luồng nghiệp vụ, mã lỗi, quy tắc miền |
| **Kế hoạch triển khai** | IMP-CVD-003 | 1.0 | Development | **Nguồn sự thật của phạm vi**: stack Streamlit + Qdrant + SQLite, luồng upload/chat/xoá, cấu hình `.env`, hợp đồng hàm, ngưỡng chất lượng §9.3 |
| **Plan chi tiết** | Task breakdown S-01…S-26 | 1.0 | Development | Mã lỗi, Definition of Done, checklist thủ công S-25, bộ eval S-24 |
| **UI/UX** | UIUX_Blueprint_Design.md + html_design | 0.1 | Design | Tham khảo trạng thái UI, thông báo lỗi, cách trình bày nguồn |
| **Chuẩn** | IEEE 829-2008 | 2008 | IEEE | Cấu trúc tài liệu kiểm thử |

> **Lưu ý truy vết:** nhiều AC trong PRD/US (đăng nhập US-21, telemetry US-19/20, streaming nút Dừng, lịch sử hội thoại US-15…) đã bị **cắt bỏ** trong IMP-CVD-003 (xem bảng §1.3). Test plan chỉ truy vết tới những yếu requirement còn tồn tại trong bản đơn giản hoá; các phần còn lại được liệt kê ở §5.0.

### 2.2 Yêu cầu chức năng (FR) — trích từ IMP-CVD-003 §1.1 + US-01…US-09

| ID | Yêu cầu | Người dùng & hành vi mong đợi | US/AC nguồn | Ưu tiên |
|---|---|---|---|---|
| **FR-01** | Upload 1 PDF hợp lệ | File được lưu vào `data/uploads/{doc_id}.pdf`, ghi bản ghi SQLite `PROCESSING`, sau xử lý chuyển `READY`; xuất hiện trong danh sách | US-01 / AC-01.1 | P0 |
| **FR-02** | Từ chối file không hợp lệ ngay biên | Sai định dạng, quá `MAX_UPLOAD_MB`, quá `MAX_PAGES` → thông báo nêu tên tệp + giới hạn; không tạo bản ghi | US-01 / AC-01.2 | P0 |
| **FR-03** | Báo lý do tệp lỗi cụ thể | `.docx` → "chỉ hỗ trợ PDF"; PDF mã hoá → thông báo mật khẩu; PDF scan → `PDF_NO_TEXT` + trạng thái Lỗi; PDF hỏng → lỗi hỏng | US-03 / AC-03.1–3.3 | P0 |
| **FR-04** | Upload nhiều PDF | Xử lý tuần tự; một file lỗi không chặn các file còn lại | US-02 / AC-02.2 | P0 |
| **FR-05** | Trạng thái tài liệu | Chip `Đang xử lý / Sẵn sàng / Lỗi` kèm lý do + nút Xoá; cập nhật ngay sau upload (xử lý đồng bộ) | US-04 / AC-04.1–4.3 | P0 |
| **FR-06** | Danh sách tài liệu | Tên, số trang, trạng thái, ngày upload; còn nguyên sau refresh (SQLite) | US-05 / AC-05.1 | P0 |
| **FR-07** | Xoá tài liệu | Xác nhận → xoá khỏi SQLite, xoá points Qdrant theo `doc_id`, xoá file disk; biến mất khỏi danh sách | US-06 / AC-06.1 | P0 |
| **FR-08** | Xoá có hiệu lực với chat | Câu hỏi sau khi xoá không còn dùng/trích dẫn tài liệu đã xoá; lịch sử chat trong phiên bị xoá | US-06 / AC-06.2 | P0 |
| **FR-09** | Chat câu tự nhiên | Gửi câu trọn câu → nhận trả lời hoặc thông báo không tìm thấy | US-07 / AC-07.1 | P0 |
| **FR-10** | Chat chỉ bật khi có READY | 0 tài liệu `READY` → input disabled + thông báo "Tải PDF đầu tiên…" | US-07 / AC-07.2 | P0 |
| **FR-11** | Trả lời dựa trên tài liệu | Prompt strict, chỉ dùng ngữ cảnh `[S1]…`, không dùng kiến thức ngoài | US-08 / AC-08.1 | P0 |
| **FR-12** | Không tìm thấy | Không chunk đạt `SCORE_THRESHOLD` → thông báo cố định NOT_FOUND, **không gọi LLM**, không có nguồn | US-11 (PRD) | P0 |
| **FR-13** | Tổng hợp đa tài liệu | Nguồn có thể lấy từ ≥2 tài liệu; prompt yêu cầu tổng hợp + ghi nguồn | US-09 / AC-09.1 | P0 |
| **FR-14** | Hiển thị nguồn | Expander "Nguồn": tên file + trang + đoạn trích; lọc trùng nguồn, giới hạn `MAX_CHUNKS_PER_DOC` | US-10/13d (đơn giản hoá) | P0 |
| **FR-15** | Lịch sử chat phiên | Hỏi–đáp nhiều lượt trong `st.session_state`; mất khi refresh (thiết kế có chủ đích) | US-14 (đơn giản hoá) | P1 |
| **FR-16** | Cấu hình qua `.env` | Qdrant URL, model, API key, giới hạn upload, top-k, ngưỡng điểm; sai cấu hình → lỗi khởi động rõ ràng | US-24 (đơn giản hoá) | P0 |

### 2.3 Yêu cầu phi chức năng (NFR)

| ID | Yêu cầu | Nguồn |
|---|---|---|
| **NFR-01** | Upsert Qdrant idempotent: point ID = `uuid5(doc_id:chunk_index)`; re-index không tạo point trùng | IMP §5.2 |
| **NFR-02** | Qdrant restart → dữ liệu còn lại (Docker volume); tài liệu vẫn search được | IMP §9.2 |
| **NFR-03** | Qdrant dừng → banner "chưa sẵn sàng", không crash; bật lại hoạt động bình thường | IMP §8, S-25 4.8.3 |
| **NFR-04** | Lỗi LLM/Embedding → thông báo thân thiện "Tạm thời không trả lời được, thử lại"; không lộ key, không stack trace | IMP §0, §8 |
| **NFR-05** | Không log nội dung câu hỏi/trả lời/PDF; chỉ log ID, số trang, độ dài | Tasks DoD chung |
| **NFR-06** | Xử lý đồng bộ hoàn tất trong giới hạn 25 MB/400 trang; file vượt giới hạn bị từ chối nhanh, không treo | IMP §1.1, §10 |
| **NFR-07** | Unicode/tiếng Việt: text chuẩn hoá NFC; tên file dài/Unicode hiển thị không vỡ layout, không XSS | IMP §2, S-25 4.8.11 |
| **NFR-08** | Không auth → chỉ chạy localhost/mạng tin cậy; README cảnh báo rõ; không expose Internet | IMP §0 cảnh báo |
| **NFR-09** | `EMBEDDING_DIM` phải khớp model; đổi model/chiều → phải xoá + tạo lại collection và re-index | IMP §3.3 ghi chú |

### 2.4 Quy tắc nghiệp vụ (BR)

| ID | Quy tắc | Giá trị mặc định | Nguồn |
|---|---|---|---|
| **BR-01** | Chỉ chấp nhận PDF — kiểm tra đuôi **và** magic bytes `%PDF-` | — | IMP §2 luồng upload |
| **BR-02** | Giới hạn dung lượng | `MAX_UPLOAD_MB=25` | IMP §3.3 |
| **BR-03** | Giới hạn số trang | `MAX_PAGES=400` | IMP §3.3 |
| **BR-04** | PDF mã hoá → từ chối, không extract | `needs_pass=True` → mã lỗi | IMP §7.1 |
| **BR-05** | PDF không có text layer (mọi trang < `MIN_TEXT_CHARS_PER_PAGE`) → ERROR `PDF_NO_TEXT`, không bao giờ READY | `MIN_TEXT_CHARS_PER_PAGE=20` | IMP §2, §3.3 |
| **BR-06** | Chunk theo trang: 700 token, overlap 100; **không vượt ranh giới trang**; giữ `char_start/char_end`; không chunk rỗng | `CHUNK_SIZE_TOKENS=700`, `CHUNK_OVERLAP_TOKENS=100` | IMP §3.3, §7.2 |
| **BR-07** | Retrieval: top-k, ngưỡng điểm, đa dạng nguồn, giới hạn ngân sách ngữ cảnh | `TOP_K=8`, `SCORE_THRESHOLD=0.25`, `MAX_CHUNKS_PER_DOC=4`, `MAX_CONTEXT_CHARS=24000` | IMP §3.3 |
| **BR-08** | Point ID deterministic theo `(doc_id, chunk_index)` | `uuid5(NAMESPACE_URL, "{doc_id}:{chunk_index}")` | IMP §5.2 |
| **BR-09** | Xoá cascade + xoá lịch sử chat trong session | Qdrant filter delete → SQLite DELETE → disk delete → clear `st.session_state.messages` | IMP §2 luồng xoá |
| **BR-10** | Embedding batch + retry | `EMBEDDING_BATCH_SIZE=64`, retry 2 lần, có timeout | IMP §3.1, S-09 |

### 2.5 Ngưỡng chất lượng RAG (QLT) — IMP §9.3

| ID | Chỉ số | Ngưỡng |
|---|---|---|
| **QLT-01** | Câu trả lời đúng nội dung (trong tài liệu) | ≥ 8/10 câu |
| **QLT-02** | Câu trả lời đa tài liệu có nguồn từ ≥ 2 tài liệu | ≥ 8/10 câu |
| **QLT-03** | Not-found đúng (câu ngoài phạm vi, không bịa) | ≥ 9/10 câu |
| **QLT-04** | Nguồn đúng tài liệu/trang | ≥ 9/10 câu có nguồn |

### 2.6 Phần tử thiết kế (from IMP/SADD) → mục tiêu kiểm thử

**Phân rã module (IMP §4) ↔ task ↔ test:**

| Module | Trách nhiệm | Task | Test chính |
|---|---|---|---|
| `config.py` | Đọc `.env`, validate, tạo `data/` | S-03 | UT-08 |
| `db.py` | SQLite schema + CRUD `documents` | S-04 | UT-09, IT-09 |
| `pdf.py` | Validate (magic/size/pages/needs_pass) + extract theo trang NFC | S-06, S-07 | UT-04…07 |
| `chunking.py` | Chunk theo trang + overlap + offset | S-08 | UT-01…03 |
| `embeddings.py` | Embed batch, retry, timeout | S-09 | IT-10 |
| `vector_store.py` | ensure_collection, upsert, search, delete | S-05, S-10 | IT-01…04 |
| `ingest.py` | Orchestrate upload → READY/ERROR | S-11, S-13 | IT-05…08 |
| `rag.py` + `prompts.py` | Build context `[S#]`, prompt strict, NOT_FOUND | S-15, S-17, S-21 | UT-11/12, IT-11/12 |
| `llm.py` | Gọi LLM streaming | S-16 | IT-12 |
| `errors.py` | Mã lỗi + thông điệp tiếng Việt | S-14 | UT-10 |
| `main.py` / `ui.py` | Trang duy nhất: sidebar + chat | S-12, S-18…S-20 | ST-01…ST-18, UI-01…07 |

**Máy trạng thái tài liệu:** `PROCESSING → READY` hoặc `PROCESSING → ERROR(error_code)`; xoá bỏ bản ghi khỏi bảng. Mọi chuyển trạng thái được kiểm chứng qua IT-05…IT-09.

**Mô hình dữ liệu:** SQLite `documents(id, file_name, stored_path, size_bytes, page_count, status, error_code, created_at, processed_at)`; Qdrant collection `document_chunks` (cosine, `EMBEDDING_DIM`, payload index `doc_id` KEYWORD) — payload mỗi point gồm `doc_id, file_name, page, chunk_index, text, char_start, char_end`. Kiểm tra schema qua IT-01, IT-02.

### 2.7 Phần tử UI/UX (bản tối thiểu — IMP §8)

| UI thành phần | Trạng thái bắt buộc | Screen ref | Test |
|---|---|---|---|
| Sidebar uploader + danh sách | rỗng (hướng dẫn) / processing / ready / error (+lý do, nút Xoá) | SCR-02/03/04/05 | ST-01, ST-07, UI-01 |
| Chip trạng thái | biểu tượng + nhãn (`Đang xử lý`/`Sẵn sàng`/`Lỗi`) | SCR-04/05/11 | UI-01 |
| Nút Xoá + confirm | xác nhận/huỷ | SCR-06 | ST-06 |
| Chat input | disabled khi 0 READY / enabled khi có READY | SCR-02/03 | ST-07, UI-02 |
| Lịch sử chat | hỏi–đáp nhiều lượt trong phiên | SCR-05 | ST-03, ST-18 |
| Expander "Nguồn" | tên file + trang + đoạn trích; không nguồn khi NOT_FOUND | IMP §8 | ST-03, ST-04, UI-04 |
| NOT_FOUND card | thẻ trung tính, thông báo cố định, gợi ý | SCR-05 | ST-04, UI-03 |
| Lỗi LLM/thiếu Qdrant | thông báo thân thiện, không crash, không lộ key | component | ST-14/15, UI-03 |
| Dòng nhắc | "AI có thể sai. Kiểm tra lại tài liệu." | IMP §8 | UI-07 |

### 2.8 Giao diện thành phần (adapter contracts) — thay cho mục "API testing" của template

Không có REST API công khai; hợp đồng kiểm thử là **hàm Python** (IMP §7) và **endpoint bên ngoài**:

| Giao tiếp | Hợp đồng | Kiểm thử |
|---|---|---|
| `pdf.inspect_pdf(path, max_pages) → PdfInfo` | `page_count, needs_pass, is_pdf` | UT-04…06 |
| `pdf.extract_pages(path) → list[PageText]` | NFC, bỏ trang rỗng | UT-07 |
| `chunking.chunk_pages(pages, size_tokens, overlap_tokens) → list[Chunk]` | không vượt trang, offset đúng | UT-01…03 |
| `vector_store.upsert_chunks(doc_id, file_name, chunks, vectors)` | idempotent, payload đầy đủ | IT-02 |
| `vector_store.search(query_vector, limit, score_threshold, doc_ids)` | thứ tự điểm, filter, threshold | IT-03 |
| `vector_store.delete_document(doc_id)` | xoá hết point theo doc | IT-04 |
| `embeddings.*` (OpenAI-compatible) | batch 64, retry 2, timeout, lỗi rõ | IT-10 |
| `rag.answer_question(question, history, selected_doc_ids)` | `(answer, hits)`; no-hit → `(NOT_FOUND, [])`, **không gọi LLM** | IT-11, IT-12 |
| `llm.*` (OpenAI-compatible streaming) | token stream; lỗi API có thông báo | IT-12, ST-13 |

### 2.9 Đánh giá rủi ro đầu vào

| Risk ID | Mô tả rủi ro | Likelihood (1–5) | Impact (1–5) | Score | Mitigation / Test |
|---|---|---|---|---|---|
| **RISK-01** | LLM bịa câu trả lời khi không có ngữ cảnh đủ mạnh | 4 | 5 | 20 | Prompt strict + threshold + NOT_FOUND; eval QLT-01…03 (EV-01…03) |
| **RISK-02** | PDF scan (chỉ ảnh, không text layer) chiếm tỷ lệ cao trong PDF thật | 4 | 4 | 16 | BR-05 từ chối sớm, thông báo rõ; ST-02, ST-17 |
| **RISK-03** | `EMBEDDING_DIM` lệch model → search thất bại toàn bộ | 3 | 5 | 15 | NFR-09, UT-08, quy trình re-index trong README (S-26) |
| **RISK-04** | Xử lý đồng bộ bị treo/timeout với PDF lớn gần giới hạn | 3 | 4 | 12 | NFR-06, PF-01; từ chối nhanh ở biên |
| **RISK-05** | No-auth bị expose ra Internet vô tình | 3 | 5 | 15 | NFR-08: kiểm tra README, cổng lắng nghe, SEC-04 |
| **RISK-06** | Xoá không triệt để → chat sau vẫn trích dẫn dữ liệu đã xoá | 2 | 5 | 10 | BR-09 xoá cascade; IT-04, ST-06 |
| **RISK-07** | Re-index tạo point trùng → nguồn lặp, chi phí tăng | 2 | 3 | 6 | BR-08 uuid5 idempotent; IT-02 |
| **RISK-08** | Streamlit rerun vô tình re-ingest file còn trong uploader | 2 | 3 | 6 | Thiết kế trong S-11; ST-01 (1.6), ST-02 (2.5 không dedupe là đúng kiến trúc) |
| **RISK-09** | Ollama/model local chậm hoặc bận → chat chờ lâu | 3 | 3 | 9 | PF-02 đo p90; thông báo lỗi timeout; ghi chú cấu hình |
| **RISK-10** | Qdrant volume mất → mất toàn bộ vector | 1 | 4 | 4 | Docker volume; ST-17 (4.8.12); khuyến nghị backup `data/` |

---

## 3. Cấu trúc tài liệu — ánh xạ IEEE 829-2008

| Section tài liệu này | IEEE 829 clause | Nội dung |
|---|---|---|
| §4.1 | 5.1 | Test Plan Identifier |
| §4.2 | 5.2 | Introduction |
| §4.3 | 5.3 | Test Items |
| §4.4 | 5.4 | Features to be Tested |
| §4.5 | 5.5 | Features Not to be Tested |
| §4.6 | 5.6 | Approach (mức kiểm thử, loại kiểm thử, kịch bản, chu kỳ) |
| §4.7 | 5.7 | Item Pass/Fail Criteria |
| §4.8 | 5.8 | Suspension & Resumption Criteria |
| §4.9 | 5.9 | Test Deliverables |
| §4.10 | 5.10 | Testing Tasks |
| §4.11 | 5.11 | Environmental Needs |
| §4.12 | 5.12 | Responsibilities |
| §4.13 | 5.13 | Staffing & Training |
| §4.14 | 5.14 | Schedule |
| §4.15 | 5.15 | Risks & Contingencies |
| §4.16 | 5.16 | Approvals |
| §5 | — | Ma trận truy vết đầy đủ (REQ ↔ TC ↔ Task ↔ US/AC) |
| §6 | — | Phụ lục: dữ liệu thử nghiệm, bộ eval, danh mục mã lỗi |

---

## 4. Nội dung Kế hoạch Kiểm thử

### 4.1 §1.0 Test Plan Identifier

| Thuộc tính | Giá trị |
|---|---|
| Document ID | TP-CVD-004 |
| Phiên bản | 1.0 (Draft) |
| Ngày phát hành | 2026-10-23 |
| Trạng thái | Draft — chờ review QA/Product |
| Phân loại | Internal — tài liệu nội bộ |
| Biên soạn | QA Team (hỗ trợ bởi Principal Architect) |
| Phê duyệt | QA Lead / Product Owner (xem §4.16) |
| Sản phẩm kiểm thử | Ứng dụng "Upload PDF & Chat với AI" (monolith Streamlit, Qdrant, SQLite) — build theo IMP-CVD-003 |
| Chu kỳ áp dụng | Theo milestone M1–M4 của IMP §12 |

### 4.2 §2.0 Introduction

#### 2.1 Mục đích

- Định nghĩa chiến lược kiểm thử toàn diện cho bản triển khai đơn giản hoá trong IMP-CVD-003.
- Truy vết 100% yêu cầu FR/NFR/BR/QLT còn tồn tại tới test case và task phát triển (S-01…S-26).
- Chốt tiêu chí vào/ra cho từng mức kiểm thử và các cổng nghiệm thu trước demo.
- Làm rõ phạm vi **không** kiểm thử (đã cắt so với PRD đầy đủ) để tránh hiểu nhầm.

#### 2.2 Phạm vi

**Trong phạm vi:**

- Kiểm thử chức năng toàn bộ FR-01…FR-16: upload (1/nhiều file), validate PDF, extract/chunk/embed/upsert, danh sách, chat, nguồn, NOT_FOUND, xoá, cấu hình.
- Kiểm thử hợp nhất (integration) Qdrant + SQLite + pipeline ingest, chạy với Qdrant Docker thật.
- Kiểm thử thủ công UI trên browser cho 6 luồng chính + 12 trạng thái biên (bám checklist S-25).
- Đánh giá chất lượng RAG bằng bộ eval 20–30 câu (S-24) với ngưỡng QLT-01…04.
- Kiểm thử hồi quy: pytest + integration + checklist smoke + eval.
- Kiểm thử bảo mật **mức tối thiểu** đúng phạm vi no-auth (SEC-01…04: không lộ key/log/XSS, hướng dẫn triển khai an toàn).
- Kiểm thử hiệu năng **quan sát** (PF-01…03) ở quy mô 1 người dùng demo.

**Ngoài phạm vi:**

| Hạng mục | Lý do |
|---|---|
| Đăng nhập/phân quyền/403/hết phiên (US-21, SCR-01/08/10) | Đã cắt khỏi kiến trúc (no-auth), sẽ thêm nếu đưa ra mạng nội bộ |
| Telemetry/đánh giá 👍👎, báo cáo MET-001…005 (US-19/20) | Không có trong bản đơn giản hoá |
| Load/stress/endurance đa người dùng (US-24 đầy đủ) | Mục tiêu demo 1 người dùng; xem PF giới hạn |
| Penetration testing | Do đội bảo mật chuyên trách, ngoài phạm vi QA này |
| OCR PDF scan | Tính năng không tồn tại; chỉ kiểm tra báo lỗi đúng |
| Lịch sử hội thoại bền/đa phiên, chọn phạm vi tài liệu ở UI, source viewer mở đúng trang PDF | Hạng mục "sau" của IMP §13 |
| Kiểm thử nội bộ của LLM/Embedding provider (OpenAI/Ollama) | Trách nhiệm nhà cung cấp; chỉ kiểm tra hợp đồng adapter |

#### 2.3 Mục tiêu kiểm thử

| Objective ID | Mục tiêu | Tiêu chí thành công | Truy vết |
|---|---|---|---|
| OBJ-01 | Xác nhận 100% FR còn tồn tại hoạt động đúng AC | 100% FR-01…16 có ≥1 TC pass | §5 |
| OBJ-02 | Xác nhận pipeline dữ liệu toàn vẹn (ingest → search → delete) | Toàn bộ IT-01…09 pass với Qdrant thật | NFR-01/02, BR-08/09 |
| OBJ-03 | Xác nhận chất lượng RAG đạt ngưỡng | QLT-01…04 đạt (EV-01…04) | §2.5 |
| OBJ-04 | Xác nhận hành vi biên an toàn | 12/12 trạng thái biên S-25 pass hoặc bug đã ghi nhận | FR-02/03, BR-01…05 |
| OBJ-05 | Xác nhận lỗi kỹ thuật được che và khôi phục | Không traceback trên UI; Qdrant/LLM down có thông báo; NFR-03/04 | ST-14/15 |
| OBJ-06 | Xác nhận triển khai an toàn ở mức demo | SEC-01…04 pass; README có cảnh báo no-auth | NFR-05/08 |

#### 2.4 Tài liệu tham chiếu

| Tài liệu | Phiên bản | Nguồn |
|---|---|---|
| IMP-CVD-003 — Kế hoạch triển khai (Qdrant) | 1.0 | Development |
| Task breakdown S-01…S-26 | 1.0 | Development |
| PRD-CVD-001 | 0.1 | BA |
| US-CVD-001 (US-01…US-09 rút gọn) | 0.1 | Product/BA |
| SADD-CVD-001 (tham khảo, đã đơn giản hoá) | 1.0 | Architecture |
| UIUX_Blueprint_Design.md (tham khảo) | 0.1 | Design |
| Checklist thủ công S-25 | — | QA |
| IEEE 829-2008 | 2008 | IEEE |

### 4.3 §3.0 Test Items

#### 3.1 Phần mềm được kiểm thử

| Item ID | Tên | Phiên bản | Nguồn | Mô tả |
|---|---|---|---|---|
| SI-01 | Ứng dụng Streamlit `app/main.py` | build theo S-01…S-21 | Dev | Trang duy nhất sidebar + chat |
| SI-02 | Backend modules (`config, db, pdf, chunking, embeddings, vector_store, ingest, llm, rag, errors`) | — | Dev | Thư viện Python nội bộ |
| SI-03 | Qdrant v1.12.4 (Docker) | 1.12.4 | docker-compose.yml | Collection `document_chunks`, volume `qdrant_data` |
| SI-04 | SQLite `data/app.db` | — | Dev | Bảng `documents` |
| SI-05 | PDF gốc trong `data/uploads/` | — | Dev | Lưu `{doc_id}.pdf` |
| SI-06 | Cấu hình `.env` | — | Dev | Qdrant URL, model, giới hạn, threshold |
| SI-07 | README/runbook | — | S-26 | Điều kiện nghiệm thu "chạy được ≤15 phút" |

#### 3.2 Artifact kiểm thử được cung cấp

| Artifact ID | Tên | Định dạng | Nguồn |
|---|---|---|---|
| TA-01 | Unit + integration tests | `pytest` (`tests/`, `tests/eval/fixtures/`) | QA/Dev (S-22, S-23) |
| TA-02 | Bộ eval 30 câu + runner + báo cáo | JSONL + script (`eval.py`) + Markdown | QA (S-24) |
| TA-03 | Checklist kiểm thử thủ công | `docs/testing/manual-checklist.md` | QA (S-25) |
| TA-04 | Bộ PDF đặc chủng (adversarial) | files (§6-A) | QA |
| TA-05 | Môi trường Docker Qdrant + `.env` mẫu | docker-compose.yml, .env.example | Dev (S-01, S-02) |
| TA-06 | Stub embedding/LLM cho unit test | fixture/mock cục bộ | Dev (không gọi mạng thật trong unit test — DoD) |

### 4.4 §4.0 Features to be Tested

#### 4.1 Ma trận ưu tiên dựa trên rủi ro

Score = Likelihood × Impact của rủi ro liên quan (§2.9).

| Ưu tiên | Tính năng | Rủi ro liên quan | Score | Test chính |
|---|---|---|---|---|
| **High** | Chat grounded + NOT_FOUND + nguồn (FR-11…14) | RISK-01 (LLM bịa) | 20 | EV-01…04, IT-11/12, ST-03/04/05 |
| **High** | Validate PDF + thông báo lỗi (FR-02/03) | RISK-02 (PDF scan) | 16 | UT-04…10, IT-06/07, ST-02/16/17 |
| **High** | Xoá cascade triệt để (FR-07/08) | RISK-06 (dữ liệu còn sót) | 10 | IT-04/09, ST-06 |
| **High** | Cấu hình đúng (FR-16, NFR-09) | RISK-03 (dim lệch) | 15 | UT-08, IT-01, quy trình re-index |
| **Medium** | Pipeline ingest + đa file (FR-01/04/05/06) | RISK-04/08 | 12/6 | IT-05…09, ST-01/02 |
| **Medium** | Bền vững hạ tầng (NFR-02/03) | RISK-10 | 4 | ST-14/15/17 |
| **Medium** | Idempotency upsert (NFR-01) | RISK-07 (point trùng) | 6 | UT-13, IT-02 |
| **Low** | UI chi tiết (FR-15, UI-*), Unicode (NFR-07) | — | — | UI-01…07, SEC-03 |

#### 4.2 Ma trận tính năng × loại kiểm thử

| Tính năng | Unit | Integration | System/Manual | Eval | Perf | Security | UI |
|---|---|---|---|---|---|---|---|
| Upload PDF (FR-01) | ✓ | ✓ | ✓ | — | ✓ | — | ✓ |
| Validate PDF (FR-02/03) | ✓ | ✓ | ✓ | — | — | — | ✓ |
| Multi-file (FR-04) | — | ✓ | ✓ | — | — | — | ✓ |
| Trạng thái + danh sách (FR-05/06) | ✓ | ✓ | ✓ | — | — | — | ✓ |
| Xoá (FR-07/08) | — | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| Chat + nguồn + NOT_FOUND (FR-09…14) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Lịch sử chat (FR-15) | — | — | ✓ | — | — | — | ✓ |
| Cấu hình (FR-16, NFR-09) | ✓ | ✓ | ✓ | — | — | ✓ | ✓ |
| Bền vững Qdrant (NFR-02/03) | — | ✓ | ✓ | — | — | — | — |

#### 4.3 Mô tả chi tiết tính năng

| Feature ID | Tên | Mô tả | Điểm kiểm được | AC chính |
|---|---|---|---|---|
| F-01 | Upload & ingest | 1/nhiều PDF → lưu → extract → chunk → embed → Qdrant → READY/ERROR | trạng thái, page_count, points, file disk | AC-01.1, AC-02.2 |
| F-02 | Kiểm tra PDF | Đuôi + magic + size + pages + needs_pass + text layer | 6 lỗi từ chối đúng lý do | AC-01.2, AC-03.1–3.3 |
| F-03 | Danh sách | Tên/trang/trạng thái/ngày; còn sau refresh | dữ liệu đúng SQLite | AC-05.1 |
| F-04 | Xoá | Confirm → Qdrant + SQLite + disk + chat history | 4 lớp đều sạch | AC-06.1/06.2 |
| F-05 | Chat grounded | chỉ ngữ cảnh `[S1]`, đúng ngôn ngữ, không bịa | eval 30 câu | AC-08.1, AC-13b.1 |
| F-06 | Nguồn | Expander tên file + trang + trích; dedupe, ≤4 chunk/doc | nguồn đúng | AC-10.1 |
| F-07 | NOT_FOUND | Không hit → thông báo cố định, không gọi LLM | message + 0 nguồn | — (BR-07 IMP) |
| F-08 | UI trạng thái | Chip, input disable/enable, streaming, dòng nhắc | 8 trạng thái IMP §8 | AC-04.x, AC-07.2 |

### 4.5 §5.0 Features Not to be Tested

| Feature ID | Tính năng | Lý do | Rủi ro chấp nhận | Kế hoạch tương lai |
|---|---|---|---|---|
| NT-01 | Auth/OIDC/403/hết phiên | Không có trong kiến trúc | Cao nếu expose Internet — đã có SEC-04 + cảnh báo README | IMP §13-6 khi lên mạng nội bộ |
| NT-02 | Telemetry, 👍/👎, MET-* | Không có UI/logic | Không ảnh hưởng demo | Sau go/no-go |
| NT-03 | Load test đa người dùng, endurance 24h | Quy mô demo 1 user | Đã giới hạn 25 MB/400 trang | Khi chuyển background worker |
| NT-04 | OCR | Chưa hỗ trợ, chỉ báo lỗi | Người dùng bị từ chối file scan — chấp nhận | IMP §13-7 |
| NT-05 | Chọn phạm vi tài liệu ở UI (`selected_doc_ids`) | API có nhưng UI chưa; xếp hạng "sau" | Thấp | IMP §13-3 (IT-03 vẫn test filter ở tầng vector_store) |
| NT-06 | Provider LLM/Embedding nội tại | Trách nhiệm nhà cung cấp | Thấp | Hợp đồng qua IT-10/12 |
| NT-07 | Kiến trúc đầy đủ của SADD (PostgreSQL/Redis/MinIO/worker/SSE) | Đã bị thay thế bởi IMP-CVD-003 | — | Nếu quay lại thiết kế đầy đủ |
| NT-08 | WCAG 2.1 AA đầy đủ | Streamlit mặc định, ngoài tầm kiểm soát QA ở bản demo | Trung bình | Áp dụng lại khi có UI tuỳ chỉnh (IMP §13-4) |

### 4.6 §6.0 Approach

#### 6.1 Các mức và loại kiểm thử

##### 6.1.1 Unit Testing

| Thuộc tính | Giá trị |
|---|---|
| Responsible | Developer (mỗi task tự test) |
| Tool | `pytest` + fixtures/mock; **không gọi mạng thật** trong unit test (DoD chung) |
| Coverage target | ≥ 80% line cho module không phải UI (`config, db, pdf, chunking, embeddings, vector_store, ingest, rag, llm, errors`) |
| Entry | Code hoàn thành, pass `ruff format`/`ruff check` |
| Exit | Toàn bộ unit test xanh; coverage đạt mốc |
| Focus | Hàm thuần: chunking, validation, prompt builder, error mapping, CRUD, UUID |

**Danh sách test case Unit:**

| TC | Test | Dữ liệu/Điều kiện | Kết quả mong đợi | BR/REQ |
|---|---|---|---|---|
| UT-01 | `chunk_pages` không vượt trang | trang có 2000 ký tự | các Chunk đều `page` của trang sinh ra; không chunk chứa nội dung 2 trang | BR-06 |
| UT-02 | overlap + offset đúng | 2 chunk liền nhau | `char_start` chunk sau ≤ `char_end` chunk trước; offset nằm trong trang | BR-06 |
| UT-03 | trang ngắn/rỗng | `MIN_TEXT_CHARS_PER_PAGE` | không sinh chunk rỗng; trang bỏ qua được | BR-05/06 |
| UT-04 | `inspect_pdf` sai định dạng | file text giả, file đổi đuôi .pdf | `is_pdf=False` hoặc mã lỗi đúng | BR-01 |
| UT-05 | PDF mã hoá | fixture PDF có mật khẩu | `needs_pass=True` → mã lỗi encrypted | BR-04 |
| UT-06 | vượt số trang | fixture > MAX_PAGES | báo lỗi/trả cờ vượt trang | BR-03 |
| UT-07 | `extract_pages` | PDF đa trang Unicode | NFC hoá; trang rỗng bị bỏ; `PageText.page` đúng thứ tự | NFR-07 |
| UT-08 | `config.py` | thiếu `OPENAI_API_KEY`, `EMBEDDING_DIM≤0`, `data/` chưa có | lỗi rõ từng trường; tự tạo `data/` | NFR-09, FR-16 |
| UT-09 | CRUD `documents` | insert/list/update status/delete | đúng vòng đời trạng thái; timestamp ISO8601 UTC | FR-05/06 |
| UT-10 | map mã lỗi | mỗi mã lỗi (§6-C) | thông điệp tiếng Việt đúng, nêu tên file + hành động | FR-03 |
| UT-11 | Prompt builder | hits giả | đánh số `[S1]…`; cắt ở `MAX_CONTEXT_CHARS`; system prompt strict | FR-11 |
| UT-12 | Format nguồn + dedupe | hits trùng, >4/doc | lọc trùng; tối đa `MAX_CHUNKS_PER_DOC` mỗi tài liệu | FR-14, BR-07 |
| UT-13 | Point ID ổn định | cùng doc_id + chunk_index | `uuid5` cho ra cùng ID mỗi lần | BR-08 |

##### 6.1.2 Integration Testing

| Thuộc tính | Giá trị |
|---|---|
| Responsible | Dev + QA |
| Tool | `pytest` chạy với **Qdrant Docker thật** (`docker compose up -d` trước suite); embedding/LLM dùng local stub (server stub cục bộ / WireMock) hoặc Ollama |
| Scope | Qdrant collection lifecycle, SQLite, pipeline ingest E2E, adapter embedding/LLM |
| Entry | Unit tests xanh; Qdrant healthy |
| Exit | Toàn bộ IT pass |

**Danh sách test case Integration:**

| TC | Test | Kết quả mong đợi | REQ/BR |
|---|---|---|---|
| IT-01 | `ensure_collection` lần đầu/lần n | collection `document_chunks` được tạo đúng `EMBEDDING_DIM`, cosine, payload index `doc_id` KEYWORD; chạy lần 2 không lỗi | NFR-01, NFR-09 |
| IT-02 | `upsert_chunks` + re-upsert | point đúng payload (`doc_id, file_name, page, chunk_index, text, char_start/char_end`); chạy lại → **số point không đổi** | NFR-01, BR-08 |
| IT-03 | `search` | đúng thứ tự điểm giảm dần; lọc `doc_ids`; bỏ hit dưới `score_threshold`; respects `top_k` | BR-07 |
| IT-04 | `delete_document` | 0 point còn `doc_id` đó; các doc khác nguyên | FR-07, BR-09 |
| IT-05 | Ingest E2E (PDF hợp lệ) | SQLite `READY` + `page_count`; Qdrant có point; file tồn tại `data/uploads/{doc_id}.pdf` | FR-01 |
| IT-06 | Ingest PDF scan | ERROR `PDF_NO_TEXT`, **không** có point, không READY | BR-05 |
| IT-07 | Ingest encrypted/corrupt/oversize/đuôi sai | mỗi lỗi đúng mã (§6-C), bản ghi không rơi vào trạng thái treo | FR-02/03, BR-01…04 |
| IT-08 | Ingest nhiều file (1 lỗi giữa) | file sau vẫn READY; file lỗi có mã riêng | FR-04 |
| IT-09 | Nhất quán SQLite ↔ Qdrant sau xoá | cả 2 bên đều sạch | FR-07 |
| IT-10 | Embedding adapter | batch ≤64; retry 2 lần khi 5xx; timeout có thông báo; lỗi không crash | BR-10, NFR-04 |
| IT-11 | `answer_question` không hit | trả `(NOT_FOUND, [])`; **LLM spy không được gọi** | FR-12 |
| IT-12 | Chat E2E với LLM stub/Ollama | trả lời + hits; ngôn ngữ trả lời = câu hỏi; lỗi endpoint → thông báo thân thiện | FR-09/11, NFR-04 |

##### 6.1.3 System Testing (Manual UI)

Chạy trên browser thực (Chrome mới nhất), theo đúng các bước của [S-25 checklist](../implement/tasks/S-25-manual-test-checklist.md); xuất kết quả vào `docs/testing/manual-checklist.md`.

| TC | Luồng | Bước chính | Kết quả mong đợi | REQ |
|---|---|---|---|---|
| ST-01 | Upload 1 PDF | Kéo-thả `hop-dong.pdf`; chờ xử lý; kiểm tra `data/uploads/`, Qdrant dashboard, refresh trang | Tài liệu xuất hiện → chip **Sẵn sàng**; đúng số trang/dung lượng; có point Qdrant; còn trong danh sách sau refresh | FR-01, FR-05/06 |
| ST-02 | Upload nhiều + file lỗi | Chọn 2 PDF hợp lệ + 1 `.docx` + 1 PDF scan + tải lại file trùng | File `.docx` bị chặn; PDF scan → row **Lỗi** `PDF_NO_TEXT`; 2 PDF hợp lệ **Sẵn sàng** không bị dừng; tải lại trùng → tạo doc mới (thiết kế, không dedupe) | FR-03/04 |
| ST-03 | Chat trong phạm vi | Hỏi "Hạn chót nộp hồ sơ là ngày nào?"; mở expander Nguồn; hỏi tiếp câu có đại từ; hỏi tiếng Việt có dấu; quan sát streaming | Trả lời đúng có `[S1]`; nguồn đúng file + trang; giữ ngữ cảnh hội thoại; không lỗi encoding; trả lời hiện dần, không treo | FR-09/11/14/15 |
| ST-04 | Ngoài phạm vi | Hỏi "Giá cổ phiếu VNM hôm nay?", "Thủ đô nước Pháp?", câu nửa đúng nửa ngoài | Thông báo cố định "Không tìm thấy thông tin…" nguyên văn; không nguồn; không bịa phần ngoài | FR-12 |
| ST-05 | Đa tài liệu | Upload ≥2 tài liệu READY; hỏi câu cần cả 2; hỏi câu chỉ liên quan 1 file | Trả lời tổng hợp có nguồn từ ≥2 tài liệu; nguồn đúng file; không tài liệu nào chiếm hết nguồn | FR-13 |
| ST-06 | Xoá | Bấm Xoá → Huỷ; Xoá → Xác nhận; kiểm tra Qdrant, `data/uploads/`; hỏi lại câu cũ; xoá doc cuối | Huỷ → còn nguyên; Xác nhận → biến mất danh sách, hết point Qdrant, hết file disk; lịch sử chat clear, câu hỏi sau không nhắc file đã xoá; xoá doc cuối → chat disabled | FR-07/08, FR-10 |
| ST-07…ST-18 | Trạng thái biên (4.8.1…4.8.12) | Chạy đủ 12 mục biên của checklist S-25 §4.8 | Mỗi mục đúng kỳ vọng; không crash, không traceback; không lộ key | FR-10, FR-02/03, NFR-03/04/07 |

##### 6.1.4 Acceptance Testing (UAT/demo)

Chạy bởi Product/BA trên môi trường QA, chạy theo checklist nghiệm thu IMP §9.2. Đánh dấu Pass/Fail từng mục; toàn bộ mục bắt buộc phải pass trước demo M4.

| TC | Tiêu chí nghiệm thu (IMP §9.2) | Bằng chứng |
|---|---|---|
| UAT-01 | Upload hợp lệ → READY | manual-checklist 4.2 |
| UAT-02 | Nhiều PDF; lỗi 1 không chặn | 4.3 |
| UAT-03 | .docx / mã hoá / scan → đúng lý do | 4.3, 4.8 |
| UAT-04 | Danh sách đủ tên/trang/trạng thái/ngày | 4.2 |
| UAT-05 | Chat vô hiệu khi 0 READY | 4.8.1/4.8.2 |
| UAT-06 | Câu trong tài liệu → đúng + nguồn file/trang | EV-01 + 4.4 |
| UAT-07 | Câu ngoài phạm vi → NOT_FOUND, không bịa | EV-03 + 4.5 |
| UAT-08 | Câu đa tài liệu → tổng hợp + nguồn cả 2 | EV-02 + 4.6 |
| UAT-09 | Xoá → sạch 3 kho + chat không nhắc lại | 4.7 |
| UAT-10 | Qdrant restart → dữ liệu còn | 4.8.12 |
| UAT-11 | README đủ chạy ≤15 phút | S-26 review bởi người mới |

##### 6.1.5 Regression Testing

| Thuộc tính | Giá trị |
|---|---|
| Trigger | Mỗi PR (smoke unit), mỗi merge (integration), trước demo/final build (đầy đủ) |
| Frequency | Theo chu kỳ §6.2 |
| Suite | REG-01: pytest unit (~13 nhóm TC) · REG-02: IT-01…12 · REG-03: smoke manual 6 luồng (45–60 phút) · REG-04: eval 30 câu |

##### 6.1.6 Performance Testing (quy mô demo)

| TC | Kịch bản | Khoảng đo | Mục tiêu (đề xuất QA — chờ xác nhận với OQ-011) | REQ |
|---|---|---|---|---|
| PF-01 | Ingest PDF 30 trang / PDF sát 25 MB–400 trang | thời gian từ upload tới READY | hoàn tất trong 1 request, không timeout proxy; ghi nhận baseline | NFR-06 |
| PF-02 | Chat: p90 thời gian gửi → token đầu | 10 câu lặp | phụ thuộc model; ghi nhận baseline (Ollama local) | FR-09 |
| PF-03 | Search Qdrant độ trễ | 100 query | < 1 s (không tính LLM) | BR-07 |
| PF-04 | Upload file biên (25.1 MB / 401 trang) | bị từ chối trước khi xử lý | từ chối nhanh (<5 s), không treo UI | FR-02 |

> Không chạy load/stress/endurance đa người dùng (NT-03).

##### 6.1.7 Security Testing (mức tối thiểu đúng phạm vi no-auth)

| TC | Test | Kết quả mong đợi | REQ |
|---|---|---|---|
| SEC-01 | Sai API key → UI | thông báo cấu hình/thử lại; **không hiện key, không stack trace** | NFR-04 |
| SEC-02 | Hội thoại/file trong log | terminal + DevTools chỉ có ID/độ dài/số trang, không nội dung | NFR-05 |
| SEC-03 | Tên file độc hại (`<script>`, `../`, tên dài Unicode) | hiển thị escape đúng, không XSS, không path traversal ngoài `data/uploads/`, không vỡ layout | NFR-07 |
| SEC-04 | Triển khai an toàn | README cảnh báo no-auth + hướng dẫn VPN/reverse proxy; Streamlit mặc định không mở `--server.enableCORS` rộng; chỉ lắng nghe cổng nội bộ | NFR-08 |

##### 6.1.8 UI/UX Testing (bản tối thiểu)

| TC | Test | Kết quả mong đợi |
|---|---|---|
| UI-01 | Chip trạng thái đủ 3 giá trị, có icon + nhãn | đúng IMP §8 |
| UI-02 | Chat input disable/enable theo READY | đúng điều kiện |
| UI-03 | Thông báo lỗi thân thiện tiếng Việt | đúng danh mục §6-C |
| UI-04 | Expander Nguồn: file + trang + trích; NOT_FOUND không có nguồn | đúng |
| UI-05 | History đa lượt hiển thị đúng trong phiên | đúng |
| UI-06 | Tên file dài/Unicode không vỡ layout | đúng |
| UI-07 | Dòng nhắc "AI có thể sai…" luôn hiển thị | đúng |

> Accessibility WCAG AA đầy đủ nằm ngoài phạm vi (NT-08).

#### 6.2 Chiến lược thực thi

| Cycle | Thời điểm | Nội dung | Bằng chứng ra |
|---|---|---|---|
| C0 — Smoke mỗi PR | khi merge từng task | unit liên quan + lint + không log nhạy cảm (DoD) | log CI/terminal |
| C1 — Integration | sau milestone M1 (xong S-11) | IT-01…IT-10 với Qdrant Docker; confirm đủ points bằng script/Qdrant dashboard | kết quả pytest integration |
| C2 — System partial | sau M2 (xong S-14) | ST-01, ST-02, ST-07…ST-18 (biên upload) | checklist 4.1–4.3 + 4.8 |
| C3 — System full + Eval | sau M3 (xong S-21) | ST-03…ST-06, UI-01…07, EV-01…04, PF-01…04, SEC-01…04 | checklist đầy đủ + báo cáo eval |
| C4 — Regression + UAT | sau M4 | REG-01…04; retest bug; UAT-01…11; sign-off | báo cáo tổng + chữ ký |

Quy tắc: bug phát hiện ghi vào bảng bug trong manual-checklist (ID, mô tả, mức S1–S4, task liên quan); bug S1/S2 phải fix + retest trước khi sang cycle sau.

### 4.7 §7.0 Item Pass/Fail Criteria

**Tiêu chí vào (entry) từng mức:**

| Mức | Entry criteria |
|---|---|
| Unit | Code hoàn thành + lint pass; mock sẵn |
| Integration | Unit xanh; Qdrant healthy; `.env` hợp lệ |
| System/Manual | Integration xanh; build chạy `streamlit run app/main.py` không exception; bộ PDF chuẩn bị sẵn |
| Eval | Ít nhất 3 tài liệu READY trong kho (theo bộ EV) |
| UAT | C3 pass trong ngày; không bug S1/S2 mở |

**Tiêu chí pass/fail từng item:**

| Kiểm thử | Pass khi |
|---|---|
| Unit | 100% assert pass; coverage ≥80% (module không UI) |
| Integration | 100% IT pass với Qdrant thật |
| System/Manual | 6 luồng chính (ST-01…06) 100% pass; biên ST-07…18 pass hoặc bug đã ghi nhận kèm mức độ; **0 traceback UI** |
| Eval | QLT-01 ≥8/10 · QLT-02 ≥8/10 · QLT-03 ≥9/10 · QLT-04 ≥9/10 |
| Perf | PF-04 từ chối nhanh; PF-01…03 không timeout; baseline ghi nhận |
| Security | 100% SEC pass |
| UAT | 11/11 mục IMP §9.2 pass |

**Tiêu chí nghiệm thu tổng (exit criteria của test phase):**

1. `pytest` đầy đủ xanh (unit + integration).
2. Manual checklist: mục 4.2–4.7 (bắt buộc) 100% pass; biên 4.8 pass hoặc bug đã ghi.
3. Eval đạt 4 ngưỡng QLT; báo cáo có tỉ lệ + nguồn từng câu.
4. Không còn bug S1/S2 mở; bug S3/S4 có ticket + kế hoạch.
5. Không traceback trên UI; không nội dung nhạy cảm trong log.
6. UAT 11/11 được Product Owner ký.

### 4.8 §8.0 Suspension & Resumption Criteria

**Tạm dừng khi:**

1. Qdrant không healthy sau restart/migration → dừng C1/C3 (không đoán kết quả).
2. LLM/Embedding endpoint không phản hồi (network/quota/key hết hạn) → dừng eval + ST-03…05.
3. `.env` hoặc cấu hình thay đổi giữa lúc chạy (đổi model/dim giữa kho dữ liệu) → dừng + recreate collection.
4. Bug S1 chặn luồng chính (không upload được/mất dữ liệu) → dừng test chức năng, chờ hotfix.
5. Môi trường QA mất dữ liệu chuẩn (PDF fixtures/quyền ghi `data/`).

**Resume khi:**

1. Đã khôi phục: `docker compose up -d` healthy; endpoint LLM/Embedding phản hồi; file `data/` ghi được.
2. Chạy lại **smoke**: UT nhanh + IT-01 (collection) + ST-01 rút gọn (upload 1 PDF + 1 câu hỏi) trước khi tiếp tục.
3. Nếu đổi model embedding: chạy quy trình re-index (README) trên lại toàn bộ kho test, ghi lại trong kết quả.

### 4.9 §9.0 Test Deliverables

| ID | Deliverable | Định dạng | Owner | Điểm giao |
|---|---|---|---|---|
| D-01 | Kế hoạch kiểm thử này | Markdown | QA | ngay sau review |
| D-02 | Test case + traceability | trong tài liệu này §6 + §5 | QA | C1 |
| D-03 | Báo cáo unit/integration | pytest output + coverage | Dev/QA | C1, mỗi cycle |
| D-04 | `docs/testing/manual-checklist.md` đã điền | Markdown (giữ bảng bug) | QA | C3 |
| D-05 | Báo cáo eval 30 câu (đúng/sai + nguồn) | Markdown/JSON | QA | C3 |
| D-06 | Báo cáo hiệu năng + bảo mật baseline | Markdown | QA | C3 |
| D-07 | Bug list + trạng thái | bảng trong D-04 | QA/Dev | liên tục |
| D-08 | Báo cáo tổng nghiệm thu + chữ ký UAT | Markdown/Email | QA + PO | C4 |

### 4.10 §10.0 Testing Tasks

| ID | Task | Báo về task dev | Tag test | Owner | Ước lượng |
|---|---|---|---|---|---|
| TT-01 | Chuẩn bị test plan + traceability | — | §2, §5 | QA | 0,5d |
| TT-02 | Chuẩn bị bộ PDF adversarial (§6-A) + môi trường | S-01, S-02 | §6-A | QA | 0,5d |
| TT-03 | Rà/đồng bộ unit test theo task (S-22) | S-22 | UT-01…13 | Dev | 0,75d |
| TT-04 | Integration Qdrant + pipeline (S-23) | S-23 | IT-01…12 | Dev+QA | 0,5d |
| TT-05 | Bộ eval + runner (S-24) | S-24 | EV-01…05 | QA | 0,75d |
| TT-06 | Thực thi manual checklist (S-25) | S-25 | ST/UI/SEC | QA | 0,5d |
| TT-07 | Perf + security baseline | — | PF/SEC | QA | 0,5d |
| TT-08 | Regression + retest theo từng cycle | — | REG | QA | 0,5d |
| TT-09 | UAT demo + sig-noff (đi với M4) | S-26 | UAT | PO+QA | 0,25d |
| TT-10 | Báo cáo tổng + lessons learned | — | D-08 | QA | 0,25d |

> Tổng effort QA riêng ≈ 4,5 ngày công (chưa gồm "unit test trong từng task" — phần đó đã gộp trong 11,5 ngày dev của IMP).

### 4.11 §11.0 Environmental Needs

| Hạng mục | Production-like test env |
|---|---|
| **H/W + OS** | Linux desktop/laptop ≥ 8 GB RAM; Docker Engine |
| **Runtime** | Python 3.12 + venv (`uv sync` hoặc `pip install -e .`); Streamlit |
| **DB/Vector** | Qdrant v1.12.4 qua `docker compose up -d` — ports 6333/6334, volume `qdrant_data`; SQLite `data/app.db` (WAL) |
| **AI endpoint** | Mặc định Ollama local (`llama3.1`, `nomic-embed-text`, dim 768). Phương án OpenAI (gpt-4o-mini + text-embedding-3-small, dim 1536) nếu được cấp key. Ghi rõ trong kết quả |
| **Browser** | Chrome phiên bản 2 bản mới nhất; thay thế kiểm thử Safari/Firefox nếu có thời gian (P2) |
| **Tools** | `pytest`, Qdrant dashboard (`:6333/dashboard`), curl, Docker CLI, DevTools |
| **Giới hạn đặt** | Dùng đúng `.env.example`: `MAX_UPLOAD_MB=25`, `MAX_PAGES=400`, `TOP_K=8`, `SCORE_THRESHOLD=0.25`… (không đổi giữa lúc test; nếu đổi → resume theo §4.8) |
| **Nhân sự truy cập** | QA + Dev; không expose cổng ra ngoài (SEC-04) |
| **Khác** | Backup `data/` trước mỗi test xoá để khôi phục nhanh |

**Bộ dữ liệu chuẩn:** PDF adversarial (§6-A), bộ eval 30 câu (§6-B), danh mục mã lỗi (§6-C).

### 4.12 §12.0 Responsibilities

| Vai trò | Người | Trách nhiệm kiểm thử |
|---|---|---|
| **QA / Test lead** | QA (có thể là developer thứ 2) | Plan, traceability, checklist, eval, bug, báo cáo |
| **Developer** | 1 dev theo IMP | Unit test từng task (S-22), hỗ trợ IT, fix bug, không giấu lỗi |
| **Product Owner / BA** | Minh Tran | UAT (UAT-01…11), chốt ngưỡng QLT nếu OQ-002/015 được giải quyết |
| **Reviewer kỹ thuật** | Principal Architect | Review plan, nhận kết quả bảo mật/hiệu năng |
| **DevOps / IT** | (tự dev) | Cấp key LLM/thành phần mạng nội bộ nếu cần |
| **Security** | (đại diện) | Review SEC-01…04 khi quyết định cho phép share nội bộ |

Ghi chú: mô hình team 1 dev → QA áp dụng self-QA (dev tự chạy checklist nhưng nên có 1 người khác tác giả code chạy lại S-25 cho mắt mới); PO thực hiện UAT trực tiếp.

### 4.13 §13.0 Staffing & Training

| Vai trò | Số người | Kỹ năng cần | Training |
|---|---|---|---|
| QA | 1 (có thể là 2nd dev) | pytest, Docker cơ bản, thiết kế negative test, RAG khái niệm | 0,5d đọc IMP + S-01…S-26 + demo Qdrant dashboard |
| Developer/QA hybrid | 1 | cùng trên + hiểu code | — |
| PO UAT | 1 | nghiệp vụ | 30 phút (brief) |

Không cần đào tạo chuyên sâu; chi phí training tối đa ~1 ngày công tổng.

### 4.14 §14.0 Schedule

Gắn theo 4 phase phát triển của IMP (1 dev, ~11,5 ngày) + QA ~4,5 ngày (một phần overlap).

| Ngày công | Hoạt động phát triển | Hoạt động kiểm thử | Milestone |
|---|---|---|---|
| D0,5 | S-01 scaffold | TT-02 chuẩn bị dữ liệu (song song) | — |
| D1 | S-02…S-05 (Qdrant + SQLite + config) | UT-08/09 đồng bộ theo task | — |
| D1,5–3 | S-06…S-10 (PDF/chunk/embed/upsert) | UT-01…07, 13 + IT-01…04 | — |
| D3,5–5 | S-11…S-14 (ingest + UI + lỗi) | IT-05…09 + C1 → **M1**; C2 một phần | M1 sau S-11 |
| D5,5–6,75 | S-15…S-21 (RAG/chat UI) | **M2**: C2 hoàn chỉnh (ST-01/02 + biên upload) | M2 sau S-14 |
| D7–9 | (tiếp S-15…S-21) | chuẩn bị eval dataset + fixtures | M3 sau S-21 |
| D9,5–11 | S-22…S-24 (test + eval code) | C3: ST đầy đủ + EV-01…05 + PF + SEC | — |
| D11,25–11,75 | S-25…S-26 (checklist + README) | C4: regression + re-test + UAT-11 | M4 sau S-26 |
| D12 | Demo | UAT-01…11 + sig-noff + D-08 | Demo |

Nếu 2 người (backend + UI/QA chạy song song): toàn bộ rút ngắn còn ~6–8 ngày; QA có thể bắt đầu C2 ngay khi S-12 xong.

**Kết thúc test phase = đạt exit criteria §4.7 + UAT ký.**

### 4.15 §15.0 Risks & Contingencies (góc nhìn QA)

| Risk ID | Rủi ro kiểm thử | Contingency |
|---|---|---|
| TR-01 | LLM quá chậm/limit → eval không chạy kịp | Gom câu eval, chạy nền; chuyển sang model nhỏ hơn; ghi baseline partial |
| TR-02 | Không có key OpenAI khi test | Dùng Ollama local mặc định; nếu cả hai không có → dựng stub embedding + mock LLM, chỉ giữ IT/UT, delay eval |
| TR-03 | Bug S1 chặn luồng upload/xoá trong thử nghiệm | Đóng băng luồng test, triage cùng dev trong 2h, rồi chạy lại cycle tương ứng |
| TR-04 | Thiếu người (dev trễ) | Cắt P3: eval giảm 20 câu, chỉ giữ 6 luồng manual bắt buộc + unit/integration xanh |
| TR-05 | Ngưỡng QLT không đạt (câu eval sai) | Không demo trước khi đạt; tune prompt/threshold theo SOP: sửa `prompts.py` / `SCORE_THRESHOLD` → chạy lại EV; nếu vẫn fail → phản ánh kiến trúc (chunking quá lớn/top-k), trình bày lại với IMP |
| TR-06 | Rủi ro nội dung: môi trường test chứa tài liệu thật nhạy cảm | Cấm: chỉ dùng fixtures tự tạo; xoá `data/` sau test; SEC-02 kiểm tra log |
| TR-07 | Thay đổi cấu hình giữa lúc test (đổi model/threshold) | Resume rule §4.8-3; log vào kết quả |
| TR-08 | Mất dữ liệu Qdrant/SQLite giữa test | Backup `data/` trước mỗi test; restore + re-index nếu cần |

### 4.16 §16.0 Approvals

| Vai trò | Tên | Chữ ký | Ngày |
|---|---|---|---|
| QA / Test Lead | | | |
| Product Owner | Minh Tran | | |
| (Reviewer) Principal Architect | | | |

Phê duyệt có điều kiện: các giá trị `[Giả định QA]` (PF target, cấu trúc bộ EV) được chốt tại C2 trước khi C3 chạy chính thức.

---

## 5. Ma trận truy vết (REQ ↔ Test Case ↔ Task ↔ Story)

### 5.1 Yêu cầu chức năng

| REQ | Người dùng mong đợi | US/AC | Test case | Task dev |
|---|---|---|---|---|
| FR-01 | Upload 1 PDF → READY | US-01/AC-01.1 | IT-05, ST-01, PF-01 | S-11, S-12 |
| FR-02 | Từ chối vượt giới hạn | US-01/AC-01.2 | UT-04…06, IT-07, ST-16 (4.8.6/7) | S-06, S-11 |
| FR-03 | Lý do từng tệp lỗi | US-03/AC-03.1–3.3 | UT-10, IT-06/07, ST-02, ST-17, UI-03 | S-06, S-14 |
| FR-04 | Nhiều file không chặn nhau | US-02/AC-02.2 | IT-08, ST-02 | S-13 |
| FR-05 | Trạng thái + lý do | US-04/AC-04.1–3 | UI-01, ST-01/16 | S-12, S-14 |
| FR-06 | Danh sách đủ thông tin | US-05/AC-05.1 | UT-09, ST-01 (1.6) | S-04, S-12 |
| FR-07 | Xoá 3 kho + danh sách | US-06/AC-06.1 | IT-04/09, ST-06 | S-05, S-12 |
| FR-08 | Xoá hiệu lực với chat | US-06/AC-06.2 | ST-06 (6.6), EV trong C4 | S-18, S-20 |
| FR-09 | Chat tự nhiên | US-07/AC-07.1 | IT-12, ST-03, PF-02 | S-16, S-18 |
| FR-10 | Chat disable khi 0 READY | US-07/AC-07.2 | ST-07 (4.8.1/2), UI-02 | S-19 |
| FR-11 | Trả lời theo tài liệu | US-08/AC-08.1 | UT-11, IT-12, EV-01 | S-15, S-17 |
| FR-12 | NOT_FOUND cố định | US-11 (PRD) · IMP §1.1 | UT-11, IT-11, ST-04, EV-03 | S-17 |
| FR-13 | Tổng hợp đa tài liệu | US-09/AC-09.1 | ST-05, EV-02 | S-15, S-21 |
| FR-14 | Nguồn file + trang | US-10/13d | UT-12, ST-03, EV-04, UI-04 | S-20 |
| FR-15 | Chat history trong phiên | US-14 (rút gọn) | ST-03, ST-18 (4.8.10) | S-18 |
| FR-16 | Cấu hình `.env` | US-24 (rút gọn) | UT-08, IT-01, SEC-04 | S-03 |

### 5.2 NFR/BR/QLT

| REQ | Mô tả | Test case | Task |
|---|---|---|---|
| NFR-01 | Upsert idempotent | UT-13, IT-02 | S-10 |
| NFR-02 | Qdrant bền vững volume | ST-17 (4.8.12) | S-02 |
| NFR-03 | Qdrant down → banner không crash | ST-14/15 (4.8.3/4) | S-05 |
| NFR-04 | Lỗi LLM thân thiện, không lộ key | SEC-01, ST-15 (4.8.5), IT-12 | S-16, S-14 |
| NFR-05 | Không log nội dung | SEC-02 (kiểm terminal/DevTools + DoD) | mọi task |
| NFR-06 | Sync trong giới hạn | PF-01, PF-04 | S-11 |
| NFR-07 | Unicode NFC + tên file | UT-07, UI-06, SEC-03 | S-07, S-12 |
| NFR-08 | Triển khai an toàn no-auth | SEC-04, UAT-11 | S-01, S-26 |
| NFR-09 | `EMBEDDING_DIM` khớp | UT-08, IT-01, TR quy trình re-index | S-03, S-05 |
| BR-01 | Chỉ PDF (magic) | UT-04, IT-07, ST-02 | S-06 |
| BR-02 | `MAX_UPLOAD_MB` | UT-04, ST-16 (4.8.6) | S-06 |
| BR-03 | `MAX_PAGES` | UT-06, ST-16 (4.8.7) | S-06 |
| BR-04 | PDF mã hoá | UT-05, ST-17 (4.8.8) | S-06 |
| BR-05 | PDF scan → `PDF_NO_TEXT` | UT-03/07, IT-06, ST-17 (4.8.9) | S-07, S-11 |
| BR-06 | Chunk 700/100/trang | UT-01…03 | S-08 |
| BR-07 | TOP_K/threshold/diversity | UT-12, IT-03, PF-03 | S-15, S-21 |
| BR-08 | `uuid5` point ID | UT-13, IT-02 | S-10 |
| BR-09 | Xoá cascade | IT-04/09, ST-06 | S-05, S-11 |
| BR-10 | Batch + retry embedding | IT-10 | S-09 |
| QLT-01 | ≥8/10 đúng nội dung | EV-01 | S-24 |
| QLT-02 | ≥8/10 đa tài liệu | EV-02 | S-24 |
| QLT-03 | ≥9/10 not-found | EV-03 | S-24 |
| QLT-04 | ≥9/10 nguồn đúng | EV-04 | S-24 |

### 5.3 Độ phủ

- 16/16 FR có ≥1 test case (100%).
- 9/9 NFR, 10/10 BR, 4/4 QLT có ≥1 test case (100%).
- Mọi task S-01…S-26 được bảo vệ bởi ít nhất 1 test case trừ S-01 (scaffold — được phủ qua UT-08/SEC-04) và S-26 (phủ qua UAT-11).

---

## 6. Phụ lục

### 6-A Bộ dữ liệu PDF sẵn sàng (adversarial test set)

| # | File | Đặc điểm | Mục đích | Kiểm tra |
|---|---|---|---|---|
| A-01 | `hop-dong.pdf` | text tiếng Việt 32 trang | tài liệu cơ sở | ST-01, EV in-scope |
| A-02 | `bao-gia.pdf` | text 12 trang, nội dung khác A-01 | đa tài liệu | ST-05, EV multi-doc |
| A-03 | `quy-dinh.pdf` | text 5 trang | chủ đề độc lập, kiểm tra đa dạng nguồn | ST-05 |
| A-04 | `scan.pdf` | PDF scan (ảnh, không text layer) | BR-05 | ST-17 (4.8.9), IT-06 |
| A-05 | `encrypted.pdf` | có mật khẩu | BR-04 | ST-17 (4.8.8) |
| A-06 | `corrupt.pdf` | hỏng middle-of-file, đầu `%PDF-` | PDF corrupt | IT-07 |
| A-07 | `fake.docx` | đuôi .docx | định dạng sai | ST-02 |
| A-08 | `disguised.pdf` | text file đổi đuôi .pdf | magic bytes | UT-04 |
| A-09 | `big-25mb.pdf` | ~25,1 MB | BR-02 | ST-16 (4.8.6) |
| A-10 | `long-401p.pdf` | 401 trang | BR-03 | ST-16 (4.8.7) |
| A-11 | `ten-tap-tin--<script>.pdf` (tên dài + chuỗi `<script>` trong tên, hợp lệ trên HĐH) | tên dài + ký tự đặc biệt | NFR-07, SEC-03 | UI-06 |
| A-12 | `blank.pdf` | 2 trang trắng | MIN_TEXT_CHARS | UT-03 |

Lưu ý: A-09/A-10 có thể sinh bằng cách gộp/generate; lưu tại `tests/eval/fixtures/` (S-24) kèm ghi chú mật khẩu cho A-05.

### 6-B Bộ eval 30 câu (khung + ví dụ) — chi tiết do task S-24 sản xuất

| Nhóm | Số câu | Ví dụ | Threshold | EV |
|---|---|---|---|---|
| (1) Trong tài liệu | 10 | "Hạn chót nộp hồ sơ là ngày nào?" → phải có cụm ngày + nguồn | ≥8 đúng | EV-01 |
| (2) Đa tài liệu | 10 | "So sánh thời gian giao hàng (bao-gia) và điều khoản thanh toán (hop-dong)" → nguồn ≥2 file | ≥8 câu nguồn ≥2 tài liệu | EV-02 |
| (3) Ngoài phạm vi | 10 | "Giá cổ phiếu VNM hôm nay?" / "Thủ đô nước Pháp?" | ≥9 NOT_FOUND đúng, không bịa | EV-03 |
| Nguồn | mọi nhóm | đối chiếu tên file + trang với PDF gốc | ≥9 đúng | EV-04 |

Định dạng chấm mỗi câu: `câu | kỳ vọng | thực tế | đúng/sai | nguồn trích | ghi chú`. Báo cáo tổng hợp % mỗi nhóm.

### 6-C Danh mục mã lỗi + thông báo (đồng bộ S-14 — placeholder)

| Mã | Kích hoạt | Thông báo đề xuất |
|---|---|---|
| `PDF_NOT_PDF` | sai đuôi/magic | "Chỉ hỗ trợ PDF: <tên file>" |
| `PDF_TOO_LARGE` | > 25 MB | "<tên file> vượt quá giới hạn 25 MB (tệp ~N MB)" |
| `PDF_TOO_MANY_PAGES` | > 400 trang | "<tên file> có N trang, vượt giới hạn 400 trang" |
| `PDF_ENCRYPTED` | `needs_pass` | "<tên file> được bảo vệ bằng mật khẩu, không thể đọc" |
| `PDF_CORRUPT` | lỗi parse | "<tên file> bị hỏng, không đọc được" |
| `PDF_NO_TEXT` | mọi trang <20 ký tự | "<tên file> không có văn bản trích xuất được (PDF dạng ảnh scan chưa được hỗ trợ)" |
| `QDRANT_UNAVAILABLE` | health fail | "Hệ thống lưu trữ chưa sẵn sàng, thử lại sau" |
| `EMBEDDING_FAILED` | API lỗi | "Tạm thời không xử lý được tài liệu, thử lại" |
| `LLM_FAILED` | API lỗi/timeout | "Tạm thời không trả lời được, thử lại" |
| `CONFIG_INVALID` | startup | "Cấu hình thiếu hoặc sai: <trường>" |

_NOT_FOUND (không phải lỗi): "Không tìm thấy thông tin này trong các tài liệu đã tải lên."_

### 6-D Ghi chú truy vết ngược (những phần PRD không test)

Các phần đã cắt của PRD (auth, telemetry, feedback, streaming có nút Dừng, lịch sử hội thoại bền, 403, PDF viewer cột phải, hộp thoại tệp trùng tên "Thay thế/Giữ cả hai"...) không nằm trong test plan này theo §4.5 NT-01…NT-08. Nếu sau này quay lại phạm vi đầy đủ theo PRD, test plan cần bổ sung cycle mới để phủ các phần đã cắt.

---

## 7. Lịch sử phiên bản

| Phiên bản | Ngày | Người thực hiện | Nội dung |
|---|---|---|---|
| 1.0 | 2026-10-23 | QA | Bản đầu tiên: traceability FR/NFR/BR/QLT + 4 mức kiểm thử + cycles C0…C4 theo milestones M1–M4 của IMP-CVD-003 |

*Hết tài liệu. Bước tiếp theo đề xuất: chuẩn bị bộ fixtures §6-A (kèm S-01/S-02) và tạo `docs/testing/manual-checklist.md` từ template S-25 trước khi vào C1.*
