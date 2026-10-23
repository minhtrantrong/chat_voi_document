# Kế hoạch Kiểm thử Tổng thể (Master Test Plan)

**Dự án:** Chat với tài liệu — PDF + Qdrant + Ollama  
**Mã tài liệu:** CVD-MTP-001  
**Phiên bản:** 1.0  
**Ngày lập:** 2026-10-23  
**Trạng thái:** Draft for review  
**Chuẩn áp dụng:** IEEE 829-2008 — Software Test Documentation  
**Phân loại:** Internal

> Tài liệu này lập kế hoạch kiểm thử cho **phiên bản MVP đơn giản hoá** đang có trong
> repository, theo `IMP-CVD-003`. Phạm vi kiểm thử bám theo US-01…US-09 (rút gọn) và
> các task S-01…S-26. Các thành phần của SADD/PRD đầy đủ như đăng nhập, PostgreSQL,
> Redis, worker, OCR, source viewer và telemetry **không thuộc phạm vi bản kiểm thử này**.

---

## 0. Thông tin tài liệu

| Thuộc tính | Giá trị |
|---|---|
| Tên hệ thống | Ứng dụng một trang: upload PDF và chat với AI về nội dung tài liệu |
| Môi trường mặc định | Streamlit + SQLite + local disk + Qdrant + Ollama |
| Mô hình mặc định | `llama3.1` (chat), `nomic-embed-text` (embedding), `EMBEDDING_DIM=768` |
| Phương án thay thế | API tương thích OpenAI (ví dụ `gpt-4o-mini` + `text-embedding-3-small`, 1536 chiều) |
| Người dùng | Một người dùng nội bộ / demo; **không có đăng nhập, không phân quyền** |
| Đơn vị thực hiện | QA/Test, có hỗ trợ từ Development và Product Owner |
| Tài liệu nguồn | BRD, PRD, User Stories, SADD, UI/UX Blueprint, Implementation Plan, Task Breakdown, README |
| Tài liệu đầu ra | Test Plan, test case, traceability matrix, test summary, eval report, manual checklist |

### 0.1 Lịch sử phiên bản

| Phiên bản | Ngày | Người thực hiện | Nội dung |
|---|---|---|---|
| 1.0 | 2026-10-23 | QA Architect | Bản kế hoạch đầu tiên cho MVP đơn giản hoá |

### 0.2 Tóm tắt điều hành

Ứng dụng đã có nền tảng chạy được: upload PDF, validate/extract/chunk/embedding,
lưu metadata SQLite, upsert và tìm kiếm Qdrant, chat RAG streaming, hiển thị nguồn,
xoá cứng tài liệu và bộ eval 30 câu. Kế hoạch này xác định cách kiểm chứng các luồng
chính, các trường hợp biên, chất lượng câu trả lời và các ràng buộc vận hành của MVP.

Kết quả baseline ngày 2026-10-23:

| Hạng mục | Kết quả | Ghi chú |
|---|---|---|
| Unit + integration tests | **156 passed** | Chạy bằng `pytest -q` |
| Coverage | **94%** | Đo trên `app`, không tính `app/main.py` và `app/shared` |
| Lint/format | **Pass** | `ruff check`, `ruff format --check` |
| Type check | **Pass** | `mypy app` |
| Streamlit headless smoke | **HTTP 200** | Ứng dụng khởi động được |
| Qdrant | **Healthy, v1.20.0** | Collection `document_chunks`, 768 chiều, 0 point |
| Chat/upload thực tế với Ollama | **Chưa chạy** | Máy kiểm thử chưa có `ollama serve`; cổng 11434 đóng |
| Eval 30 câu | **Chưa chạy** | Phụ thuộc Ollama và dữ liệu fixture |

> **Kết luận baseline:** phần lớn kiểm thử tự động đã đạt; các luồng end-to-end có AI
> thật, chất lượng RAG và eval **chưa được nghiệm thu**. Đây là các cổng bắt buộc
> trước khi ký acceptance.

### 0.3 Cấu trúc tài liệu theo IEEE 829

| Mục | Clause IEEE 829-2008 | Nội dung |
|---|---|---|
| 1.0 | 5.1 | Test Plan Identifier |
| 2.0 | 5.2 | Introduction, scope, references, assumptions |
| 3.0 | 5.3 | Test Items |
| 4.0 | 5.4 | Features to be Tested |
| 5.0 | 5.5 | Features Not to be Tested |
| 6.0 | 5.6 | Approach, levels, types, test cases |
| 7.0 | 5.7 | Item Pass/Fail Criteria |
| 8.0 | 5.8 | Suspension and Resumption Criteria |
| 9.0 | 5.9 | Test Deliverables |
| 10.0 | 5.10 | Testing Tasks |
| 11.0 | 5.11 | Environmental Needs |
| 12.0 | 5.12 | Responsibilities |
| 13.0 | 5.13 | Staffing and Training Needs |
| 14.0 | 5.14 | Schedule |
| 15.0 | 5.15 | Risks and Contingencies |
| 16.0 | 5.16 | Approvals |
| Phụ lục A–E | — | Traceability, baseline, fixture, checklist, trạng thái |

---

## 1.0 Định danh kế hoạch kiểm thử

### 1.1 Định danh

| Trường | Giá trị |
|---|---|
| Test Plan ID | `CVD-MTP-001` |
| Tên | Master Test Plan — Chat với tài liệu (PDF + Qdrant + Ollama) |
| Phiên bản | 1.0 |
| Ngày hiệu lực dự kiến | 2026-10-26 |
| Người lập | QA Architect |
| Người phê duyệt | QA Lead, Product Owner, Engineering Lead |
| Phạm vi áp dụng | MVP đơn giản hoá trong repository `chat_voi_document` |
| Hình thức | Tài liệu số, Markdown, quản lý trong Git |

### 1.2 Mục đích của kế hoạch

Kế hoạch này mô tả cách kiểm chứng rằng ứng dụng:

1. Nhận và xử lý được PDF hợp lệ, từ chối PDF không hợp lệ với thông báo rõ ràng.
2. Lưu và truy xuất đúng dữ liệu qua SQLite, file local và Qdrant.
3. Trả lời câu hỏi dựa trên nội dung tài liệu, có nguồn (tên file + trang), và không
   bịa thông tin khi không có căn cứ.
4. Xoá cứng tài liệu đúng cách, không để lại point trong Qdrant hoặc lịch sử chat.
5. Chạy ổn định với cấu hình mặc định Ollama 768 chiều, đồng thời hỗ trợ cấu hình
   OpenAI tương thích khi cần.
6. Có bằng chứng kiểm thử đủ để Product Owner ra quyết định acceptance cho MVP.

---

## 2.0 Giới thiệu

### 2.1 Mục tiêu kiểm thử

| Mục tiêu | Mô tả | Đo lường |
|---|---|---|
| OBJ-01 | Xác nhận luồng upload → ingest → chat → delete hoạt động đúng | 100% test case P0/P1 pass |
| OBJ-02 | Xác nhận chất lượng câu trả lời có căn cứ và trích dẫn | Eval in-document ≥ 80%; citation ≥ 90% (mục tiêu PRD) |
| OBJ-03 | Xác nhận xử lý lỗi không làm sập ứng dụng | Không có lỗi Critical/High; thông báo thân thiện |
| OBJ-04 | Xác nhận cấu hình mặc định Ollama/Qdrant đúng | Upload và chat thật thành công với 768 chiều |
| OBJ-05 | Bảo đảm truy vết yêu cầu → test case → bằng chứng | 100% yêu cầu in-scope có test case |
| OBJ-06 | Đo baseline hiệu năng và độ ổn định của MVP | Có số liệu trên môi trường tham chiếu |

### 2.2 Phạm vi

**Trong phạm vi:**

| Mã | Năng lực | Nguồn |
|---|---|---|
| IN-01 | Upload một hoặc nhiều PDF | US-01, US-02, S-11/S-13 |
| IN-02 | Validate định dạng, dung lượng, số trang, mã hoá, PDF scan không có text | US-03, S-06/S-14 |
| IN-03 | Extract text, chunking theo trang, giữ số trang | S-07/S-08 |
| IN-04 | Embedding, batch, kiểm tra dimension | S-09/S-10 |
| IN-05 | Qdrant collection, upsert, search, delete | S-04/S-05, S-16 |
| IN-06 | SQLite metadata, trạng thái tài liệu | S-03, S-12 |
| IN-07 | Danh sách tài liệu, trạng thái, thông tin file | US-04/US-05, S-12 |
| IN-08 | Chat streaming, session history, nguồn trích dẫn | US-07/08/09, S-17…S-21 |
| IN-09 | Xoá cứng tài liệu và reset chat | US-06, S-12 |
| IN-10 | Cấu hình Ollama/OpenAI, biến môi trường | S-03, README |
| IN-11 | Bộ eval 30 câu, báo cáo JSON/Markdown | S-24, `tests/eval` |
| IN-12 | Docker Compose, hướng dẫn chạy, checklist thủ công | S-25/S-26 |

**Ngoài phạm vi (xem chi tiết §5):**

- Đăng nhập, phân quyền, SSO/OIDC, quản trị người dùng, audit log.
- PostgreSQL/pgvector, Redis, worker nền, object storage.
- OCR cho PDF scan; hỗ trợ DOCX/PPTX/Excel/HTML.
- Source viewer mở đúng trang PDF; trích dẫn click được.
- Lịch sử chat bền vững giữa các phiên; streaming cancellation/retry UI.
- Telemetry, feedback, dashboard vận hành, multi-tenant.
- Kiểm thử tải lớn, penetration test, accessibility audit đầy đủ WCAG.

### 2.3 Tài liệu tham chiếu

| Mã | Tài liệu | Đường dẫn | Vai trò |
|---|---|---|---|
| REF-01 | BRD | `docs/requirements/BRD.md` | Bối cảnh kinh doanh, ràng buộc |
| REF-02 | PRD | `docs/requirements/PRD.md` | Yêu cầu chức năng/phi chức năng gốc |
| REF-03 | User Stories | `docs/requirements/User_Stories.md` | US-01…US-09 (bản rút gọn) |
| REF-04 | SADD | `docs/design/SADD.md` | Kiến trúc tham khảo; đã đơn giản hoá |
| REF-05 | UI/UX Blueprint | `docs/design/UIUX_Blueprint_Design.md` | Định hướng giao diện |
| REF-06 | Implementation Plan | `docs/implement/Implement_plan_Simple_Qdrant.md` | Phạm vi triển khai thực tế |
| REF-07 | Task breakdown | `docs/implement/tasks/README.md` | S-01…S-26, Definition of Done |
| REF-08 | README | `README.md` | Cách chạy, cấu hình, troubleshooting |
| REF-09 | Manual checklist | `docs/testing/manual-checklist.md` (nếu có; nếu chưa, dùng Phụ lục D) | Kịch bản kiểm thử thủ công |
| REF-10 | Test Plan prompt | `docs/testing/testPlan_prompt.md` | Mẫu và yêu cầu tài liệu |
| REF-11 | Eval dataset | `tests/eval/dataset.json` | 30 câu hỏi đánh giá |
| REF-12 | Fixture generator | `tests/eval/generate_fixtures.py` | Sinh PDF mẫu tiếng Việt |

### 2.4 Giả định và ràng buộc

| Mã | Giả định / ràng buộc | Ảnh hưởng đến kiểm thử |
|---|---|---|
| AS-01 | Ứng dụng phục vụ một người dùng nội bộ, không có auth | Không test login/403/RBAC; test cảnh báo lộ dữ liệu |
| AS-02 | Ingestion chạy đồng bộ trong request upload | Test trạng thái cuối; không test worker/nền/SSE |
| AS-03 | Chat history chỉ trong `st.session_state` | Refresh trang làm mất history; không test persistence |
| AS-04 | Default là Ollama local, không cần API key thật | Test mặc định với `ollama`; OpenAI là tùy chọn |
| AS-05 | Embedding mặc định 768 chiều | Phải xoá/recreate collection nếu đổi model/dimension |
| AS-06 | Qdrant chạy local bằng Docker Compose | Test integration cần Qdrant sống |
| AS-07 | Dữ liệu test là PDF tổng hợp, không chứa PII thật | Không dùng tài liệu khách hàng thật |
| AS-08 | Trình duyệt mục tiêu là Chrome/Firefox desktop | Mobile chỉ kiểm tra mức "dùng được", không phải gate |
| AS-09 | Không có public REST API của ứng dụng | Test API chỉ ở interface ra Ollama/OpenAI/Qdrant |
| AS-10 | SADD/PRD đầy đủ mô tả kiến trúc lớn hơn | Test theo IMP-CVD-003; phần dư được ghi nhận out-of-scope |

### 2.5 Xử lý khác biệt giữa tài liệu nguồn

| Chủ đề | PRD/SADD đầy đủ | IMP-CVD-003 (áp dụng) | Quyết định kiểm thử |
|---|---|---|---|
| Xác thực | Có login/SSO/RBAC | Không có auth | Không test auth; ghi rủi ro vận hành |
| Vector DB | PostgreSQL/pgvector | Qdrant | Test Qdrant |
| Xử lý nền | Worker/queue/Redis | Đồng bộ | Test luồng đồng bộ |
| Streaming | SSE, retry/cancel | Streamlit streaming, retry giới hạn | Test stream và lỗi; không test cancel UI |
| Nguồn | Viewer mở đúng trang | Hiển thị tên file + trang + snippet | Test hiển thị; viewer out-of-scope |
| Embedding | 1536 chiều | 768 chiều (Ollama) | Test 768; OpenAI 1536 là tùy chọn |
| Chat history | Bền vững | `st.session_state` | Test reset khi refresh/xoá |

### 2.6 Phân tích tài liệu đầu vào

#### 2.6.1 Input document inventory

| Loại | Tài liệu | Phiên bản | Nguồn | Thông tin chính |
|---|---|---|---|---|
| BRD | `docs/requirements/BRD.md` | BRD-CVD-001 v0.1 | Product/BA | Mục tiêu kinh doanh, stakeholder, ràng buộc |
| SRS/PRD | `docs/requirements/PRD.md` | PRD-CVD-001 v0.1 | Product/BA | Yêu cầu chức năng, NFR, edge case, metric |
| SAD | `docs/design/SADD.md` | SADD-CVD-001 v1.0 | Architecture | View kiến trúc, interface, NFR, ADR |
| UI/UX | `docs/design/UIUX_Blueprint_Design.md` | SDD-UX-CVD-001 v0.1 | Design | Screen, flow, interaction, accessibility |
| User Stories | `docs/requirements/User_Stories.md` | US-CVD-001 v0.1 | Product | US-01…US-09 rút gọn + acceptance criteria |
| Development Plan | `docs/implement/Implement_plan_Simple_Qdrant.md` | IMP-CVD-003 v1.0 | Dev | Phạm vi, stack, ràng buộc, task |
| Task Breakdown | `docs/implement/tasks/README.md` | S-01…S-26 | Dev | Hợp đồng task, test, DoD |
| Runbook | `README.md` | Hiện hành | Dev | Cài đặt, cấu hình, troubleshooting |
| Test prompt | `docs/testing/testPlan_prompt.md` | v1.0 | QA | Mẫu test plan IEEE 829 |

#### 2.6.2 Design elements

| Design view | Element | Component type | Interfaces | State / transition | Dependencies |
|---|---|---|---|---|---|
| Composition | Streamlit monolith | Web app | Browser ⇄ app | Empty → Ready → Error | Streamlit, Python |
| Composition | SQLite metadata | Local DB | SQL | Row `PROCESSING` → `READY`/`ERROR` | Filesystem |
| Composition | Qdrant | Vector DB | REST/client | Collection exists/missing; point upsert/delete | Docker |
| Component & connector | `app/pdf.py` | Module | `validate_pdf`, `extract_pages` | Valid/invalid | PyMuPDF |
| Component & connector | `app/chunking.py` | Module | `chunk_pages` | — | Config |
| Component & connector | `app/embeddings.py` | Module | `embed_texts` | Retry → success/error | Ollama/OpenAI |
| Component & connector | `app/vector_store.py` | Adapter | ensure/upsert/query/delete | Healthy/unavailable | Qdrant |
| Component & connector | `app/ingest.py` | Orchestrator | `ingest_pdf` | Processing → ready/error | PDF, DB, embed, Qdrant |
| Component & connector | `app/rag.py` | RAG service | retrieve/context/prompt | Hits/no hits | Qdrant, LLM |
| Component & connector | `app/llm.py` | Client | `stream_chat` | Stream/retry/error | Ollama/OpenAI |
| Component & connector | `app/main.py` | UI | Streamlit widgets | Empty/ready/error/chat | All modules |
| Interaction | Upload flow | Sequence | Upload → validate → save → ingest | Start → progress → result | DB/Qdrant/AI |
| Interaction | Chat flow | Sequence | Question → embed → query → prompt → stream | Idle → retrieving → streaming → done/error | RAG/LLM |
| Interaction | Delete flow | Sequence | Confirm → Qdrant delete → DB/file delete → reset chat | Ready → deleting → gone/error | All stores |
| Information | `documents` table | Schema | id, filename, path, size, pages, status, error, created_at | Status lifecycle | SQLite |
| Information | Qdrant payload | Schema | document_id, chunk_index, page_number, text, filename | Point lifecycle | Qdrant |
| Interface | Ollama/OpenAI embeddings | REST | `POST /v1/embeddings` | Success/error | Provider |
| Interface | Ollama/OpenAI chat | REST | `POST /v1/chat/completions` (stream) | Token stream/error | Provider |
| State dynamics | Document | State machine | Upload, ingest success/fail, delete | `PROCESSING` → `READY`/`ERROR` → deleted | DB |

#### 2.6.3 UI/UX elements

| UI component | Page/screen | Interactions | States | Accessibility / ghi chú | User flow |
|---|---|---|---|---|---|
| Sidebar tài liệu | Trang chính | Xem list, chọn/xoá | Empty/loading/ready/error | Label text; contrast Streamlit mặc định | Xem tài liệu |
| Upload PDF | Trang chính | Chọn/kéo thả nhiều file | Idle/uploading/success/error | Có label; hỗ trợ bàn phím cơ bản | Upload |
| Danh sách + metadata | Sidebar | Scroll/xem trạng thái | Ready/processing/error | Tên file dài được wrap/escape | Chọn tài liệu |
| Nút xoá + xác nhận | Sidebar | Click, confirm/cancel | Idle/confirming/deleting/error | Có bước xác nhận; không xoá ngay | Delete |
| Chat input | Main | Nhập, Enter/gửi | Disabled khi không READY | Placeholder tiếng Việt; disabled rõ | Chat |
| Chat messages | Main | Scroll, xem history | Streaming/done/error | Render Markdown an toàn | Chat |
| Sources expander | Main | Mở/đóng nguồn | Có/không nguồn | Tên file + trang + snippet; escape | Kiểm chứng |
| Banner Qdrant/dimension | Sidebar/Main | Xem thông báo | Healthy/unavailable/mismatch | Màu + text, không chỉ màu | Troubleshooting |
| Progress/status | Main | Theo dõi upload | Running/success/error | Text + spinner | Upload |

#### 2.6.4 API elements

> Ứng dụng **không cung cấp public API**. Bảng dưới liệt kê interface outbound và
> storage; test qua client/module, không qua endpoint của app.

| Endpoint / interface | Method | Request schema | Response schema | Error responses | Auth |
|---|---|---|---|---|---|
| `{OPENAI_BASE_URL}/embeddings` | POST | `{model, input: string[]}` | `{data: [{embedding: float[], index}]}` | 400/401/404/429/5xx | Không (Ollama local); key với OpenAI |
| `{OPENAI_BASE_URL}/chat/completions` | POST | `{model, messages, temperature, stream: true}` | SSE chunk `choices[0].delta.content` | 400/401/404/429/5xx | Không (Ollama local); key với OpenAI |
| `PUT /collections/{name}` | PUT | `{vectors: {size, distance}}` | `{result: true}` | 4xx/5xx | Không local; `api-key` nếu bật |
| `PUT /collections/{name}/points?wait=true` | PUT | `{points: [{id, vector, payload}]}` | `{result: {status}}` | 4xx/5xx | Như trên |
| `POST /collections/{name}/points/query` | POST | `{query, limit, score_threshold, filter}` | `{result: {points}}` | 4xx/5xx | Như trên |
| `POST /collections/{name}/points/delete?wait=true` | POST | `{filter: {must: [...]}}` | `{result: {status}}` | 4xx/5xx | Như trên |
| `GET /healthz` | GET | — | `healthz check passed` | 5xx/timeout | Không |
| SQLite `data/*.db` | Local | SQL schema | Rows | Lock/corrupt | Filesystem permission |
| `data/uploads/*` | Filesystem | PDF bytes | File | Permission/disk full | Filesystem permission |

#### 2.6.5 User stories và acceptance criteria (in-scope)

| ID | Story | Acceptance criteria | Ưu tiên | Phụ thuộc |
|---|---|---|---|---|
| US-01 | Tải một PDF | PDF hợp lệ được lưu, xử lý xong `READY`, chat dùng được nội dung | P0 | Qdrant, embedding |
| US-02 | Tải nhiều PDF | Nhiều file được xử lý; file lỗi không chặn file hợp lệ | P0 | US-01 |
| US-03 | Biết file bị từ chối | Thông báo đúng lý do: không phải PDF, quá size/page, mã hoá, scan/no-text | P0 | PDF validator |
| US-04 | Thấy trạng thái | Chip `Đang xử lý`/`Sẵn sàng`/`Lỗi`; lỗi có mô tả | P0 | DB/UI |
| US-05 | Xem danh sách | Danh sách tất cả tài liệu, không phân quyền | P0 | DB |
| US-06 | Xoá tài liệu | Xoá cứng; chat sau đó không dùng tài liệu đã xoá | P0 | Qdrant/DB/file |
| US-07 | Chat với tài liệu | Chat bật khi có `READY`; trả lời dựa trên nội dung | P0 | US-01, LLM |
| US-08 | Câu trả lời có căn cứ | Không đủ căn cứ → `NOT_FOUND`; không bịa | P0 | Retrieval/prompt |
| US-09 | Nhiều tài liệu/nguồn | Tổng hợp nhiều tài liệu; hiển thị file + trang | P1 | US-07/08 |

#### 2.6.6 Risk assessment

Xem bảng đầy đủ tại **§15.0**. Tóm tắt: rủi ro cao nhất là câu trả lời không có căn cứ
(R-01, score 15), Ollama không sẵn sàng (R-05, score 16), no-auth lộ dữ liệu (R-08,
score 15). Các rủi ro này quyết định thứ tự ưu tiên P0 và các cổng eval/security.

---

## 3.0 Hạng mục kiểm thử (Test Items)

| Mã | Hạng mục | Phiên bản / vị trí | Kiểm thử gì |
|---|---|---|---|
| SI-001 | Ứng dụng Streamlit | `app/main.py` | Upload, danh sách, chat, nguồn, xoá, session state |
| SI-002 | Cấu hình | `app/config.py`, `.env.example` | Default Ollama, dimension, giới hạn upload, API key |
| SI-003 | SQLite metadata | `app/db.py` | Schema, CRUD, trạng thái, delete |
| SI-004 | Validate/extract PDF | `app/pdf.py` | Định dạng, size, page, mã hoá, text, số trang |
| SI-005 | Chunking | `app/chunking.py` | Kích thước, overlap, ranh giới trang, index |
| SI-006 | Embedding | `app/embeddings.py` | Batch, dimension, retry, lỗi |
| SI-007 | Qdrant adapter | `app/vector_store.py` | Collection, upsert, query, delete, health |
| SI-008 | Ingest pipeline | `app/ingest.py` | Orchestration, progress, rollback, lỗi |
| SI-009 | RAG | `app/rag.py` | Retrieval, context, prompt, nguồn, NOT_FOUND |
| SI-010 | LLM client | `app/llm.py` | Streaming, retry, lỗi, cấu hình |
| SI-011 | UI helpers | `app/ui.py` | Format, trạng thái, escaping, nguồn |
| SI-012 | Eval runner | `app/eval.py` | Chạy 30 câu, chấm điểm, báo cáo |
| SI-013 | Hạ tầng | `docker-compose.yml`, Qdrant v1.20 | Kết nối, health, collection |
| SI-014 | Tài liệu vận hành | `README.md`, checklist | Quickstart, troubleshooting, QA thủ công |

**Test data / fixture:**

| Mã | Dữ liệu | Mục đích |
|---|---|---|
| TD-01 | `tests/eval/fixtures/hop-dong.pdf` | Hợp đồng 3 trang, câu hỏi có đáp án cụ thể |
| TD-02 | `tests/eval/fixtures/bao-gia.pdf` | Báo giá nhiều nhà cung cấp, so sánh |
| TD-03 | `tests/eval/fixtures/quy-dinh.pdf` | Quy định nội bộ, câu hỏi policy |
| TD-04 | PDF sinh tự động trong test | File rỗng, mã hoá, corrupt, quá trang, scan/no-text |
| TD-05 | `tests/eval/dataset.json` | 30 câu hỏi: 10 in-document, 10 multi-doc, 10 out-of-scope |
| TD-06 | Dữ liệu Qdrant/SQLite tạm | Test isolation, cleanup, delete |

---

## 4.0 Tính năng cần kiểm thử

### 4.1 Ma trận ưu tiên

Thang điểm: **P0** = bắt buộc trước demo/acceptance; **P1** = quan trọng; **P2** = nên có.
Mức rủi ro lấy từ §15.

| Mã | Tính năng | Ưu tiên | Yêu cầu | Rủi ro chính |
|---|---|---|---|---|
| F-01 | Upload một PDF và xử lý đến `READY` | P0 | REQ-F-01 | Extract/embedding lỗi |
| F-02 | Upload nhiều PDF, cô lập lỗi từng file | P0 | REQ-F-02 | Một file lỗi chặn file khác |
| F-03 | Validate và thông báo lỗi PDF | P0 | REQ-F-03 | Thông báo sai/không rõ |
| F-04 | Danh sách, metadata, trạng thái tài liệu | P0 | REQ-F-04 | UI không cập nhật |
| F-05 | Xoá cứng tài liệu và dữ liệu liên quan | P0 | REQ-F-05 | Sót vector/file/chat |
| F-06 | Bật/tắt chat theo trạng thái tài liệu | P0 | REQ-F-06 | Chat khi chưa có dữ liệu |
| F-07 | Trả lời có căn cứ và `NOT_FOUND` | P0 | REQ-F-07 | Bịa thông tin |
| F-08 | Tổng hợp nhiều tài liệu | P1 | REQ-F-08 | Bỏ sót tài liệu |
| F-09 | Hiển thị nguồn (file + trang + snippet) | P1 | REQ-F-09 | Nguồn sai/không khớp |
| F-10 | Streaming và lịch sử chat trong session | P1 | REQ-F-10 | Treo/không có phản hồi |
| F-11 | Chạy eval và báo cáo chất lượng | P1 | REQ-F-11 | Dataset/báo cáo sai |
| F-12 | Cấu hình Ollama/OpenAI và dimension | P0 | REQ-F-12 | Model/dimension lệch |
| F-13 | Xử lý lỗi và thông báo thân thiện | P0 | REQ-F-13 | Lộ stack trace, crash |
| F-14 | Vòng đời collection Qdrant | P0 | REQ-F-14 | Collection cũ 1536 gây lỗi |
| F-15 | Tiến trình xử lý upload | P2 | REQ-F-15 | Người dùng tưởng treo |
| F-16 | Chất lượng RAG (accuracy/citation) | P0 | REQ-NF-01 | Không đạt ngưỡng |
| F-17 | Hiệu năng MVP | P2 | REQ-NF-02 | Upload/chat quá chậm |
| F-18 | Độ tin cậy khi dependency lỗi | P1 | REQ-NF-03 | Crash khi Qdrant/Ollama down |
| F-19 | Toàn vẹn dữ liệu | P0 | REQ-NF-04 | Xoá dở dang, trùng point |
| F-20 | Ranh giới bảo mật/no-auth | P0 | REQ-NF-05 | Lộ dữ liệu nội bộ |
| F-21 | Chất lượng mã nguồn | P1 | REQ-NF-06 | Regression, type/lint |
| F-22 | Tính di động cấu hình | P1 | REQ-NF-07 | Không chạy được máy khác |
| F-23 | Khả dụng giao diện tiếng Việt | P1 | REQ-NF-08 | Trạng thái/empty state khó hiểu |

### 4.2 Ma trận mức kiểm thử

Ký hiệu: ✓ = có thực hiện; — = không áp dụng/chưa làm.

| Tính năng | Unit | Integration | System/E2E | UAT | Regression | Performance | Security |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| F-01 Upload | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| F-02 Multi-file | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| F-03 Validate PDF | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| F-04 Danh sách/trạng thái | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| F-05 Xoá cứng | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| F-06 Chat gating | ✓ | — | ✓ | ✓ | ✓ | — | — |
| F-07 Grounded/NOT_FOUND | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| F-08 Multi-doc | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| F-09 Nguồn | ✓ | — | ✓ | ✓ | ✓ | — | ✓ |
| F-10 Streaming/session | ✓ | — | ✓ | ✓ | ✓ | ✓ | — |
| F-11 Eval | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| F-12 Cấu hình | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| F-13 Xử lý lỗi | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| F-14 Qdrant lifecycle | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| F-15 Progress | ✓ | — | ✓ | ✓ | ✓ | — | — |
| F-16 Chất lượng RAG | — | ✓ | ✓ | ✓ | ✓ | — | — |
| F-17 Hiệu năng | — | — | ✓ | — | — | ✓ | — |
| F-18 Reliability | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| F-19 Data integrity | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| F-20 No-auth boundary | — | — | ✓ | ✓ | — | — | ✓ |
| F-21 Code quality | ✓ | — | — | — | ✓ | — | — |
| F-22 Portability | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| F-23 Usability | — | — | ✓ | ✓ | ✓ | — | — |

### 4.3 Mô tả tính năng và tiêu chí chấp nhận

| Mã | Mô tả | Tiêu chí chấp nhận chính |
|---|---|---|
| F-01 | Upload PDF hợp lệ, lưu file, tạo metadata, chunk, embedding, upsert Qdrant | Có row `READY`, file tồn tại, point đúng số chunk, UI hiển thị tài liệu |
| F-02 | Chọn nhiều file, xử lý lần lượt | Tất cả file hợp lệ `READY`; file lỗi `ERROR`; file hợp lệ không bị rollback |
| F-03 | Từ chối file sai định dạng/size/page/mã hoá/scan | Mã lỗi và thông báo tiếng Việt đúng; không tạo dữ liệu rác |
| F-04 | Danh sách tài liệu và trạng thái | Hiển thị tên, dung lượng, số trang, ngày, trạng thái; thứ tự mới nhất |
| F-05 | Xoá tài liệu | Qdrant hết point, SQLite hết row, file mất, chat history reset |
| F-06 | Chat chỉ khi có tài liệu `READY` | Chat input disabled khi rỗng/chỉ lỗi/đang xử lý |
| F-07 | RAG trả lời từ context, ngưỡng điểm | Có câu trả lời + nguồn khi có hit; `NOT_FOUND` khi không đủ căn cứ |
| F-08 | Hỏi trên nhiều tài liệu | Câu trả lời tổng hợp; nguồn đến từ ≥2 file khi phù hợp |
| F-09 | Nguồn | Tên file, số trang 1-based, snippet; không trùng lặp; không bịa nguồn |
| F-10 | Stream và history | Token hiển thị dần; history trong session; lỗi có thông báo |
| F-11 | Eval | 30 câu chạy được; JSON/Markdown có score, pass/fail, latency |
| F-12 | Config | Default Ollama; override env; dimension check rõ ràng |
| F-13 | Error mapping | Mã lỗi ổn định; message thân thiện; không lộ secret/stack |
| F-14 | Qdrant lifecycle | Tạo collection đúng 768; kiểm tra mismatch; xoá/reindex đúng |
| F-15 | Progress | Người dùng thấy trạng thái trong quá trình upload; lỗi giữa chừng rõ |
| F-16 | Quality | In-doc ≥ 80%, citation ≥ 90%, out-of-scope ≥ 9/10 (mục tiêu PRD) |
| F-17 | Performance | Có baseline; không có regression lớn giữa các lần chạy |
| F-18 | Reliability | Dependency down → thông báo, không crash; retry đúng giới hạn |
| F-19 | Integrity | Không trùng point/row; delete idempotent; rollback khi lỗi |
| F-20 | Security | Không lộ key/nội dung log; cảnh báo no-auth; filename được escape |
| F-21 | Code quality | Test/lint/type pass; coverage ≥ 80% |
| F-22 | Portability | Chạy được Python 3.12+; Docker Compose; Ollama/OpenAI |
| F-23 | Usability | UI tiếng Việt, empty/error/ready state rõ ràng, thao tác xoá có xác nhận |

---

## 5.0 Tính năng không kiểm thử (Out of Scope)

Các mục dưới đây có trong PRD/SADD đầy đủ nhưng **không được triển khai** trong MVP
đơn giản hoá. Chúng không được tính vào tỷ lệ coverage của bản test plan này; nếu
được đưa trở lại phạm vi, cần lập test plan bổ sung.

| Mã | Tính năng | Lý do loại trừ | Xử lý |
|---|---|---|---|
| OOS-01 | Đăng nhập, SSO/OIDC, phân quyền, RBAC | MVP không có auth | Ghi rủi ro; kiểm soát mạng nội bộ |
| OOS-02 | Multi-user, tenant, quota theo user | Một người dùng/demo | Không test |
| OOS-03 | PostgreSQL/pgvector, Redis, worker nền | Thay bằng SQLite/Qdrant/đồng bộ | Không test |
| OOS-04 | Object storage (S3/MinIO) | Lưu file local | Không test |
| OOS-05 | OCR PDF scan/ảnh | Trả `PDF_NO_TEXT` | Chỉ test trường hợp không text |
| OOS-06 | DOCX/PPTX/XLSX/HTML | Chỉ PDF | Không test |
| OOS-07 | Source viewer mở đúng trang | Chỉ hiển thị nguồn dạng text | Không test |
| OOS-08 | Chat history bền vững | Chỉ session state | Test reset, không test persistence |
| OOS-09 | Streaming cancellation/retry UI | Retry ở tầng client, không có nút cancel | Không test UI cancel |
| OOS-10 | Telemetry, feedback, dashboard | Không triển khai | Không test |
| OOS-11 | Admin/config UI | Cấu hình qua env | Không test |
| OOS-12 | Duplicate file detection/replace | Không triển khai | Không test |
| OOS-13 | Retry ingestion từ UI | Không triển khai | Test báo lỗi, không test nút retry |
| OOS-14 | Multi-format citation/annotation | Không triển khai | Không test |
| OOS-15 | Load test nhiều người dùng | Demo nội bộ | Chỉ baseline 1 user |
| OOS-16 | Penetration test, SAST/DAST đầy đủ | Ngoài phạm vi MVP | Security checklist mức cơ bản |
| OOS-17 | WCAG 2.1 AA đầy đủ | Streamlit mặc định | Kiểm tra khả dụng cơ bản |
| OOS-18 | Mobile native/responsive đầy đủ | Desktop-first | Smoke test mức dùng được |
| OOS-19 | Đa ngôn ngữ | UI tiếng Việt | Không test i18n |
| OOS-20 | Migration dữ liệu từ hệ thống cũ | Không có | Không test |

---

## 6.0 Phương pháp và kỹ thuật kiểm thử

### 6.1 Chiến lược tổng thể

- **Risk-based:** ưu tiên P0 cho upload/ingest, delete, grounded answer và cấu hình
  Ollama 768; các tính năng P2 được kiểm tra sau khi P0/P1 ổn định.
- **Shift-left:** unit test cho logic thuần (PDF, chunk, RAG, config, error mapping),
  integration test cho SQLite/Qdrant/ingest, system test cho Streamlit + AI thật.
- **Automation-first:** mọi logic có thể test không cần UI/AI thật đều được tự động
  hoá bằng pytest; UI dùng Streamlit `AppTest`; E2E dùng checklist thủ công có evidence.
- **Quality gate bằng eval:** bộ 30 câu là cổng chất lượng, không chỉ là demo.
- **Test independence:** mỗi test dùng `tmp_path`/collection riêng; không phụ thuộc
  thứ tự; dọn dữ liệu sau khi chạy.
- **Không mock hành vi đang cần kiểm chứng:** integration Qdrant dùng Qdrant thật;
  unit được phép mock OpenAI client; E2E dùng Ollama thật.

### 6.2 Các mức kiểm thử

| Mức | Mục tiêu | Công cụ / cách chạy | Entry | Exit |
|---|---|---|---|---|
| Unit (UT) | Logic thuần, boundary, error mapping | `pytest -q -m "not integration"` | Code build, dependency cài | 100% pass; coverage ≥ 80%; không có P0/P1 fail |
| Integration (IT) | SQLite, Qdrant, pipeline ingest, eval schema | `pytest -q -m integration`, Qdrant sống | Qdrant healthy; collection test riêng | 100% pass; không rò dữ liệu test |
| System/E2E (ST) | Upload → chat → source → delete trên app thật | Streamlit + Qdrant + Ollama; checklist | E3 sẵn sàng, model đã pull | Tất cả P0 pass; không Critical/High |
| Acceptance (UAT) | Người dùng xác nhận US-01…US-09 | Kịch bản UAT, Product Owner | ST pass; eval có báo cáo | PO ký; các mục waiver được ghi rõ |
| Regression (RT) | Không làm hỏng hành vi cũ | Full pytest + eval + smoke | Có thay đổi code/config | 100% pass; eval không giảm quá 5 điểm % |
| Performance (PT) | Baseline latency/tài nguyên | Đo thủ công có log | E3, model warm | Có số liệu; không regression > 20% |
| Security (SEC) | Ranh giới no-auth, secret, filename | Checklist + test thủ công | Build cuối | Không phát hiện lỗi High/Critical trong phạm vi |

**Thứ tự thực hiện khuyến nghị:** UT → IT → ST (upload/delete trước, chat sau) →
eval → UAT → regression → test summary.

### 6.3 Các loại kiểm thử

#### 6.3.1 Kiểm thử chức năng

Bao phủ: upload đơn/nhiều file, validate PDF, extract/chunk, embedding, Qdrant,
SQLite, ingest, chat, nguồn, xoá, session, eval. Test case chi tiết ở §6.6.

#### 6.3.2 Kiểm thử tích hợp và interface

| Mã | Interface | Kiểm tra | Test case |
|---|---|---|---|
| IF-01 | `POST {OPENAI_BASE_URL}/embeddings` | Model, batch input, thứ tự vector, dimension, lỗi 401/429/5xx | TC-EMB-001…003 |
| IF-02 | `POST {OPENAI_BASE_URL}/chat/completions` | Stream token, empty content, retry trước token, không retry sau token | TC-LLM-001…003 |
| IF-03 | Qdrant collection API | Tạo/kiểm tra collection, dimension, health, xoá | TC-QD-001, TC-QD-004 |
| IF-04 | Qdrant upsert/query | Payload, idempotent, top-k, threshold, filter document | TC-QD-002/003 |
| IF-05 | SQLite | Schema, CRUD, transaction, delete idempotent | TC-DB-001/002 |
| IF-06 | Filesystem | Lưu file theo UUID, đường dẫn tuyệt đối, xoá file | TC-DB-003, TC-UI-004 |
| IF-07 | Ollama runtime | `ollama serve`, model pull, kết nối 11434 | TC-COMP-001, ST |
| IF-08 | Streamlit session | State chat, rerun, reset khi xoá/refresh | TC-UI-006 |

> Ứng dụng **không có public REST API**. Các interface trên là dependency outbound
> (Ollama/OpenAI/Qdrant) hoặc lưu trữ local; không test API công khai của app.

#### 6.3.3 Kiểm thử hệ thống / end-to-end

Các luồng chính:

1. **Happy path:** mở app → upload 1 PDF → `READY` → hỏi câu có đáp án → thấy câu
   trả lời + nguồn → xoá → tài liệu biến mất, chat reset.
2. **Multi-file:** upload 3 fixture → hỏi câu cần tổng hợp → nguồn từ nhiều file.
3. **Lỗi upload:** upload file sai/scan/quá trang → thông báo đúng, app vẫn dùng được.
4. **Dependency lỗi:** Qdrant down, Ollama down, dimension mismatch → thông báo, không crash.
5. **Session:** refresh → history mất; xoá tài liệu → history reset.

#### 6.3.4 Kiểm thử chấp nhận (UAT)

| Mã | Kịch bản UAT | Người thực hiện | Tiêu chí đạt |
|---|---|---|---|
| UAT-01 | Upload và hỏi đáp trên một tài liệu | PO/QA | Câu trả lời đúng, có nguồn, thao tác ≤ 3 bước |
| UAT-02 | Upload nhiều tài liệu, hỏi câu tổng hợp | PO | Tổng hợp đúng, nguồn từ ≥ 2 file |
| UAT-03 | Hỏi ngoài phạm vi tài liệu | PO | `NOT_FOUND`, không bịa |
| UAT-04 | Upload file lỗi | PO | Thông báo tiếng Việt dễ hiểu |
| UAT-05 | Xoá tài liệu | PO | Không còn tài liệu/nguồn trong chat |
| UAT-06 | Đánh giá chất lượng 30 câu | PO + QA | Đạt ngưỡng hoặc có waiver |

#### 6.3.5 Kiểm thử hồi quy

| Bộ | Khi nào | Lệnh / cách chạy |
|---|---|---|
| RT-01 | Mỗi PR | `pytest -q -m "not integration"` |
| RT-02 | Thay đổi Qdrant/ingest | `pytest -q -m integration` |
| RT-03 | Trước release | `pytest -q && ruff check . && mypy app` |
| RT-04 | Thay đổi prompt/model | `python -m app.eval --reindex --out eval_report` |
| RT-05 | Thay đổi UI | `AppTest` + checklist E2E |

#### 6.3.6 Kiểm thử phi chức năng

| Loại | Phạm vi | Cách đo / tiêu chí |
|---|---|---|
| Performance | 1 PDF nhỏ, 1 câu hỏi | Upload + embed + upsert; retrieval; first token; full answer. Ghi p50/p95, không SLA cứng |
| Reliability | Qdrant/Ollama down, timeout, 429 | Không crash; message thân thiện; retry đúng (embedding 3, LLM 2) |
| Data integrity | Delete, retry, idempotency | Không point/row/file mồ côi; delete lặp lại không lỗi |
| Security cơ bản | Secret, log, filename, exposure | Không lộ key/nội dung; filename escape; cảnh báo no-auth |
| Compatibility | Python 3.12+, Chrome/Firefox, Docker | Chạy theo README; compose config hợp lệ |
| Accessibility | Bàn phím, độ tương phản, label | Kiểm tra cơ bản; không phải WCAG audit |
| Maintainability | Test/lint/type/coverage | Xem §7 |

**Mục tiêu hiệu năng tạm thời** (đo trên máy tham chiếu, Ollama warm; dùng để phát
hiện regression, không phải cam kết SLA):

| Chỉ số | Mục tiêu tạm thời |
|---|---|
| Thời gian app render lần đầu | ≤ 3 giây (không tính load model) |
| Upload + ingest 1 PDF 1–3 trang | ≤ 30 giây |
| Retrieval (embedding + Qdrant) p95 | ≤ 3 giây |
| First token p90 | ≤ 10 giây |
| Toàn bộ câu trả lời ngắn | ≤ 60 giây |
| RAM tiến trình app | ≤ 2 GB (không tính Ollama) |

### 6.4 Dữ liệu kiểm thử

| Nhóm | Nội dung | Cách tạo / lưu |
|---|---|---|
| Hợp lệ | 3 PDF tiếng Việt: hợp đồng, báo giá, quy định | `python tests/eval/generate_fixtures.py` |
| Biên | PDF đúng max size, max+1, max page, max+1 page | Sinh trong test hoặc thủ công |
| Lỗi | File `.txt` đổi tên `.pdf`, PDF corrupt, PDF mã hoá, PDF scan/no-text | Sinh trong test; không dùng PII |
| Eval | 30 câu: 10 in-doc, 10 multi-doc, 10 out-of-scope | `tests/eval/dataset.json` |
| Trạng thái | Tài liệu `PROCESSING`, `READY`, `ERROR` | Seed SQLite hoặc mock |
| Qdrant | Vector giả 768 chiều | Fixture test; collection tạm |

**Quy tắc dữ liệu:**

- Không dùng tài liệu thật của khách hàng/khách hàng nội bộ trong test.
- Không commit fixture PDF vào Git (đã gitignore); chỉ commit generator/dataset.
- Xoá `data/` và collection test sau khi chạy; không dùng chung collection production.
- Ghi lại model, dimension, commit hash và môi trường trong mỗi báo cáo eval.

### 6.5 Môi trường kiểm thử

| Mã | Môi trường | Thành phần | Mục đích |
|---|---|---|---|
| E1 | Unit local | Python venv, fake OpenAI/Qdrant | UT nhanh, không cần mạng |
| E2 | Integration | Qdrant Docker v1.20, SQLite tạm | IT adapter/ingest |
| E3 | System/UAT | Streamlit + Qdrant + Ollama (`llama3.1`, `nomic-embed-text`) | E2E, eval, UAT |
| E4 | OpenAI tùy chọn | API OpenAI-compatible, key thật | Kiểm tra tính di động cấu hình |

**Thông số E3:**

| Thành phần | Giá trị |
|---|---|
| OS | Linux (máy kiểm thử hiện tại); Python 3.12+ (hiện 3.14.4) |
| App | Streamlit 1.66.1, port 8501 |
| Qdrant | `qdrant/qdrant:v1.20.0`, port 6333 |
| Ollama | `llama3.1`, `nomic-embed-text`, port 11434 |
| Embedding | 768 chiều |
| SQLite/file | `data/` local, cấu hình qua `DATA_DIR`/`SQLITE_PATH` |
| Trình duyệt | Chrome/Firefox bản mới, viewport 1440×900 và 1280×720 |
| Dữ liệu | Fixture TD-01…TD-03, collection `document_chunks` sạch |
| Auth | Không có; chỉ chạy localhost/VPN, không public Internet |

**Lệnh chuẩn bị:**

```bash
# 1. Dependencies
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 2. Qdrant
docker compose up -d
curl -fsS http://localhost:6333/healthz

# 3. Ollama (bắt buộc cho E2E/eval)
ollama serve
ollama pull llama3.1
ollama pull nomic-embed-text
curl -fsS http://localhost:11434/api/tags

# 4. Fixture
python tests/eval/generate_fixtures.py

# 5. App
streamlit run app/main.py
```

**Lệnh kiểm thử:**

```bash
pytest -q -m "not integration"
pytest -q -m integration
pytest -q
pytest --cov=app --cov-report=term-missing
ruff check .
ruff format --check app tests
mypy app
python -m app.eval --reindex --out eval_report
```

---

### 6.6 Danh mục test case chi tiết

> **Quy ước:** `UT` = unit, `IT` = integration, `ST` = system/E2E, `UAT` = acceptance.
> `A` = automated, `M` = manual, `A+M` = automated một phần + kiểm tra thủ công.
> Trạng thái baseline: xem §6.8 và Appendix B.

#### 6.6.1 Upload và xử lý PDF

| ID | Tên | Mức | Ưu tiên | Tiền điều kiện | Các bước | Kết quả mong đợi | Truy vết | Tự động |
|---|---|---|---|---|---|---|---|---|
| TC-UPL-001 | Upload một PDF hợp lệ | ST/UAT | P0 | Qdrant + Ollama sẵn sàng; fixture TD-01 | Mở app → chọn `hop-dong.pdf` → upload → chờ xử lý | Tài liệu `READY`; đúng tên/size/page; file trong `data/`; Qdrant có point; chat bật | REQ-F-01, US-01 | A+M |
| TC-UPL-002 | Upload nhiều PDF hợp lệ | ST/UAT | P0 | Fixture TD-01…TD-03 | Chọn cả 3 file → upload | Cả 3 `READY`; mỗi file có metadata riêng; không trộn chunk | REQ-F-02, US-02 | A+M |
| TC-UPL-003 | Một file lỗi không chặn file hợp lệ | ST | P0 | 1 PDF hợp lệ + 1 file `.txt` đổi tên `.pdf` | Upload cả hai | File hợp lệ `READY`; file lỗi `ERROR` với thông báo; app không crash | REQ-F-02/03, US-02/03 | M |
| TC-UPL-004 | Từ chối sai định dạng | UT/ST | P0 | File `.txt`/`.docx`; tên không phải `.pdf` | Gọi validate/upload | Lỗi `PDF_NOT_PDF`; không tạo row/file; thông báo tiếng Việt | REQ-F-03, US-03 | A+M |
| TC-UPL-005 | Biên dung lượng | UT | P0 | File size = max và max+1 | Validate từng file | `max` chấp nhận; `max+1` lỗi `PDF_TOO_LARGE`; không lưu file sai | REQ-F-03 | A |
| TC-UPL-006 | Biên số trang | UT | P0 | PDF đúng max page và max+1 page | Validate từng file | `max` chấp nhận; `max+1` lỗi `PDF_TOO_MANY_PAGES` | REQ-F-03 | A |
| TC-UPL-007 | PDF mã hoá | UT/ST | P0 | PDF có mật khẩu | Upload | Lỗi `PDF_ENCRYPTED`; row `ERROR`; không crash | REQ-F-03, US-03 | A+M |
| TC-UPL-008 | PDF corrupt / magic bytes sai | UT/ST | P0 | File rỗng, file header sai, PDF cắt cụt | Upload từng file | Lỗi `PDF_CORRUPT` hoặc `PDF_NOT_PDF`; thông báo rõ; không crash | REQ-F-03 | A+M |
| TC-UPL-009 | PDF scan không có text | UT/ST | P0 | PDF chỉ có ảnh, không text layer | Upload | Lỗi `PDF_NO_TEXT`; hướng dẫn dùng PDF có text; không ingest | REQ-F-03, US-03 | A+M |
| TC-UPL-010 | Metadata, thứ tự và trạng thái | ST | P0 | Ít nhất 2 tài liệu `READY` | Upload lần lượt; quan sát danh sách | Hiển thị tên, size, page, ngày; mới nhất trước; trạng thái đúng | REQ-F-04, US-04/05 | A+M |
| TC-PDF-001 | Extract text, NFC, NUL, trang trắng | UT | P0 | PDF có Unicode tiếng Việt, ký tự NUL, trang trắng | Extract | Text được chuẩn hoá NFC; NUL bị loại; trang trắng bị bỏ qua; không lỗi | REQ-F-01/03 | A |
| TC-PDF-002 | Số trang 1-based và giữ trang | UT | P0 | PDF 3 trang, nội dung khác nhau | Extract/chunk | `page_number` đúng 1,2,3; chunk không lẫn trang | REQ-F-01/09 | A |
| TC-PDF-003 | Tên file Unicode/khoảng trắng | UT | P1 | Tên `hợp đồng (bản 1).pdf` | Upload/validate | Chấp nhận; lưu an toàn; UI hiển thị đúng; không path traversal | REQ-F-03/09 | A |

#### 6.6.2 Chunking và embedding

| ID | Tên | Mức | Ưu tiên | Tiền điều kiện | Các bước | Kết quả mong đợi | Truy vết | Tự động |
|---|---|---|---|---|---|---|---|---|
| TC-CHK-001 | Kích thước chunk và overlap | UT | P0 | Text dài > chunk size | Chunk với cấu hình mặc định | Mỗi chunk ≤ `CHUNK_SIZE`; overlap đúng; không mất nội dung | REQ-F-01 | A |
| TC-CHK-002 | Không chunk qua ranh giới trang | UT | P0 | PDF 2 trang, câu dài sát cuối trang | Chunk | Không có chunk chứa text của 2 trang; `page_number` đúng | REQ-F-01/09 | A |
| TC-CHK-003 | Ưu tiên ranh giới câu, index toàn cục | UT | P1 | Text nhiều câu, nhiều trang | Chunk | Cắt tại câu khi có thể; `chunk_index` tăng liên tục toàn tài liệu | REQ-F-01 | A |
| TC-CHK-004 | Trang chỉ có whitespace | UT | P1 | PDF có trang trắng | Chunk | Trang trắng không tạo chunk rỗng; không lỗi embedding | REQ-F-03 | A |
| TC-EMB-001 | Batch, thứ tự và số vector | UT | P0 | 5 text, batch size 2 | Mock embeddings | Gọi đúng số batch; vector trả về đúng thứ tự; length khớp input | REQ-F-01/12 | A |
| TC-EMB-002 | Dimension khớp cấu hình | UT/IT | P0 | Vector 768; cấu hình 768 | Embed/validate | Chấp nhận; nếu vector khác dimension → lỗi rõ, không upsert | REQ-F-12/14 | A |
| TC-EMB-003 | Retry và lỗi embedding | UT | P0 | Mock 429/timeout 2 lần rồi thành công; mock lỗi 401 | Gọi `embed_texts` | Retry tối đa 3; thành công sau retry; lỗi không retry được → `EmbeddingError` | REQ-F-13, REQ-NF-03 | A |
| TC-EMB-004 | Text rỗng | UT | P1 | Danh sách có chuỗi rỗng/whitespace | Gọi embed | Lỗi `EmbeddingError`, không gọi API | REQ-F-13 | A |
| TC-EMB-005 | Batch size biên | UT | P2 | 0, 1, đúng batch, batch+1 text | Gọi embed | 0 → `[]`; các trường hợp còn lại đúng số batch/vector | REQ-F-01 | A |

#### 6.6.3 SQLite, Qdrant và ingest

| ID | Tên | Mức | Ưu tiên | Tiền điều kiện | Các bước | Kết quả mong đợi | Truy vết | Tự động |
|---|---|---|---|---|---|---|---|---|
| TC-DB-001 | Tạo/đọc/cập nhật tài liệu | UT/IT | P0 | SQLite tạm | Tạo row, đọc, cập nhật `READY`/`ERROR` | Dữ liệu đúng; status/metadata không mất; timestamps hợp lệ | REQ-F-04/14 | A |
| TC-DB-002 | List, delete và idempotency | UT/IT | P0 | 2 row | List; xoá 1; xoá lại | Danh sách đúng; xoá row mục tiêu; xoá lặp lại không lỗi | REQ-F-05, REQ-NF-04 | A |
| TC-DB-003 | Khởi tạo schema và đường dẫn | UT | P1 | DB chưa tồn tại; `DATA_DIR` tùy chỉnh | Init 2 lần; kiểm tra path | Schema tạo một lần; path tuyệt đối; không ghi ngoài `DATA_DIR` | REQ-F-12, REQ-NF-07 | A |
| TC-QD-001 | Collection, dimension và health | IT | P0 | Qdrant sạch | Ensure collection 768; gọi health; thử collection 1536 | Tạo đúng 768; health true; mismatch bị phát hiện với thông báo | REQ-F-12/14, US-01 | A |
| TC-QD-002 | Upsert, payload và idempotency | IT | P0 | Collection sạch; 3 chunk | Upsert 2 lần cùng ID; query payload | Không nhân đôi point; payload có doc/chunk/page/text; count đúng | REQ-F-01, REQ-NF-04 | A |
| TC-QD-003 | Query top-k, threshold, filter | IT | P0 | Point từ 2 tài liệu | Query không filter; query theo `document_id`; threshold cao | Top-k đúng; filter chỉ trả tài liệu chọn; threshold loại điểm thấp | REQ-F-07/08 | A |
| TC-QD-004 | Xoá point theo tài liệu | IT | P0 | 2 tài liệu có point | Xoá theo `document_id`; kiểm tra count; xoá lại | Chỉ point mục tiêu bị xoá; tài liệu khác còn; xoá lặp idempotent | REQ-F-05 | A |
| TC-QD-005 | Qdrant không khả dụng | IT/ST | P1 | Qdrant dừng | Gọi health/upsert/query | Trả lỗi `QDRANT_UNAVAILABLE`; app hiển thị banner; không crash | REQ-F-13, REQ-NF-03 | A+M |
| TC-ING-001 | Happy path và progress | IT/ST | P0 | Qdrant + mock/real embedding | Ingest 1 PDF; quan sát callback/progress | Row `PROCESSING` → `READY`; progress tăng; file + vector + DB khớp | REQ-F-01/15 | A+M |
| TC-ING-002 | Lỗi embedding giữa pipeline | IT | P0 | Mock embedding lỗi | Ingest | Row `ERROR`; không upsert dở; file không bị coi là `READY`; message rõ | REQ-F-13, REQ-NF-04 | A |
| TC-ING-003 | Lỗi tạo row/file | IT | P1 | DB/file lỗi (mock) | Ingest | Không có tài liệu `READY` giả; cleanup phần đã tạo; lỗi được map | REQ-F-13, REQ-NF-04 | A |
| TC-ING-004 | Nhiều file, rollback độc lập | IT/ST | P0 | 2 file, 1 file lỗi | Ingest tuần tự | File tốt `READY`; file lỗi `ERROR`; không rollback file tốt | REQ-F-02, REQ-NF-04 | A+M |
| TC-ING-005 | Xoá sau ingest | IT | P0 | Tài liệu `READY` | Xoá qua UI/service | Không còn point/row/file; chat reset; list cập nhật | REQ-F-05 | A+M |

#### 6.6.4 Giao diện và trạng thái ứng dụng

| ID | Tên | Mức | Ưu tiên | Tiền điều kiện | Các bước | Kết quả mong đợi | Truy vết | Tự động |
|---|---|---|---|---|---|---|---|---|
| TC-UI-001 | Empty state và chat bị tắt | ST/UAT | P0 | DB rỗng, Qdrant sạch | Mở app | Có hướng dẫn upload; chat input disabled; thông báo không có tài liệu | REQ-F-06, REQ-NF-08, US-04/07 | A+M |
| TC-UI-002 | Tài liệu đang xử lý/lỗi | ST | P0 | Seed tài liệu `PROCESSING`/`ERROR` | Mở app | Chat disabled; hiển thị trạng thái và lỗi tương ứng; không crash | REQ-F-04/06 | A+M |
| TC-UI-003 | Tài liệu `READY`, chat bật | ST/UAT | P0 | 1 tài liệu `READY` | Mở app; xem sidebar/chat | Chat bật; tên/size/page/ngày/trạng thái đúng; nút xoá khả dụng | REQ-F-04/06, US-04/05 | A+M |
| TC-UI-004 | Xoá: huỷ và xác nhận | ST/UAT | P0 | 1–2 tài liệu `READY` | Bấm xoá → huỷ; bấm lại → xác nhận | Huỷ không thay đổi; xác nhận xoá đúng 1 tài liệu + dữ liệu liên quan; list/chat cập nhật | REQ-F-05, US-06 | M |
| TC-UI-005 | Qdrant down và dimension mismatch | ST | P0 | Qdrant dừng; sau đó collection 1536 | Mở app; upload/thử chat | Banner lỗi rõ; không crash; hướng dẫn reindex/recreate; chat không treo | REQ-F-13, REQ-F-14, REQ-NF-03 | A+M |
| TC-UI-006 | History và refresh | ST | P1 | Đã chat 1 câu | Gửi câu hỏi; refresh; xoá tài liệu | History hiển thị trong session; refresh làm mất; xoá reset history | REQ-F-10, US-07 | A+M |
| TC-UI-007 | Escape Markdown/HTML từ tên file/nội dung | UT/ST | P1 | Tên file chứa `**`, `<script>`, `[x](y)` | Upload; xem list/nguồn | Hiển thị literal/được escape; không chạy script; không vỡ layout | REQ-F-09, REQ-NF-05 | A+M |
| TC-UI-008 | Progress và lỗi upload | ST | P2 | 1 PDF lớn vừa phải; 1 file lỗi | Upload; quan sát progress/trạng thái | Có phản hồi trong khi xử lý; lỗi hiển thị rõ; UI không đơ vô hạn | REQ-F-15 | M |

#### 6.6.5 Chat, RAG, nguồn và LLM

| ID | Tên | Mức | Ưu tiên | Tiền điều kiện | Các bước | Kết quả mong đợi | Truy vết | Tự động |
|---|---|---|---|---|---|---|---|---|
| TC-RAG-001 | Chọn hit, dedupe, đa dạng tài liệu | UT/IT | P0 | Hit từ 2 tài liệu, có trùng | Gọi retrieve/select | Top-k đúng; không trùng chunk; ưu tiên đa dạng tài liệu khi phù hợp | REQ-F-07/08 | A |
| TC-RAG-002 | Context budget và prompt | UT | P0 | Nhiều chunk, context dài | Build context/prompt | Không vượt budget; giữ câu hỏi + context + hướng dẫn `NOT_FOUND` | REQ-F-07 | A |
| TC-RAG-003 | Không có hit | UT | P0 | Qdrant trả rỗng/điểm thấp | Hỏi | Trả `NOT_FOUND`; không gọi LLM; không tạo nguồn giả | REQ-F-07, US-08 | A |
| TC-RAG-004 | Lọc theo tài liệu được chọn | UT/IT | P1 | 2 tài liệu | Hỏi với filter 1 tài liệu | Chỉ dùng chunk của tài liệu đó; nguồn tương ứng | REQ-F-08 | A |
| TC-LLM-001 | Stream token bình thường | UT | P0 | Mock stream 3 token | Gọi `stream_chat` | Yield đúng thứ tự; kết thúc sạch; không lặp | REQ-F-10 | A |
| TC-LLM-002 | Retry trước khi có token | UT | P0 | Mock lỗi lần 1, thành công lần 2 | Gọi stream | Retry 1 lần; trả nội dung; không lộ lỗi trung gian | REQ-F-13, REQ-NF-03 | A |
| TC-LLM-003 | Không retry sau khi đã stream | UT | P1 | Mock yield 1 token rồi lỗi | Gọi stream | Không phát lại toàn bộ; lỗi được báo; không nhân đôi token | REQ-F-10, REQ-NF-03 | A |
| TC-LLM-004 | LLM trả rỗng/không có content | UT | P1 | Mock stream rỗng | Gọi stream | Lỗi `LLMError`/thông báo; UI không treo | REQ-F-13 | A |
| TC-CHAT-001 | Hỏi đáp có căn cứ + nguồn | ST/UAT | P0 | TD-01 `READY`; Ollama sẵn sàng | Hỏi câu có đáp án trong hợp đồng | Trả lời đúng thông tin; có tên file + trang; không bịa | REQ-F-07/09, US-07/08 | A+M |
| TC-CHAT-002 | Tổng hợp nhiều tài liệu | ST/UAT | P0 | TD-01…TD-03 `READY` | Hỏi câu cần so sánh/tổng hợp | Câu trả lời dùng ≥ 2 tài liệu khi phù hợp; nguồn từ nhiều file | REQ-F-08, US-09 | A+M |
| TC-CHAT-003 | Câu hỏi ngoài phạm vi | ST/UAT | P0 | Chỉ có TD-01 | Hỏi về chủ đề không có trong tài liệu | `NOT_FOUND`/không đủ thông tin; không bịa; không nguồn giả | REQ-F-07, US-08/11 | A+M |
| TC-CHAT-004 | Hiển thị nguồn | ST | P1 | Trả lời có 3 nguồn | Mở phần nguồn | Đúng file/trang/snippet; không trùng; thứ tự hợp lý; không lỗi render | REQ-F-09, US-09/10 | A+M |
| TC-CHAT-005 | Lỗi LLM/Qdrant khi chat | ST | P0 | Dừng Ollama; sau đó dừng Qdrant | Gửi câu hỏi | Thông báo thân thiện; không lộ stack/key; app vẫn dùng được khi dependency trở lại | REQ-F-13, REQ-NF-03 | M |
| TC-CHAT-006 | Câu hỏi rỗng/rất dài | ST | P1 | Tài liệu `READY` | Gửi chuỗi rỗng/khoảng trắng; câu > giới hạn | Không gọi API với câu rỗng; câu dài được cắt hợp lý hoặc báo giới hạn | REQ-F-06/10 | A+M |

#### 6.6.6 Eval, chất lượng và phi chức năng

| ID | Tên | Mức | Ưu tiên | Tiền điều kiện | Các bước | Kết quả mong đợi | Truy vết | Tự động |
|---|---|---|---|---|---|---|---|---|
| TC-EVAL-001 | Schema và số lượng dataset | UT | P0 | `dataset.json` | Load/validate | Đúng 30 câu; mỗi câu có id/câu hỏi/loại/đáp án kỳ vọng; không trùng ID | REQ-F-11 | A |
| TC-EVAL-002 | Chấm điểm in-doc/multi/out-of-scope | UT | P0 | Kết quả giả lập đúng/sai | Chạy scorer | Điểm đúng theo rubric; `NOT_FOUND` được chấm đúng; không chia 0 | REQ-F-11, REQ-NF-01 | A |
| TC-EVAL-003 | Báo cáo JSON/Markdown | IT/ST | P1 | Qdrant + Ollama; fixture | Chạy `--reindex --out eval_report` | Sinh JSON + Markdown; có score, pass/fail, latency, model/dim; đọc được | REQ-F-11 | A+M |
| TC-EVAL-004 | Reindex và dữ liệu sạch | IT | P0 | Collection cũ/dữ liệu lẫn | Chạy `--reindex` | Xoá/ingest lại đúng; không nhân đôi point; eval dùng dữ liệu mới | REQ-F-11, REQ-F-14 | A+M |
| TC-EVAL-005 | Thiếu Ollama/model/key | ST | P1 | Ollama tắt hoặc model chưa pull | Chạy eval/chat | Lỗi cấu hình rõ; hướng dẫn pull model; không crash mơ hồ | REQ-F-12/13 | M |
| TC-NFR-001 | Unit/lint/type/coverage | UT | P0 | Venv đầy đủ | Chạy pytest, ruff, mypy | 100% pass; coverage ≥ 80%; lint/type sạch | REQ-NF-06 | A |
| TC-NFR-002 | Baseline hiệu năng | ST | P2 | E3, model warm; fixture | Upload 1 file; hỏi 1 câu; ghi thời gian | Có p50/p95 cho ingest/retrieval/first token; ghi môi trường | REQ-NF-02 | M |
| TC-NFR-003 | Dọn dẹp và cô lập test | IT | P1 | Chạy full suite | Kiểm tra collection/data sau test | Không còn collection test; không ảnh hưởng dữ liệu thật; chạy lại vẫn pass | REQ-NF-04, REQ-NF-06 | A |
| TC-SEC-001 | Không lộ secret/nội dung nhạy cảm | UT/ST | P0 | Cấu hình có key giả; log bật | Kiểm tra log/UI/exception | Không in key; không log full PDF/context; lỗi không lộ stack ra UI | REQ-NF-05 | A+M |
| TC-SEC-002 | Ranh giới no-auth | ST | P0 | App chạy localhost | Truy cập từ máy khác trong LAN (nếu bind 0.0.0.0); đọc README cảnh báo | Hành vi đúng tài liệu; cảnh báo không public; không tuyên bố có auth | REQ-NF-05 | M |
| TC-SEC-003 | Filename/path traversal/Markdown | UT/ST | P1 | Tên `../../evil.pdf`, `<script>`, `**bold**` | Upload/xem UI | Lưu trong `DATA_DIR` bằng UUID; không ghi ngoài; render an toàn | REQ-F-09, REQ-NF-05 | A+M |
| TC-COMP-001 | Python/Docker/browser | ST | P1 | Máy sạch theo README | Cài đặt, compose up, chạy app trên Chrome/Firefox | Cài được; compose config hợp lệ; app render; không lỗi phiên bản | REQ-NF-07 | M |
| TC-ACC-001 | Khả dụng cơ bản | ST | P2 | App có tài liệu | Dùng bàn phím Tab/Enter; kiểm tra label/contrast | Có thể thao tác chính; label rõ; không phải audit WCAG đầy đủ | REQ-NF-08 | M |

### 6.7 Quy trình thực hiện và bằng chứng

1. **Chuẩn bị:** xác nhận commit hash, Python/model/Qdrant version; chạy
   `generate_fixtures.py`; kiểm tra Qdrant health và Ollama tags.
2. **UT/IT:** chạy lệnh; lưu log `pytest` + coverage; đính kèm vào test summary.
3. **ST:** chạy checklist `docs/testing/manual-checklist.md` nếu có (nếu chưa, dùng
   Phụ lục D); chụp màn hình các trạng
   thái empty/ready/error/chat/source/delete; ghi thời gian và model.
4. **Eval:** chạy `python -m app.eval --reindex --out eval_report`; lưu JSON/Markdown;
   ghi rõ model, dimension, dataset version, commit.
5. **UAT:** PO thực hiện UAT-01…UAT-06; ký biên bản; ghi waiver (nếu có).
6. **Regression:** chạy lại toàn bộ; so sánh eval với baseline; ghi chênh lệch.
7. **Kết thúc:** cập nhật traceability, defect log, test summary; lưu evidence trong
   `eval_report/` và ticket/PR.

### 6.8 Quản lý defect

| Severity | Định nghĩa | Ví dụ | Xử lý |
|---|---|---|---|
| Critical | Mất dữ liệu, lộ bí mật, app không dùng được | Xoá nhầm file; lộ API key; crash mọi upload | Chặn release; fix ngay |
| High | Luồng P0 sai, không có workaround | Upload PDF hợp lệ thất bại; chat bịa nguồn; delete sót vector | Chặn acceptance; fix trong cycle |
| Medium | Luồng P1 sai, có workaround | Nguồn thiếu trang; progress không cập nhật; lỗi message chưa rõ | Fix trước release hoặc waiver |
| Low | Lỗi UI/cosmetic, không ảnh hưởng chức năng | Khoảng trắng, thứ tự nguồn chưa tối ưu | Backlog |

**Priority:** P0 = fix ngay; P1 = trong sprint; P2 = sprint sau. Mọi defect phải có
ID, test case phát hiện, môi trường, bước tái hiện, expected/actual, evidence, trạng thái.

---

## 7.0 Tiêu chí đạt/không đạt

### 7.1 Tiêu chí chung

| Mã | Tiêu chí | Cách xác nhận |
|---|---|---|
| PC-01 | 100% test case P0 pass | Bảng kết quả test + evidence |
| PC-02 | Không còn defect Critical/High mở | Defect log |
| PC-03 | 100% yêu cầu in-scope có test case và kết quả | Traceability matrix |
| PC-04 | Unit + integration pass, coverage ≥ 80% | `pytest`, coverage report |
| PC-05 | Ruff/mypy sạch | CI/log |
| PC-06 | E2E upload/chat/source/delete pass với Ollama thật | Checklist + screenshot |
| PC-07 | Eval có báo cáo và đạt ngưỡng hoặc có waiver | JSON/Markdown + PO sign-off |
| PC-08 | Không có dữ liệu test rò rỉ sang môi trường thật | Kiểm tra collection/data |

### 7.2 Tiêu chí theo mức

| Mức | Đạt khi | Không đạt khi |
|---|---|---|
| Unit | Tất cả pass; coverage ≥ 80%; không P0/P1 fail | Có test fail hoặc coverage dưới ngưỡng không giải thích |
| Integration | Tất cả pass trên Qdrant thật; cleanup sạch | Qdrant lỗi/không kết nối; test phụ thuộc thứ tự |
| System | P0 pass; không Critical/High; app không crash | Thiếu môi trường AI/Qdrant; lỗi P0 |
| UAT | PO chấp nhận US-01…US-09; waiver được ghi | PO từ chối hoặc thiếu evidence |
| Regression | Full suite pass; eval không giảm > 5 điểm % | Regression hoặc chất lượng giảm mạnh |
| Security | Không có lỗi High/Critical trong checklist | Lộ key/dữ liệu, path traversal, XSS rõ ràng |

### 7.3 Ngưỡng chất lượng RAG

| Chỉ số | Ngưỡng mục tiêu | Nguồn | Xử lý nếu không đạt |
|---|---|---|---|
| In-document accuracy | ≥ 80% | PRD MET-002 | Phân tích lỗi retrieval/prompt; waiver PO nếu lý do chấp nhận |
| Citation file+page | ≥ 90% | PRD MET-003 | Kiểm tra mapping page/source; không release nếu bịa nguồn |
| Out-of-scope `NOT_FOUND` | ≥ 9/10 | Eval dataset | Tăng grounding/threshold; review prompt |
| Bịa nguồn | 0 trường hợp | Quality gate | Chặn acceptance |
| Lỗi hệ thống khi eval | 0 | Eval report | Chặn eval; fix dependency |

> Các ngưỡng trên là mục tiêu của PRD, **chưa được xác nhận** trong baseline hiện tại
> vì Ollama chưa chạy. Khi chạy eval, ghi rõ kết quả thực tế; không suy diễn từ unit test.

---

## 8.0 Tạm dừng và tiếp tục

### 8.1 Điều kiện tạm dừng

| Mã | Điều kiện | Hành động |
|---|---|---|
| SUS-01 | Ollama không chạy/model chưa pull > 15 phút | Dừng ST/eval; chuyển sang UT/IT; ghi blocker |
| SUS-02 | Qdrant down hoặc collection hỏng | Dừng IT/ST; kiểm tra Docker/health; không xoá dữ liệu thật |
| SUS-03 | Dimension mismatch không xử lý được | Dừng ingest; recreate/reindex theo runbook |
| SUS-04 | Phát hiện Critical (mất dữ liệu/lộ secret) | Dừng cycle; báo Dev/QA Lead; bảo toàn evidence |
| SUS-05 | Môi trường khác baseline nghiêm trọng | Dừng; đồng bộ Python/model/Qdrant version |
| SUS-06 | Dữ liệu test không cô lập/ảnh hưởng dữ liệu thật | Dừng ngay; cleanup; điều tra |

### 8.2 Điều kiện tiếp tục

- Nguyên nhân dừng được xác định và có fix/waiver bằng văn bản.
- Qdrant healthy, Ollama trả lời được, collection đúng 768.
- Chạy lại smoke/regression tối thiểu: UT + upload + một câu chat + delete.
- Ghi lại thời điểm, người xác nhận, phạm vi chạy lại vào test log.

---

## 9.0 Sản phẩm bàn giao

| Mã | Sản phẩm | Nội dung | Người chịu trách nhiệm |
|---|---|---|---|
| D-01 | Test Plan (tài liệu này) | Phạm vi, chiến lược, lịch, tiêu chí | QA Lead |
| D-02 | Test case / checklist | TC chi tiết + manual checklist | QA Engineer |
| D-03 | Automated test suite | `tests/` unit + integration + AppTest | Dev + QA |
| D-04 | Coverage/lint/type report | Log pytest, coverage, ruff, mypy | QA/Dev |
| D-05 | E2E evidence | Screenshot/log upload/chat/source/delete | QA |
| D-06 | Eval report | JSON + Markdown, model/dim/commit | QA |
| D-07 | Defect log | ID, severity, status, evidence | QA |
| D-08 | Traceability matrix | REQ → TC → evidence | QA |
| D-09 | Test summary report | Kết quả, blocker, waiver, kết luận | QA Lead |
| D-10 | UAT sign-off | Biên bản PO | Product Owner |

---

## 10.0 Nhiệm vụ kiểm thử

| ID | Nhiệm vụ | Phụ thuộc | Ước lượng | Đầu ra |
|---|---|---|---|---|
| T-01 | Review requirement/scope, chốt in/out-of-scope | IMP, US | 0,25 ngày | Scope + traceability draft |
| T-02 | Chuẩn bị E1/E2/E3, pull model, fixture | Docker/Ollama | 0,5 ngày | Môi trường sẵn sàng |
| T-03 | Chạy UT + IT, lưu coverage | T-02 | 0,5 ngày | Log test + coverage |
| T-04 | Chạy ST: upload/delete trước, chat/source sau | T-03 | 1,0 ngày | Checklist + screenshot |
| T-05 | Chạy eval 30 câu, phân tích lỗi | T-04 | 0,5 ngày | Eval JSON/MD + nhận xét |
| T-06 | UAT với PO | T-04/T-05 | 0,5 ngày | Biên bản UAT |
| T-07 | Regression + test summary | T-06 | 0,5 ngày | Test summary + waiver |
| T-08 | Cập nhật tài liệu/README/troubleshooting | T-04 | 0,25 ngày | Tài liệu cập nhật |

Tổng QA effort dự kiến: **~4,0 ngày công**, chưa tính thời gian chờ model/fix defect.

---

## 11.0 Nhu cầu môi trường

### 11.1 Phần cứng và hệ điều hành

| Hạng mục | Tối thiểu | Khuyến nghị |
|---|---|---|
| CPU | 4 core | 8 core |
| RAM | 8 GB | 16 GB (Ollama + app + Qdrant) |
| Disk trống | 8 GB | 20 GB (model + PDF + report) |
| OS | Linux/macOS | Linux (Ubuntu) |
| Network | Localhost | Localhost + VPN nội bộ |

### 11.2 Phần mềm

| Thành phần | Phiên bản / ghi chú |
|---|---|
| Python | 3.12+ (baseline hiện tại 3.14.4) |
| Streamlit | 1.66.1 |
| Qdrant | v1.20.0 qua Docker Compose |
| Ollama | Bản mới; model `llama3.1`, `nomic-embed-text` |
| SQLite | Thư viện chuẩn Python |
| PyMuPDF | Theo `pyproject.toml` |
| OpenAI SDK | Theo `pyproject.toml`; dùng cho Ollama/OpenAI-compatible |
| pytest/coverage/ruff/mypy | Theo `.[dev]` |
| Trình duyệt | Chrome/Firefox bản mới |

### 11.3 Dữ liệu, tài khoản và quyền

- **Tài khoản test:** không có; ứng dụng không có auth.
- **Quyền hệ thống:** quyền ghi `data/`, chạy Docker, bind port 8501/6333/11434.
- **Dữ liệu:** chỉ fixture tổng hợp; không dùng PDF thật.
- **Mạng:** không mở app ra Internet; nếu cần truy cập từ xa, dùng VPN/reverse proxy
  có kiểm soát (ngoài phạm vi app).
- **Biến môi trường:** dùng `.env` local hoặc export; không commit `.env`/key.
- **Dọn dẹp:** xoá `data/`, collection test, report tạm sau khi lưu evidence.

---

## 12.0 Trách nhiệm

Ký hiệu RACI: **R** = thực hiện, **A** = chịu trách nhiệm cuối, **C** = tư vấn, **I** = được thông báo.

| Hoạt động | QA Lead | QA Engineer | Dev Backend | Dev UI | PO | DevOps |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Test plan/scope | A/R | C | C | C | C | I |
| Test case | A | R | C | C | C | I |
| Môi trường/Qdrant/Ollama | I | C | C | I | I | A/R |
| Unit/integration | C | C | A/R | C | I | I |
| System/E2E | A | R | C | C | I | C |
| Eval chất lượng | A | R | C | I | C | I |
| UAT | C | C | I | I | A/R | I |
| Fix defect | I | C | R | R | I | C |
| Test summary/sign-off | A/R | C | C | C | C | I |

---

## 13.0 Nhân sự và đào tạo

| Vai trò | Số lượng | Kỹ năng cần | Đào tạo |
|---|---:|---|---|
| QA Lead/Test Architect | 1 | Test plan, risk, traceability, RAG eval | 2 giờ: kiến trúc + rubric eval |
| QA Engineer | 1 | pytest, Streamlit AppTest, Qdrant, Docker | 2 giờ: môi trường + checklist |
| Dev Backend | 1 | Python, Qdrant, SQLite, OpenAI SDK | 1 giờ: runbook/eval |
| Dev UI | 1 | Streamlit, UI state | 1 giờ: AppTest/UI checklist |
| Product Owner | 0,5 | Nghiệp vụ, tiêu chí chấp nhận | 1 giờ: UAT/eval |
| DevOps/SRE | 0,5 | Docker, Qdrant, Ollama, network | 1 giờ: health/troubleshooting |

**Kiến thức tối thiểu:** phân biệt US-01…US-09 với PRD đầy đủ; hiểu no-auth; biết
cách pull model, recreate collection 768, chạy eval và đọc báo cáo.

---

## 14.0 Lịch trình

> Lịch đề xuất, **có điều kiện**: nếu Ollama/model chưa sẵn sàng, T-04/T-05 dời sang
> ngày kế tiếp; UT/IT vẫn chạy bình thường.

| Ngày | Hoạt động | Kết quả/gate |
|---|---|---|
| 2026-10-26 (D0) | Kick-off, chốt scope, chuẩn bị E3, pull model, fixture | Môi trường sẵn sàng; scope sign-off |
| 2026-10-27 (D1) | UT/IT, smoke app | Gate 1: test tự động + coverage |
| 2026-10-28 (D2) | ST upload/delete/session, bắt đầu chat | Gate 2: luồng P0 không lỗi Critical/High |
| 2026-10-29 (D3) | Chat/source/multi-doc, eval 30 câu, performance baseline | Gate 3: eval report + ngưỡng chất lượng |
| 2026-10-30 (D4) | UAT, regression, test summary | Gate 4: PO sign-off/waiver |

**Milestone bắt buộc:** trước UAT phải có (1) Qdrant healthy, (2) Ollama chat +
embedding hoạt động, (3) ít nhất một PDF `READY`, (4) eval report đọc được.

---

## 15.0 Đánh giá rủi ro

Thang điểm: Likelihood (L) × Impact (I), 1–5; score = L×I. Ưu tiên score ≥ 15.

| ID | Rủi ro | L | I | Score | Giảm thiểu / ứng phó | Owner |
|---|---|---:|---:|---:|---|---|
| R-01 | Câu trả lời bịa/không có căn cứ | 3 | 5 | 15 | Prompt grounding + `NOT_FOUND`; eval out-of-scope; review nguồn | QA/Dev |
| R-02 | Retrieval bỏ sót thông tin đúng | 3 | 4 | 12 | Tune top-k/threshold; eval in-doc; kiểm tra chunk/page | Dev/QA |
| R-03 | Extract PDF sai/không có text | 4 | 3 | 12 | Fixture đa dạng; validate; test scan/no-text; message rõ | Dev |
| R-04 | Qdrant down/dimension mismatch | 3 | 4 | 12 | Health check; banner; runbook recreate 768; test IT | DevOps |
| R-05 | Ollama không chạy/thiếu model/chậm | 4 | 4 | 16 | Preflight; pull trước; hướng dẫn; OpenAI fallback tùy chọn | DevOps/QA |
| R-06 | Đổi model/dimension làm hỏng index | 3 | 4 | 12 | Check dimension; reindex; ghi config trong report | Dev |
| R-07 | Xoá không hết vector/file/chat | 2 | 5 | 10 | Test cascade; delete idempotent; kiểm tra count/file | QA/Dev |
| R-08 | Không có auth, lộ dữ liệu nội bộ | 3 | 5 | 15 | Chỉ localhost/VPN; cảnh báo README; không public | DevOps/PO |
| R-09 | Dữ liệu test chứa PII bị lộ | 2 | 5 | 10 | Chỉ fixture tổng hợp; không log nội dung; kiểm tra repo | QA |
| R-10 | Upload đồng bộ gây timeout/chậm | 3 | 3 | 9 | Giới hạn size/page; progress; test file lớn; ghi baseline | Dev |
| R-11 | Môi trường test khác production | 3 | 3 | 9 | Pin version; Docker; ghi environment; smoke trước test | DevOps |
| R-12 | Scope hiểu nhầm PRD đầy đủ | 3 | 3 | 9 | Traceability; out-of-scope rõ; sign-off | QA/PO |
| R-13 | Filename/Markdown gây XSS/vỡ UI | 2 | 3 | 6 | Escape; test TC-UI-007/TC-SEC-003 | Dev |
| R-14 | Eval dataset không đại diện | 3 | 3 | 9 | Review 30 câu; bổ sung khi cần; ghi version | QA/PO |
| R-15 | Regression do thay đổi prompt/model | 3 | 3 | 9 | Chạy eval lại; so baseline; gate 5% | QA/Dev |

---

## 16.0 Phê duyệt

| Vai trò | Tên | Chữ ký | Ngày | Trạng thái |
|---|---|---|---|---|
| QA Lead |  |  |  | Pending |
| Product Owner |  |  |  | Pending |
| Engineering Lead |  |  |  | Pending |
| DevOps/SRE |  |  |  | Pending |
| Security (tư vấn) |  |  |  | Pending |

> Test plan chỉ có hiệu lực khi QA Lead và Product Owner ký. Mọi thay đổi phạm vi,
> ngưỡng chất lượng hoặc môi trường phải được cập nhật phiên bản tài liệu.

---

## Phụ lục A — Yêu cầu và ma trận truy vết

### A.1 Danh mục yêu cầu in-scope

| Mã | Yêu cầu | Nguồn | Ưu tiên |
|---|---|---|---|
| REQ-F-01 | Upload PDF hợp lệ, lưu file, tạo metadata, chunk, embedding và upsert Qdrant; kết thúc `READY` | US-01, S-07…S-11 | P0 |
| REQ-F-02 | Upload nhiều PDF; xử lý độc lập, một file lỗi không chặn file khác | US-02, S-13 | P0 |
| REQ-F-03 | Validate PDF và từ chối đúng trường hợp: sai định dạng, quá size, quá trang, mã hoá, corrupt, scan/no-text | US-03, S-06/S-14 | P0 |
| REQ-F-04 | Hiển thị danh sách và metadata tài liệu (tên, size, page, ngày, trạng thái) | US-04/US-05, S-12 | P0 |
| REQ-F-05 | Xoá cứng tài liệu: point Qdrant, row SQLite, file PDF, chat history | US-06, S-12 | P0 |
| REQ-F-06 | Chat chỉ khả dụng khi có ít nhất một tài liệu `READY`; empty/error state rõ | US-07, S-18 | P0 |
| REQ-F-07 | Trả lời dựa trên context; trả `NOT_FOUND` khi không đủ căn cứ, không bịa | US-08, S-15/S-17 | P0 |
| REQ-F-08 | Tổng hợp câu trả lời trên nhiều tài liệu khi câu hỏi cần | US-09, S-15 | P1 |
| REQ-F-09 | Hiển thị nguồn: tên file, trang 1-based, snippet; không trùng/bịa | US-09/US-10, S-20/S-21 | P1 |
| REQ-F-10 | Streaming câu trả lời; history trong `st.session_state` | US-07, S-18/S-19 | P1 |
| REQ-F-11 | Chạy eval 30 câu; xuất báo cáo JSON/Markdown có score/latency | S-24, US-12 | P1 |
| REQ-F-12 | Cấu hình qua env; default Ollama `llama3.1`/`nomic-embed-text`/768; hỗ trợ OpenAI-compatible | S-03, README | P0 |
| REQ-F-13 | Map lỗi thành mã/thông báo thân thiện; không crash/lộ stack | S-14, PRD lỗi | P0 |
| REQ-F-14 | Quản lý collection Qdrant: tạo, kiểm tra dimension, upsert/query/delete | S-04/S-05, S-16 | P0 |
| REQ-F-15 | Hiển thị tiến trình/trạng thái trong upload đồng bộ | S-11/S-12 | P2 |
| REQ-NF-01 | Chất lượng RAG: in-doc ≥ 80%, citation ≥ 90%, out-of-scope ≥ 9/10 | PRD MET-002/003 | P0 |
| REQ-NF-02 | Có baseline hiệu năng cho ingest/retrieval/first token | PRD NFR, MVP | P2 |
| REQ-NF-03 | Chịu lỗi dependency: Qdrant/Ollama/timeout/429; retry đúng giới hạn | S-10/S-14 | P1 |
| REQ-NF-04 | Toàn vẹn dữ liệu: không point/row/file mồ côi; delete/upsert idempotent | S-05/S-12 | P0 |
| REQ-NF-05 | Bảo mật cơ bản: không lộ key/nội dung; filename an toàn; cảnh báo no-auth | PRD security, MVP | P0 |
| REQ-NF-06 | Chất lượng mã: test/lint/type pass; coverage ≥ 80% | DoD S-22 | P1 |
| REQ-NF-07 | Di động cấu hình: Python 3.12+, Docker Compose, Ollama/OpenAI | README/S-26 | P1 |
| REQ-NF-08 | Khả dụng: UI tiếng Việt, state rõ, thao tác xoá có xác nhận | US/UIUX | P1 |

### A.2 Ma trận truy vết yêu cầu → test case → bằng chứng

| Yêu cầu | Test case chính | Bằng chứng tự động / thủ công | Trạng thái baseline 2026-10-23 |
|---|---|---|---|
| REQ-F-01 | TC-UPL-001, TC-UPL-002, TC-ING-001 | `tests/test_ingest.py`, `test_pdf.py`; ST pending | Một phần: UT/IT pass; ST chưa chạy |
| REQ-F-02 | TC-UPL-002, TC-UPL-003, TC-ING-004 | `tests/test_ingest.py`; ST pending | Một phần |
| REQ-F-03 | TC-UPL-004…009, TC-PDF-001…003 | `tests/test_pdf.py`, `tests/test_errors.py` | Đạt UT; ST pending |
| REQ-F-04 | TC-UPL-010, TC-DB-001, TC-UI-002/003 | `tests/test_db.py`, `tests/test_ui.py` | Đạt UT/AppTest; ST pending |
| REQ-F-05 | TC-UI-004, TC-ING-005, TC-QD-004, TC-DB-002 | `tests/test_ui.py`, `test_vector_store.py`, `test_db.py` | Đạt UT/IT; ST pending |
| REQ-F-06 | TC-UI-001/002/003, TC-CHAT-006 | `tests/test_ui.py`, `test_ui_state.py` | Đạt UT/AppTest |
| REQ-F-07 | TC-RAG-001/002/003, TC-CHAT-001/003 | `tests/test_rag.py`, `test_sources.py`; eval blocked | Đạt UT; eval chưa chạy |
| REQ-F-08 | TC-RAG-001/004, TC-CHAT-002 | `tests/test_rag.py`, `test_diversity.py`; ST pending | Một phần |
| REQ-F-09 | TC-CHAT-004, TC-PDF-002, TC-UI-007, TC-SEC-003 | `tests/test_sources.py`, `test_ui.py`; ST pending | Một phần |
| REQ-F-10 | TC-LLM-001…004, TC-UI-006, TC-CHAT-001 | `tests/test_llm.py`, `test_ui.py`; ST pending | Một phần |
| REQ-F-11 | TC-EVAL-001…005 | `tests/test_eval_schema.py`; eval report chưa có | Schema đạt; eval blocked |
| REQ-F-12 | TC-EMB-001/002, TC-QD-001, TC-UPL-001, TC-COMP-001 | `tests/test_config.py`, `test_embeddings.py` | Đạt UT/IT; E2E blocked |
| REQ-F-13 | TC-ING-002/003, TC-EMB-003/004, TC-QD-005, TC-LLM-004, TC-CHAT-005, TC-UI-005 | `tests/test_errors.py`, `test_ingest.py`, `test_llm.py` | Đạt UT; ST pending |
| REQ-F-14 | TC-QD-001/002/004, TC-EVAL-004 | `tests/test_vector_store.py`, integration Qdrant | Đạt IT |
| REQ-F-15 | TC-ING-001, TC-UI-008 | `tests/test_ingest.py`; ST pending | Một phần |
| REQ-NF-01 | TC-EVAL-002/003, TC-CHAT-003 | Eval report 30 câu | **Blocked** (Ollama) |
| REQ-NF-02 | TC-NFR-002 | Bảng đo baseline | Chưa chạy |
| REQ-NF-03 | TC-QD-005, TC-LLM-002/003, TC-CHAT-005, TC-UI-005 | `tests/test_llm.py`, `test_errors.py` | Đạt UT; ST pending |
| REQ-NF-04 | TC-DB-002, TC-QD-002/004, TC-ING-002/003/004, TC-NFR-003 | `tests/test_db.py`, `test_vector_store.py`, `test_ingest.py` | Đạt UT/IT |
| REQ-NF-05 | TC-SEC-001/002/003, TC-UI-007 | Checklist + `test_ui.py` | Một phần; ST security pending |
| REQ-NF-06 | TC-NFR-001 | `pytest`, coverage, ruff, mypy | **Đạt** (156 pass, 94%) |
| REQ-NF-07 | TC-COMP-001, TC-DB-003, TC-QD-001 | `docker compose config`, README smoke | Một phần; máy sạch chưa test |
| REQ-NF-08 | TC-UI-001/002/003/006, TC-ACC-001 | AppTest + checklist | Một phần |

### A.3 Độ phủ User Story

| User Story | Phạm vi | Yêu cầu | Test case | Kết luận |
|---|---|---|---|---|
| US-01 | Tải một PDF | REQ-F-01 | TC-UPL-001, TC-ING-001 | Có phủ |
| US-02 | Tải nhiều PDF | REQ-F-02 | TC-UPL-002/003, TC-ING-004 | Có phủ |
| US-03 | Biết file bị từ chối | REQ-F-03 | TC-UPL-004…009 | Có phủ |
| US-04 | Thấy trạng thái | REQ-F-04 | TC-UPL-010, TC-UI-002/003 | Có phủ |
| US-05 | Xem danh sách | REQ-F-04 | TC-UPL-010, TC-UI-003 | Có phủ |
| US-06 | Xoá tài liệu | REQ-F-05 | TC-UI-004, TC-ING-005, TC-QD-004 | Có phủ |
| US-07 | Chat với tài liệu | REQ-F-06/10 | TC-UI-001, TC-CHAT-001/006 | Có phủ |
| US-08 | Trả lời có căn cứ/không bịa | REQ-F-07 | TC-RAG-003, TC-CHAT-001/003 | Có phủ |
| US-09 | Nhiều tài liệu/nguồn | REQ-F-08/09 | TC-CHAT-002/004, TC-RAG-001 | Có phủ |
| US-10 (hỗ trợ) | Xem tên file/trang | REQ-F-09 | TC-CHAT-004 | Chỉ hiển thị, không viewer |
| US-11 (hỗ trợ) | Không tìm thấy | REQ-F-07 | TC-CHAT-003 | Có phủ |
| US-12 (hỗ trợ) | Chất lượng/eval | REQ-F-11/NF-01 | TC-EVAL-001…003 | Có phủ schema; eval blocked |
| US-23 (hỗ trợ) | Xoá dữ liệu | REQ-F-05/NF-04 | TC-UI-004, TC-QD-004 | Có phủ |

> **Kết luận coverage:** 100% yêu cầu **in-scope** (15 functional + 8 non-functional)
> và 9 user story chính có test case. Không tuyên bố 100% cho toàn bộ PRD/SADD đầy đủ;
> các mục ngoài phạm vi được liệt kê ở §5.

---

## Phụ lục B — Baseline kiểm thử tự động

### B.1 Kết quả đã chạy

| Hạng mục | Lệnh / cách kiểm tra | Kết quả |
|---|---|---|
| Unit + integration | `pytest -q` | **156 passed** |
| Coverage | `pytest --cov=app` | **94%** (không tính `app/main.py`, `app/shared`) |
| Lint | `ruff check .` | Pass |
| Format | `ruff format --check app tests` | Pass |
| Type | `mypy app` | Pass |
| Streamlit smoke | Chạy headless, gọi HTTP | **200** |
| Qdrant health | `curl localhost:6333/healthz` | Healthy, v1.20.0 |
| Collection | Kiểm tra `document_chunks` | 768 chiều, 0 point |
| Compose config | `docker compose config` | Hợp lệ |

### B.2 Test suite hiện có

| Nhóm | File tiêu biểu | Nội dung |
|---|---|---|
| Config | `tests/test_config.py` | Default Ollama/768, env override, validation |
| DB | `tests/test_db.py` | Schema, CRUD, status, delete |
| PDF | `tests/test_pdf.py` | Validate/extract/boundary/no-text |
| Chunk | `tests/test_chunking.py` | Size, overlap, page boundary |
| Embedding | `tests/test_embeddings.py` | Batch, dimension, retry |
| Vector store | `tests/test_vector_store.py` | Collection, upsert, query, delete |
| Ingest | `tests/test_ingest.py` | Happy path, rollback, multi-file |
| RAG | `tests/test_rag.py`, `test_sources.py`, `test_diversity.py` | Retrieval, context, nguồn |
| LLM | `tests/test_llm.py` | Stream, retry, empty |
| UI | `tests/test_ui.py`, `test_ui_state.py`, `test_app_smoke.py` | Render, state, delete, smoke |
| Errors | `tests/test_errors.py` | Mapping lỗi, thông báo |
| Eval schema | `tests/test_eval_schema.py` | Dataset/report schema |
| Integration | `tests/integration/test_qdrant.py`, `tests/test_integration_ingest.py` | Qdrant thật, ingest end-to-end |

### B.3 Blocker hiện tại

| Blocker | Ảnh hưởng | Cách xử lý |
|---|---|---|
| Ollama chưa cài/chưa chạy; cổng 11434 đóng | Không chạy được chat/embedding/upload thật/eval | Cài Ollama; `ollama serve`; pull 2 model |
| Chưa có `.env` | Dùng default Ollama; không phải lỗi | Chấp nhận cho baseline; tạo `.env` khi test OpenAI |
| Collection mới 0 point | Chưa có dữ liệu để chat | Upload fixture hoặc chạy eval `--reindex` |
| Chưa chạy eval 30 câu | Chưa có bằng chứng chất lượng | Chạy sau khi Ollama sẵn sàng; lưu report |

> **Không được báo cáo "RAG đạt"** chỉ dựa trên unit test mock. Kết luận chất lượng
> phải đến từ eval với model thật và dữ liệu fixture.

---

## Phụ lục C — Dữ liệu fixture và câu hỏi eval

### C.1 Fixture PDF

| File | Nội dung chính | Dùng cho |
|---|---|---|
| `hop-dong.pdf` | Hợp đồng giữa bên A (Minh Phát) và bên B (Đông Á); giá trị 1.200.000.000 VND; hạn 30/11/2026; thời hạn 12 tháng; bảo hành 24 tháng | Hỏi đáp đơn tài liệu, trích trang |
| `bao-gia.pdf` | Báo giá nhà cung cấp A 450 triệu, B 620 triệu; giao hàng 45/60 ngày; hiệu lực 30 ngày | So sánh, tổng hợp nhiều tài liệu |
| `quy-dinh.pdf` | Mật khẩu tối thiểu 12 ký tự; bật 2FA; lưu log 90 ngày; backup hằng ngày, giữ 30 bản; RTO 4 giờ | Câu hỏi policy, out-of-scope |

> Nội dung trên dùng để đối chiếu đáp án test; không phải tài liệu pháp lý thật.

### C.2 Eval dataset

| Nhóm | Số câu | Ví dụ | Tiêu chí |
|---|---:|---|---|
| In-document | 10 | "Giá trị hợp đồng là bao nhiêu?" | Đúng số/ngày/tên; có nguồn |
| Multi-document | 10 | "So sánh báo giá A và B" | Tổng hợp ≥ 2 file; không bỏ sót |
| Out-of-scope | 10 | "Giá vàng hôm nay?" | `NOT_FOUND`, không bịa |

**Trường bắt buộc trong dataset:** `id`, `question`, `type`, `expected`/`expected_answer`,
`expected_sources` (nếu có). Không trùng ID; type thuộc 3 nhóm trên.

---

## Phụ lục D — Checklist trước khi kết thúc kiểm thử

- [ ] Đã ghi commit hash, Python, Streamlit, Qdrant, Ollama và model.
- [ ] Qdrant healthy; collection đúng 768; không còn collection test.
- [ ] `pytest -q` pass; coverage ≥ 80%; ruff/mypy sạch.
- [ ] Upload 1 PDF → `READY`; file/DB/Qdrant khớp.
- [ ] Upload nhiều PDF; file lỗi không chặn file tốt.
- [ ] Chat có câu trả lời + nguồn đúng; câu ngoài phạm vi → `NOT_FOUND`.
- [ ] Xoá tài liệu: Qdrant/SQLite/file/chat đều sạch.
- [ ] Refresh làm mất chat history đúng thiết kế session.
- [ ] Qdrant down/Ollama down/dimension mismatch có thông báo, không crash.
- [ ] Không lộ API key/nội dung PDF trong log/UI.
- [ ] Eval 30 câu có JSON + Markdown; đạt ngưỡng hoặc có waiver.
- [ ] UAT-01…UAT-06 có biên bản/evidence.
- [ ] Defect Critical/High = 0; waiver được PO duyệt.
- [ ] Test summary và traceability đã cập nhật.

---

## Phụ lục E — Định nghĩa trạng thái test case

| Trạng thái | Ý nghĩa |
|---|---|
| Not Run | Chưa thực hiện |
| Blocked | Không thể chạy do môi trường/dependency |
| Pass | Kết quả đúng expected, có evidence |
| Fail | Kết quả sai expected; đã tạo defect |
| Partial | Một phần pass (ví dụ UT pass, ST chưa chạy) |
| Waived | Không đạt nhưng được PO chấp nhận bằng văn bản |

---

**Hết tài liệu.**  
*Kế hoạch này là baseline; mọi thay đổi phạm vi, model, dimension hoặc ngưỡng chất
lượng phải được cập nhật phiên bản và thông báo cho QA/PO.*






