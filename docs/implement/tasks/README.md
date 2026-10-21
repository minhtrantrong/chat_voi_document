# Danh sách task phát triển — "Chat với tài liệu" MVP

> **Nguồn:** [Implement_plan.md](../Implement_plan.md) (IMP-CVD-001 v0.2, Phần I §4 và Phần II §13–§23) · [SADD.md](../../design/SADD.md) · [User_Stories.md](../../requirements/User_Stories.md)
> **Mục lục này được sinh từ phần đầu của từng file task** — sửa thông tin (sprint, ước lượng, phụ thuộc) ở file task, rồi sinh lại bảng.

## 1. Cách dùng

Mỗi file là **một task giao được cho một developer**, gồm:

| Phần | Nội dung |
|---|---|
| Bảng đầu | Story, sprint, tầng kiến trúc, ước lượng, owner gợi ý, **Phụ thuộc** (phải xong trước), **Chặn** (task chờ task này) |
| Bối cảnh | Vì sao cần, trích yêu cầu/AC/quyết định kiến trúc liên quan |
| Phạm vi | **Làm** / **Không làm** — tránh làm lấn sang task khác |
| Đặc tả | Chữ ký hàm, DTO, SQL, khoá Redis, pseudo-code, quy tắc biên |
| Tiêu chí xong | Checklist nghiệm thu riêng của task |
| Test | Tên file/test cần viết và khẳng định |
| Tham chiếu | SADD, User Stories, quyết định C-xx |

**Trước khi nhận task:** đọc [Implement_plan §13–§14](../Implement_plan.md) (quy ước và 18 quyết định làm rõ C-01…C-18). **Khi đóng task:** đạt tiêu chí riêng của task **và** Definition of Done chung ở Implement_plan §6.

**Mã task:**

| Tiền tố | Ý nghĩa |
|---|---|
| `PLT-xx` | Hạ tầng, CI/CD, vận hành, kiểm thử hệ thống (hạng mục ở Phần I §4 chưa có mã) |
| `F-xx` | Nền tảng code dùng chung (Implement_plan §15) |
| `T-<story>-<n>` | Task theo user story (Implement_plan §16–§22); ví dụ `T-13d-2` là task 2 của US-13d |

**Owner gợi ý** theo vai trò ở Implement_plan §9: Tech Lead, Backend 1 (documents/conversation/feedback/UI), Backend 2 (identity/platform/telemetry/admin), AI/Backend (ingestion/QA/eval), QA/DevOps.

Các **gate phi-code** (G-01…G-06: phê duyệt dữ liệu AI, SSO, giấy phép PyMuPDF, bộ câu hỏi vàng, ngưỡng, hạ tầng) theo dõi ở [Implement_plan §2](../Implement_plan.md); chỉ G-01 có task tài liệu riêng ([T-22-1](T-22-1-data-flow-compliance-doc.md)).

## 2. Tổng hợp theo sprint

| Sprint | Mục tiêu | Số task | Ngày công |
|---|---|---|---|
| S0 | Khởi tạo repo, CI, hạ tầng, shared kernel (M0) | 12 | 11.5d |
| S1 | Dữ liệu, identity, job queue, worker (M1) | 21 | 21.75d |
| S2 | Tải lên, xử lý tài liệu, danh sách (M2) | 29 | 22d |
| S3 | Hỏi đáp, streaming, trích dẫn, eval (M3) — sprint rủi ro cao nhất | 49 | 36.25d |
| S4 | Nguồn, xoá, hội thoại, feedback, P2 nếu còn dung lượng (M4) | 34 | 23d |
| S5 | Bảo mật, tải, vận hành, admin, eval cuối (M5) | 11 | 19d |
| **Tổng** | | **156** | **133.5d** |

Ước lượng là ngày công lý tưởng, đã gồm unit test của task, chưa gồm review/họp. Task P2 (US-17, US-18, 5 ngày công nằm trong S4) chỉ làm khi còn dung lượng. S3 nặng nhất: nên cho Backend 1 làm trước các task UI stream (T-13-6, T-13-7, T-10-4, T-10-5) trên `FakeQaService` từ cuối S2.

## 3. Danh sách task theo sprint

### S0 — Khởi tạo repo, CI, hạ tầng, shared kernel (M0)

| Task | Nội dung | Story | Ước lượng | Owner gợi ý | Phụ thuộc |
|---|---|---|---|---|---|
| [PLT-01](PLT-01-scaffold-repo.md) | Khởi tạo cấu trúc repository và dependency | Nền tảng | 1d | Tech Lead | — |
| [PLT-02](PLT-02-quality-tooling.md) | Công cụ chất lượng: ruff, mypy, import-linter, pre-commit | Nền tảng | 1d | Tech Lead | PLT-01 |
| [PLT-03](PLT-03-ci-pipeline.md) | Pipeline CI | Nền tảng | 1.5d | QA/DevOps | PLT-01, PLT-02, PLT-04 (build image) |
| [PLT-04](PLT-04-docker-compose.md) | Dockerfile một image và Docker Compose local/staging | Nền tảng | 1.5d | QA/DevOps | PLT-01 |
| [PLT-05](PLT-05-settings.md) | Cấu hình môi trường bằng pydantic-settings | Nền tảng | 0.5d | Backend 2 | PLT-01 |
| [PLT-06](PLT-06-ops-health-metrics.md) | Dịch vụ ops: health, readiness và endpoint metrics | Nền tảng | 1d | Backend 2 | PLT-04, PLT-05 |
| [PLT-07](PLT-07-streamlit-shell-layout.md) | Khung Streamlit: điều hướng, bố cục 3 cột, TopBar, cấu hình production | Nền tảng | 1.5d | Backend 1 | PLT-01, F-03 (có thể làm song song, dùng chuỗi tạm) |
| [F-01](F-01-shared-types-ids-clock.md) | Shared kernel: Actor, Role, Page, UUIDv7, Clock | Nền tảng | 0.5d | Tech Lead | PLT-01 |
| [F-02](F-02-errors.md) | Mô hình lỗi: AppError, ErrorCode, lỗi job | Nền tảng | 0.5d | Tech Lead | PLT-01 |
| [F-03](F-03-i18n-strings.md) | Từ điển chuỗi giao diện (i18n) và ánh xạ mã lỗi | Nền tảng | 1d | Backend 1 | F-02 |
| [F-12](F-12-structured-logging.md) | Structured logging JSON và lọc dữ liệu nhạy cảm | Nền tảng | 0.5d | Backend 2 | PLT-01, PLT-05 |
| [T-22-1](T-22-1-data-flow-compliance-doc.md) | Tài liệu luồng dữ liệu gửi cho Bảo mật/Pháp chế (gate G-01) | US-22 | 1d | Tech Lead/Architect | Lựa chọn sơ bộ LLM/Embedding provider (Implement_plan §12 mục 2) |

### S1 — Dữ liệu, identity, job queue, worker (M1)

| Task | Nội dung | Story | Ước lượng | Owner gợi ý | Phụ thuộc |
|---|---|---|---|---|---|
| [PLT-08](PLT-08-schema-migrations.md) | Schema cơ sở dữ liệu và migration Alembic | Nền tảng | 2d | Backend 2 | PLT-04 (role DB), PLT-05 |
| [PLT-09](PLT-09-observability-base.md) | Nền observability: Prometheus, Loki, Grafana, trace ID | Nền tảng | 1.5d | QA/DevOps | PLT-04, PLT-06, F-12 |
| [PLT-12](PLT-12-scheduler.md) | Scheduler: lên lịch job định kỳ trong worker-ingest | Nền tảng | 0.75d | Backend 2 | F-08 |
| [F-04](F-04-config-service.md) | ConfigService: giới hạn nghiệp vụ và feature flag từ `app_config` | Nền tảng | 1.5d | Backend 2 | PLT-08, F-07 |
| [F-05](F-05-audit-service.md) | AuditService: ghi nhật ký kiểm toán trong cùng transaction | Nền tảng | 0.5d | Backend 2 | PLT-08, F-07 |
| [F-06](F-06-telemetry-service.md) | TelemetryService: sự kiện không chứa nội dung | Nền tảng | 1d | Backend 2 | PLT-08, F-07 |
| [F-07](F-07-db-engine-uow.md) | Engine DB, Unit of Work và repository base | Nền tảng | 1.5d | Backend 2 | PLT-05, PLT-08 |
| [F-08](F-08-job-queue.md) | Job queue trên PostgreSQL: enqueue, claim, NOTIFY, reaper | Nền tảng | 3d | Backend 2 | PLT-08, F-07 |
| [F-09](F-09-worker-runtime.md) | Worker runtime: vòng lặp, registry handler, graceful shutdown | Nền tảng | 1d | Backend 2 | F-08, PLT-06 |
| [F-10](F-10-pdf-sandbox.md) | Sandbox subprocess cho mọi thao tác parse/render PDF | Nền tảng | 1.5d | AI/Backend | PLT-01 |
| [F-11](F-11-bootstrap-ui-state.md) | Bootstrap service cho UI và quản lý session_state | Nền tảng | 1d | Backend 1 | F-04…F-08, PLT-07 |
| [T-21-1](T-21-1-oidc-secrets-entrypoint.md) | Sinh `secrets.toml` OIDC lúc khởi động container | US-21 | 0.5d | Backend 2 | PLT-04, PLT-05, gate G-02 (client ID/secret của IdP) |
| [T-21-2](T-21-2-auth-guard-login.md) | AuthGuard "fail closed" và màn hình đăng nhập SCR-01 | US-21 | 0.5d | Backend 2 | T-21-1, PLT-07, F-03, F-11 |
| [T-21-3](T-21-3-identity-resolve-actor.md) | IdentityService: JIT provision người dùng và ánh xạ nhóm → role | US-21 | 1d | Backend 2 | PLT-08, F-01, F-05, F-07, T-21-2 |
| [T-21-4](T-21-4-session-timeout.md) | Thời hạn phiên: idle 8 giờ, tối đa 12 giờ | US-21 | 1d | Backend 2 | T-21-3, Redis client (PLT-04) |
| [T-21-5](T-21-5-forbidden-403.md) | Màn hình 403 "Không có quyền" (SCR-08) | US-21 | 0.25d | Backend 2 | T-21-2, T-21-3, F-03, F-04 (`ACCESS_REQUEST_CONTACT`) |
| [T-21-6](T-21-6-session-expired-draft.md) | Màn hình hết phiên (SCR-10) và giữ nháp câu hỏi | US-21 | 0.75d | Backend 2 | T-21-4; T-07-4 (Composer) cho phần khôi phục |
| [T-21-7](T-21-7-user-menu-logout.md) | Menu người dùng ở TopBar và đăng xuất | US-21 | 0.25d | Backend 2 | PLT-07, T-21-3 |
| [T-21-8](T-21-8-authz-matrix-tests.md) | Authz matrix tự động cho mọi service | US-21 | 1.5d | QA/DevOps + Backend 2 | T-21-3, F-07 |
| [T-22-2](T-22-2-allow-external-ai-guard.md) | Khoá an toàn `ALLOW_EXTERNAL_AI` cho adapter LLM/Embedding | US-22 | 0.25d | AI/Backend | PLT-05 |
| [T-22-3](T-22-3-egress-allowlist.md) | Egress allowlist cho container ứng dụng | US-22 | 0.5d | QA/DevOps (phối hợp IT) | PLT-04, G-06 |

### S2 — Tải lên, xử lý tài liệu, danh sách (M2)

| Task | Nội dung | Story | Ước lượng | Owner gợi ý | Phụ thuộc |
|---|---|---|---|---|---|
| [PLT-10](PLT-10-storage-gc-job.md) | Job `storage.gc`: dọn object mồ côi trong storage | Nền tảng | 0.75d | Backend 1 | T-01-1, F-08, F-09, PLT-12 (lịch chạy) |
| [PLT-11](PLT-11-upload-fuzz-suite.md) | Bộ fuzz test cho upload và ingestion | Nền tảng | 1d | QA/DevOps | T-01-4, T-04-4, F-10 |
| [T-01-1](T-01-1-s3-storage-adapter.md) | Adapter object storage S3/MinIO | US-01 | 1d | Backend 1 | PLT-04, PLT-05 |
| [T-01-2](T-01-2-pdf-inspect.md) | `PdfPort.inspect`: kiểm tra nhanh PDF khi tải lên | US-01 | 1d | AI/Backend | F-10, gate G-03 (chọn PyMuPDF hay pypdfium2) |
| [T-01-3](T-01-3-document-domain.md) | Domain Document: entity, trạng thái, chính sách upload | US-01 | 0.5d | Backend 1 | F-01, F-02 |
| [T-01-4](T-01-4-document-service-upload.md) | `DocumentService.upload`: kiểm tra, lưu, tạo tài liệu + job | US-01 | 1.5d | Backend 1 | T-01-1, T-01-2, T-01-3, F-04, F-05, F-06, F-07, F-08 |
| [T-01-5](T-01-5-upload-name-conflict.md) | Xử lý trùng tên khi tải lên: Thay thế / Giữ cả hai | US-01 | 0.5d | Backend 1 | T-01-4, T-06-1 (`mark_deleting`) |
| [T-01-6](T-01-6-upload-dropzone-ui.md) | UI vùng tải lên (UploadDropzone) và thông báo lỗi theo tệp | US-01 | 1d | Backend 1 | T-01-4, F-03, F-04, F-11, PLT-07 |
| [T-01-7](T-01-7-duplicate-name-dialog.md) | Hộp thoại tệp trùng tên (SCR-07) | US-01 | 0.5d | Backend 1 | T-01-5, T-01-6 |
| [T-02-1](T-02-1-batch-upload-service.md) | Tải lên theo lô: giới hạn số tệp và xử lý song song | US-02 | 0.5d | Backend 1 | T-01-4 |
| [T-02-2](T-02-2-batch-upload-ui.md) | UI kết quả tải lên theo lô | US-02 | 1d | Backend 1 | T-02-1, T-01-6, T-01-7 |
| [T-02-3](T-02-3-batch-upload-tests.md) | Test tích hợp cho tải lên theo lô | US-02 | 0.5d | QA/DevOps | T-02-1, T-03-4 (fixture PDF) |
| [T-03-1](T-03-1-file-error-messages.md) | Bảng thông điệp lỗi tệp đúng nguyên văn AC | US-03 | 0.5d | Backend 1 | F-02, F-03 |
| [T-03-2](T-03-2-detect-no-text-pdf.md) | Phát hiện PDF không có lớp văn bản (scan) trong ingest | US-03 | 0.5d | AI/Backend | T-04-1 |
| [T-03-3](T-03-3-document-error-chip-ui.md) | UI tài liệu lỗi: chip "Lỗi", lý do, Thử lại / Xoá | US-03 | 0.5d | Backend 1 | T-03-1, T-05-3 (DocumentItem), T-04-6 (retry) |
| [T-03-4](T-03-4-pdf-test-fixtures.md) | Bộ PDF mẫu cho test | US-03 | 0.5d | QA/DevOps | PLT-01 |
| [T-04-1](T-04-1-pdf-extract-pages.md) | `PdfPort.extract_pages`: trích văn bản theo trang và block | US-04 | 1d | AI/Backend | F-10, T-01-2 (adapter đã có), T-03-4 |
| [T-04-2](T-04-2-chunker.md) | Chunker: chia văn bản theo token, giữ trang và vị trí | US-04 | 1.5d | AI/Backend | T-04-1 (kiểu `PageText`), F-01 |
| [T-04-3](T-04-3-embedding-adapter-cache.md) | Adapter Embedding, cache theo nội dung và bản giả cho test | US-04 | 1d | AI/Backend | PLT-05, T-22-2, Redis client |
| [T-04-4](T-04-4-ingest-job-handler.md) | Handler `document.ingest`: extract → chunk → embed → index | US-04 | 1.5d | AI/Backend | T-01-1, T-04-1, T-04-2, T-04-3, T-03-2, F-08, F-09 |
| [T-04-5](T-04-5-ingest-reaper-hook.md) | Reaper hook cho ingest: tài liệu ERROR `WORKER_LOST` | US-04 | 0.5d | AI/Backend | F-08 (REAPER_HOOKS), T-04-4 |
| [T-04-6](T-04-6-document-retry.md) | `DocumentService.retry`: xử lý lại tài liệu lỗi | US-04 | 0.5d | Backend 1 | T-01-3, T-05-1 (AccessPolicy), F-05, F-08 |
| [T-04-7](T-04-7-document-status-polling-ui.md) | UI tự cập nhật trạng thái tài liệu (fragment poll) và bật Composer | US-04 | 1d | Backend 1 | T-05-2, T-05-3, F-11 |
| [T-05-1](T-05-1-access-policy.md) | AccessPolicy cho tài liệu | US-05 | 0.5d | Backend 1 | F-01, T-01-3 |
| [T-05-2](T-05-2-document-list-repository.md) | Truy vấn danh sách tài liệu theo quyền, phân trang keyset | US-05 | 0.5d | Backend 1 | T-05-1, F-01 (cursor), F-07 |
| [T-05-3](T-05-3-document-item-ui.md) | UI danh sách tài liệu và DocumentItem | US-05 | 1d | Backend 1 | T-05-2, F-03, PLT-07 |
| [T-05-4](T-05-4-document-authz-tests.md) | Test phân quyền cho danh sách và chi tiết tài liệu | US-05 | 0.5d | QA/DevOps | T-05-2, T-21-8 (khung matrix) |
| [T-06-1](T-06-1-document-mark-deleting.md) | Domain: chuyển tài liệu sang DELETING | US-06 | 0.25d | Backend 1 | T-01-3 |
| [T-24-1](T-24-1-limits-from-config-ui.md) | UI đọc mọi giới hạn từ cấu hình (S2–S3) | US-24 | 0.5d | Backend 1 | F-04, T-01-6, T-07-4 |

### S3 — Hỏi đáp, streaming, trích dẫn, eval (M3) — sprint rủi ro cao nhất

| Task | Nội dung | Story | Ước lượng | Owner gợi ý | Phụ thuộc |
|---|---|---|---|---|---|
| [T-07-1](T-07-1-qa-schemas.md) | DTO và domain của hỏi đáp: AskCommand, AnswerHandle, AnswerDTO | US-07 | 0.25d | AI/Backend | F-01, F-02 |
| [T-07-2](T-07-2-qa-service-ask.md) | `QaService.ask`: kiểm tra điều kiện, tạo message + answer + job | US-07 | 1.5d | AI/Backend | T-07-1, T-07-3, T-07-6, T-13c-2 (`resolve_scope`), T-24-2 (`BudgetService`, có thể stub), F-06, F-08 |
| [T-07-3](T-07-3-redis-guard.md) | RedisGuard: ping, rate limit theo người dùng, idempotency | US-07 | 0.5d | Backend 2 | Redis client (PLT-04/PLT-05) |
| [T-07-4](T-07-4-composer-ui.md) | Composer: ô nhập câu hỏi, trạng thái bật/tắt, DisclaimerBar | US-07 | 1d | Backend 1 | T-07-1, T-04-7 (`docs.has_ready`), F-03, F-11 |
| [T-07-5](T-07-5-submit-flow-ui.md) | Luồng gửi câu hỏi ở UI: hiển thị tức thì và khởi động stream | US-07 | 0.5d | Backend 1 | T-07-2, T-07-4, T-13-6 |
| [T-07-6](T-07-6-lazy-conversation-create.md) | Tạo hội thoại "lười" khi gửi câu hỏi đầu tiên | US-07 | 0.25d | Backend 1 | PLT-08, F-07 |
| [T-08-1](T-08-1-prompt-file-loader.md) | Prompt `qa_answer.v1` và PromptLoader có version | US-08 | 0.5d | AI/Backend | PLT-01 |
| [T-08-2](T-08-2-prompt-builder.md) | PromptBuilder: dựng ngữ cảnh có đánh số nguồn và cắt theo ngân sách token | US-08 | 1d | AI/Backend | T-08-1, T-09-1 (kiểu `RetrievedChunk`), T-04-2 (Tokenizer), T-11-3 (`detect_lang`) |
| [T-08-3](T-08-3-llm-adapter-fake.md) | Adapter LLM streaming (openai-compatible) và FakeLLM | US-08 | 1.5d | AI/Backend | PLT-05, T-22-2 |
| [T-08-4](T-08-4-eval-counter-factual.md) | Bộ eval "phản thực tế" (tài liệu khác kiến thức phổ thông) | US-08 | 0.5d | AI/Backend + BA | T-12-1 (định dạng bộ eval) |
| [T-09-1](T-09-1-retriever.md) | Retriever: tìm vector có lọc quyền/phạm vi, đa dạng theo tài liệu, mở rộng lân cận | US-09 | 1.5d | AI/Backend | T-04-3, T-04-4, T-05-1, F-07 |
| [T-10-1](T-10-1-citation-validator.md) | CitationValidator: tách segment, kiểm tra marker `[S#]` | US-10 | 1.5d | AI/Backend | T-07-1, T-11-3 (câu not-found theo ngôn ngữ) |
| [T-10-2](T-10-2-citation-assembler.md) | CitationAssembler: tạo citation snapshot và quote để highlight | US-10 | 1d | AI/Backend | T-10-1, T-08-2 (`Source`) |
| [T-10-3](T-10-3-strip-markers-stream.md) | Ẩn marker `[S#]` trong lúc stream | US-10 | 0.25d | AI/Backend | T-10-1 (regex `MARKER`) |
| [T-10-4](T-10-4-citation-chip-ui.md) | CitationChip: hiển thị `[Tên tệp, tr. N]` và các trạng thái | US-10 | 1d | Backend 1 | T-07-1 (`CitationDTO`), F-03, F-04 (cờ `source_viewer`) |
| [T-10-5](T-10-5-answer-view-ui.md) | AnswerView: hiển thị câu trả lời hoàn tất theo segment | US-10 | 0.75d | Backend 1 | T-10-4, T-07-1 |
| [T-10-6](T-10-6-citation-tests.md) | Test invariant citation và chỉ số citation precision | US-10 | 0.5d | AI/Backend | T-13-3 (finalize), T-12-3 (chỉ số eval) |
| [T-11-1](T-11-1-not-found-no-hits.md) | NOT_FOUND khi không có chunk đạt ngưỡng (không gọi LLM) | US-11 | 0.25d | AI/Backend | T-09-1, T-13-3 (khung handler + finalize) |
| [T-11-2](T-11-2-not-found-llm-and-invalid.md) | NOT_FOUND khi LLM trả "không tìm thấy" hoặc citation không hợp lệ | US-11 | 0.25d | AI/Backend | T-10-1, T-13-3 |
| [T-11-3](T-11-3-detect-language.md) | Nhận diện ngôn ngữ câu hỏi (vi/en) | US-11 | 0.25d | AI/Backend | — |
| [T-11-4](T-11-4-not-found-message-ui.md) | NotFoundMessage: thẻ "Không tìm thấy" ở giao diện | US-11 | 0.5d | Backend 1 | T-10-5, F-03 |
| [T-12-1](T-12-1-eval-dataset-format.md) | Định dạng bộ câu hỏi vàng và validator schema | US-12 | 0.5d | AI/Backend | — |
| [T-12-2](T-12-2-eval-runner.md) | Eval runner chạy qua đúng luồng production | US-12 | 1.5d | AI/Backend | T-12-1, T-07-2, T-13-3, T-01-4, T-04-4 |
| [T-12-3](T-12-3-eval-metrics.md) | Chỉ số eval tự động | US-12 | 1d | AI/Backend | T-12-2 |
| [T-12-4](T-12-4-eval-human-grading.md) | Chấm tay bởi chuyên gia: xuất và nhập bảng chấm | US-12 | 0.5d | AI/Backend | T-12-2 |
| [T-12-5](T-12-5-eval-gate-ci.md) | Eval gate: so sánh baseline và chặn hồi quy trong CI | US-12 | 1d | AI/Backend + QA/DevOps | T-12-3, PLT-03 |
| [T-12-6](T-12-6-prompt-injection-corpus.md) | Corpus prompt injection | US-12 | 0.5d | AI/Backend | T-12-1, T-12-2 |
| [T-13-1](T-13-1-streaming-spike.md) | Spike: stream token qua Redis + `st.fragment` và nút Dừng | US-13 | 2.5d | Tech Lead | PLT-04, PLT-07 |
| [T-13-2](T-13-2-redis-token-stream.md) | TokenStreamPort trên Redis Streams | US-13 | 0.75d | Backend 2 | T-13-1 (GO), T-07-1 (`StreamEvent`) |
| [T-13-3](T-13-3-answer-generate-handler.md) | Handler `answer.generate`: truy hồi, gọi LLM, stream, finalize | US-13 | 2d | AI/Backend | T-13-2, T-09-1, T-08-2, T-08-3, T-10-1, T-10-2, T-11-3, F-08, F-09 |
| [T-13-4](T-13-4-qa-read-tokens-get-answer.md) | `QaService.read_tokens` và `get_answer` | US-13 | 0.5d | AI/Backend | T-13-2, T-07-1 (biểu thức `deleted` tính động viết luôn trong task này theo đặc tả T-06-4; T-06-4 ở S4 chỉ rà soát mọi nơi đọc citation dùng chung hàm) |
| [T-13-5](T-13-5-qa-cancel.md) | `QaService.cancel`: dừng câu trả lời | US-13 | 0.5d | AI/Backend | T-13-2, T-13-4, F-05, F-06, F-08 |
| [T-13-6](T-13-6-streaming-fragment-ui.md) | UI fragment stream: hiển thị dần, nút Dừng, fallback DB, watchdog | US-13 | 1.5d | Backend 1 | T-13-1 (GO), T-07-1, T-10-3, T-13-4, T-13-5 |
| [T-13-7](T-13-7-answer-variants-ui.md) | Các biến thể AnswerMessage: Đã dừng, Chưa hoàn tất, Lỗi AI, Thử lại | US-13 | 1d | Backend 1 | T-10-5, T-11-4, T-13-6 |
| [T-13-8](T-13-8-answer-reaper-hook.md) | Reaper hook cho `answer.generate`: kết thúc answer khi worker chết | US-13 | 0.5d | AI/Backend | F-08 (REAPER_HOOKS), T-13-2, T-13-3 |
| [T-13-9](T-13-9-qa-metrics.md) | Metric hỏi đáp: first-token, thời gian trả lời, outcome | US-13 | 0.25d | Backend 2 | PLT-06, T-13-3 |
| [T-13b-1](T-13b-1-same-language-answer.md) | Trả lời cùng ngôn ngữ câu hỏi | US-13b | 0.25d | AI/Backend | T-08-1, T-08-2, T-11-3 |
| [T-13b-2](T-13b-2-no-hardcoded-strings.md) | Kiểm tra không có chuỗi giao diện viết cứng | US-13b | 0.75d | Backend 1 | F-03 |
| [T-13b-3](T-13b-3-text-expansion-check.md) | Kiểm tra giãn chữ +30% | US-13b | 0.25d | Backend 1 | F-03, T-13b-2 |
| [T-13b-4](T-13b-4-eval-language.md) | Eval ngôn ngữ trả lời | US-13b | 0.25d | AI/Backend | T-12-1, T-12-3, T-11-3 |
| [T-13c-1](T-13c-1-scope-checkbox-ui.md) | Checkbox chọn phạm vi tài liệu | US-13c | 0.75d | Backend 1 | T-05-3, F-04 (cờ `scope_select`) |
| [T-13c-2](T-13c-2-resolve-scope.md) | `DocumentService.resolve_scope`: kiểm tra phạm vi ở server | US-13c | 0.5d | Backend 1 | T-05-1, T-05-2 |
| [T-13c-3](T-13c-3-scope-tests.md) | Test phạm vi: 100% trích dẫn thuộc tài liệu đã chọn | US-13c | 0.5d | QA/DevOps | T-13c-2, T-09-1, T-13-3 |
| [T-20-1](T-20-1-telemetry-emit-points.md) | Rà soát điểm phát sự kiện telemetry | US-20 | 0.5d | Backend 2 | F-06; các task phát sự kiện |
| [T-20-2](T-20-2-weekly-questions-view.md) | View `v_weekly_questions` | US-20 | 0.25d | Backend 2 | PLT-08, T-07-2 (telemetry có `answer_id`) |
| [T-20-3](T-20-3-weekly-report-cli.md) | CLI báo cáo số câu hỏi theo tuần | US-20 | 0.5d | Backend 2 | T-20-2 |
| [T-20-4](T-20-4-weekly-count-scenario-test.md) | Kịch bản kiểm thử số câu hỏi theo tuần (AC-20.1) | US-20 | 0.75d | QA/DevOps | T-20-1, T-20-2, T-20-3 |
| [T-22-4](T-22-4-no-content-in-logs-test.md) | Test "canary": không có nội dung trong log, telemetry, audit | US-22 | 0.5d | QA/DevOps | F-05, F-06, F-12, T-07-2, T-13-3, T-01-4 |
| [T-24-2](T-24-2-budget-service.md) | BudgetService: ngân sách token AI theo ngày | US-24 | 0.75d | Backend 2 | F-04, Redis client |

### S4 — Nguồn, xoá, hội thoại, feedback, P2 nếu còn dung lượng (M4)

| Task | Nội dung | Story | Ước lượng | Owner gợi ý | Phụ thuộc |
|---|---|---|---|---|---|
| [PLT-13](PLT-13-accessibility-review.md) | Rà soát trợ năng và khả năng giãn chữ của UI | Nền tảng | 1d | QA/DevOps + Backend 1 | Các UI task của S2–S4 đã xong |
| [T-06-2](T-06-2-document-service-delete.md) | `DocumentService.delete`: xoá mềm, audit, tạo job purge | US-06 | 0.75d | Backend 1 | T-06-1, T-05-1, F-05, F-06, F-08 |
| [T-06-3](T-06-3-purge-job-handler.md) | Handler `document.purge`: xoá vector, object và đánh dấu citation | US-06 | 1d | Backend 1 | T-06-2, T-01-1, F-07 (`advisory_xact_lock`), F-08, F-09 |
| [T-06-4](T-06-4-citation-deleted-computed.md) | Trạng thái "đã xoá" của citation tính tại lúc đọc | US-06 | 0.25d | Backend 1 | T-13-4 |
| [T-06-5](T-06-5-delete-confirm-dialog.md) | Hộp thoại xác nhận xoá (SCR-06) và xử lý sau khi xoá | US-06 | 0.75d | Backend 1 | T-06-2, T-05-3, T-13d-3 |
| [T-06-6](T-06-6-delete-effect-tests.md) | Test hiệu lực xoá với hỏi đáp (AC-06.2) | US-06 | 0.5d | QA/DevOps | T-06-2, T-06-3, T-13-3 |
| [T-13d-1](T-13d-1-pdf-render-page.md) | `PdfPort.render_page`: render trang PNG có highlight | US-13d | 1d | AI/Backend | F-10 (SandboxPool), T-01-2 |
| [T-13d-2](T-13d-2-document-service-render-page.md) | `DocumentService.render_page`: kiểm tra quyền và cache | US-13d | 1d | Backend 1 | T-13d-1, T-05-1, T-01-1, F-05 |
| [T-13d-3](T-13d-3-source-panel-ui.md) | Khung Nguồn (SourcePanel): xem trang, điều hướng, đóng | US-13d | 1d | Backend 1 | T-13d-2, T-10-4, PLT-07 |
| [T-13d-4](T-13d-4-citation-click-telemetry-audit.md) | Telemetry `citation_clicked` và audit khi ADMIN xem tài liệu người khác | US-13d | 0.25d | Backend 1 | T-13d-2, F-05, F-06 |
| [T-13d-5](T-13d-5-source-viewer-e2e.md) | E2E khung Nguồn và chip tài liệu đã xoá | US-13d | 0.5d | QA/DevOps | T-13d-3, T-06-5 |
| [T-14-1](T-14-1-recent-turns-history.md) | Lấy lịch sử gần nhất để đưa vào prompt | US-14 | 0.5d | Backend 1 | T-07-6, T-04-2 (Tokenizer) |
| [T-14-2](T-14-2-followup-retrieval-query.md) | Câu truy vấn retrieval cho câu hỏi tiếp theo (follow-up) | US-14 | 1d | AI/Backend | T-14-1, T-08-1, T-08-3, F-04 (cờ `query_rewrite`) |
| [T-14-3](T-14-3-eval-followup.md) | Eval hỏi tiếp: 10 kịch bản, đạt ≥ 8/10 | US-14 | 1d | AI/Backend + BA | T-12-1, T-12-2, T-14-2 |
| [T-15-1](T-15-1-conversation-service-list-get.md) | ConversationService: danh sách và nội dung hội thoại | US-15 | 1d | Backend 1 | T-07-6, T-06-4, T-13-4 |
| [T-15-2](T-15-2-history-dialog-ui.md) | Ngăn "Lịch sử hội thoại" (SCR-09) | US-15 | 1d | Backend 1 | T-15-1, T-10-5, T-13-6 |
| [T-15-3](T-15-3-retention-sweep-job.md) | Job `retention.sweep`: xoá dữ liệu quá hạn lưu trữ | US-15 | 0.75d | Backend 2 | F-08, F-09, PLT-12, F-04 |
| [T-15-4](T-15-4-history-tests.md) | Test lịch sử qua phiên mới và cách ly người dùng | US-15 | 0.5d | QA/DevOps | T-15-1, T-15-2 |
| [T-16-1](T-16-1-new-conversation-button.md) | Nút "＋ Hội thoại mới" ở TopBar | US-16 | 0.5d | Backend 1 | PLT-07, F-11 (`reset_chat_state`), T-07-6 |
| [T-16-2](T-16-2-new-conversation-context-test.md) | Test: hội thoại mới không mang ngữ cảnh cũ | US-16 | 0.5d | QA/DevOps | T-16-1, T-14-1, T-08-3 (FakeLLM ghi `last_messages`) |
| [T-17-1](T-17-1-qa-summarize-service.md) | `QaService.summarize`: yêu cầu tóm tắt một tài liệu (P2) | US-17 | 0.5d | AI/Backend | T-07-2, T-05-1, F-04 |
| [T-17-2](T-17-2-summarize-worker-mode.md) | Chế độ `summarize` trong worker trả lời (P2) | US-17 | 1d | AI/Backend | T-17-1, T-13-3, T-10-1 |
| [T-17-3](T-17-3-summarize-menu-ui.md) | Mục "Tóm tắt" trong menu ⋯ của tài liệu (P2) | US-17 | 0.25d | Backend 1 | T-17-1, T-05-3, T-13-6 |
| [T-17-4](T-17-4-summarize-expert-eval.md) | Chuyên gia chấm 5 bản tóm tắt mẫu (P2) (S4–S5) | US-17 | 0.5d | AI/Backend + chuyên gia nghiệp vụ | T-17-2, T-12-4 (công cụ chấm) |
| [T-18-1](T-18-1-suggestions-table.md) | Bảng `document_suggestions` (P2) | US-18 | 0.25d | AI/Backend | PLT-08 |
| [T-18-2](T-18-2-suggest-job.md) | Job `document.suggest`: sinh và kiểm tra câu hỏi gợi ý (P2) | US-18 | 1.5d | AI/Backend | T-18-1, T-04-4, T-09-1, T-08-3 |
| [T-18-3](T-18-3-suggested-questions-ui.md) | Chip gợi ý câu hỏi ở SCR-03 (P2) | US-18 | 0.5d | Backend 1 | T-18-2, T-07-4, T-07-5 |
| [T-18-4](T-18-4-suggestions-eval.md) | Kiểm chứng gợi ý trả lời được có trích dẫn (P2) (S4–S5) | US-18 | 0.5d | AI/Backend | T-18-2, T-12-2 |
| [T-19-1](T-19-1-feedback-service.md) | FeedbackService.upsert | US-19 | 0.5d | Backend 1 | T-13-4 (kiểm tra sở hữu answer), F-06 |
| [T-19-2](T-19-2-feedback-bar-ui.md) | FeedbackBar 👍/👎 và ô lý do | US-19 | 1d | Backend 1 | T-19-1, T-10-5, F-04 (cờ `feedback`) |
| [T-19-3](T-19-3-feedback-silent-retry.md) | Ghi feedback lạc quan và thử lại ngầm | US-19 | 0.5d | Backend 1 | T-19-2 |
| [T-23-1](T-23-1-integrity-check-job.md) | Job `integrity.check` hằng ngày | US-23 | 0.75d | Backend 2 | F-08, F-09, PLT-12 (lịch), PLT-06 (metric) |
| [T-23-2](T-23-2-delete-ui-latency-test.md) | E2E: tài liệu biến khỏi UI ≤ 1 s sau khi xoá | US-23 | 0.25d | QA/DevOps | T-06-5 |
| [T-23-3](T-23-3-old-conversation-deleted-doc.md) | Hội thoại cũ sau khi xoá tài liệu | US-23 | 0.25d | QA/DevOps | T-06-4, T-10-4, T-15-1 |

### S5 — Bảo mật, tải, vận hành, admin, eval cuối (M5)

| Task | Nội dung | Story | Ước lượng | Owner gợi ý | Phụ thuộc |
|---|---|---|---|---|---|
| [PLT-14](PLT-14-security-testing.md) | Kiểm thử bảo mật trước release | Nền tảng | 2d | QA/DevOps + Tech Lead | T-21-8 (authz matrix), PLT-11 (fuzz), T-12-6 (prompt injection), T-22-3, T-22-4 |
| [PLT-15](PLT-15-chaos-resilience.md) | Kiểm thử chịu lỗi (chaos) cho worker, Redis, LLM | Nền tảng | 1.5d | QA/DevOps | T-13-3, T-13-8, T-04-5, F-08 |
| [PLT-16](PLT-16-eval-tuning-final-gate.md) | Tinh chỉnh RAG và chốt eval gate phát hành | Nền tảng | 3d | AI/Backend | T-12-1…T-12-6, G-04 (bộ câu hỏi thật), G-05 (ngưỡng) |
| [PLT-17](PLT-17-dashboards-alerts-runbooks.md) | Dashboard, alert và runbook vận hành | Nền tảng | 2d | QA/DevOps | PLT-09, các metric ở PLT-06 đã được ghi từ code |
| [PLT-18](PLT-18-backup-restore.md) | Backup, restore và diễn tập khôi phục | Nền tảng | 1.5d | QA/DevOps | PLT-04 |
| [PLT-19](PLT-19-production-deploy.md) | Triển khai staging/production: blue/green và rollback | Nền tảng | 2d | QA/DevOps | PLT-03, PLT-04, PLT-06 |
| [PLT-20](PLT-20-handover-docs.md) | Tài liệu bàn giao vận hành và người dùng | Nền tảng | 1.5d | Tech Lead (điều phối), mỗi owner module viết phần của mình | PLT-17, PLT-18, PLT-19 |
| [T-09-2](T-09-2-retrieval-benchmark.md) | Benchmark truy hồi ở quy mô 1.000 tài liệu | US-09 | 0.5d | AI/Backend | T-09-1, staging có tài nguyên gần production |
| [T-24-3](T-24-3-admin-page.md) | Trang Quản trị: cấu hình, feature flag, audit, job DEAD | US-24 | 2d | Backend 2 | F-04, F-05, F-08, PLT-07 |
| [T-24-4](T-24-4-load-harness.md) | Load harness cho hỏi đáp và tải lên | US-24 | 2d | QA/DevOps | T-07-2, T-13-3, T-13-2, T-01-4, T-09-2 (seed dữ liệu) |
| [T-24-5](T-24-5-load-test-run.md) | Chạy kiểm thử tải và báo cáo SLO | US-24 | 1d | QA/DevOps | T-24-4, T-09-2, PLT-17 (dashboard để quan sát) |

## 4. Tra cứu theo user story

| Story | Nội dung | Task |
|---|---|---|
| Nền tảng | Nền tảng (PLT, F) | [PLT-01](PLT-01-scaffold-repo.md), [PLT-02](PLT-02-quality-tooling.md), [PLT-03](PLT-03-ci-pipeline.md), [PLT-04](PLT-04-docker-compose.md), [PLT-05](PLT-05-settings.md), [PLT-06](PLT-06-ops-health-metrics.md), [PLT-07](PLT-07-streamlit-shell-layout.md), [PLT-08](PLT-08-schema-migrations.md), [PLT-09](PLT-09-observability-base.md), [PLT-10](PLT-10-storage-gc-job.md), [PLT-11](PLT-11-upload-fuzz-suite.md), [PLT-12](PLT-12-scheduler.md), [PLT-13](PLT-13-accessibility-review.md), [PLT-14](PLT-14-security-testing.md), [PLT-15](PLT-15-chaos-resilience.md), [PLT-16](PLT-16-eval-tuning-final-gate.md), [PLT-17](PLT-17-dashboards-alerts-runbooks.md), [PLT-18](PLT-18-backup-restore.md), [PLT-19](PLT-19-production-deploy.md), [PLT-20](PLT-20-handover-docs.md), [F-01](F-01-shared-types-ids-clock.md), [F-02](F-02-errors.md), [F-03](F-03-i18n-strings.md), [F-04](F-04-config-service.md), [F-05](F-05-audit-service.md), [F-06](F-06-telemetry-service.md), [F-07](F-07-db-engine-uow.md), [F-08](F-08-job-queue.md), [F-09](F-09-worker-runtime.md), [F-10](F-10-pdf-sandbox.md), [F-11](F-11-bootstrap-ui-state.md), [F-12](F-12-structured-logging.md) |
| US-01 | Tải một tệp PDF lên | [T-01-1](T-01-1-s3-storage-adapter.md), [T-01-2](T-01-2-pdf-inspect.md), [T-01-3](T-01-3-document-domain.md), [T-01-4](T-01-4-document-service-upload.md), [T-01-5](T-01-5-upload-name-conflict.md), [T-01-6](T-01-6-upload-dropzone-ui.md), [T-01-7](T-01-7-duplicate-name-dialog.md) |
| US-02 | Tải lên nhiều PDF | [T-02-1](T-02-1-batch-upload-service.md), [T-02-2](T-02-2-batch-upload-ui.md), [T-02-3](T-02-3-batch-upload-tests.md) |
| US-03 | Lý do tệp bị từ chối | [T-03-1](T-03-1-file-error-messages.md), [T-03-2](T-03-2-detect-no-text-pdf.md), [T-03-3](T-03-3-document-error-chip-ui.md), [T-03-4](T-03-4-pdf-test-fixtures.md) |
| US-04 | Trạng thái tài liệu | [T-04-1](T-04-1-pdf-extract-pages.md), [T-04-2](T-04-2-chunker.md), [T-04-3](T-04-3-embedding-adapter-cache.md), [T-04-4](T-04-4-ingest-job-handler.md), [T-04-5](T-04-5-ingest-reaper-hook.md), [T-04-6](T-04-6-document-retry.md), [T-04-7](T-04-7-document-status-polling-ui.md) |
| US-05 | Danh sách theo quyền | [T-05-1](T-05-1-access-policy.md), [T-05-2](T-05-2-document-list-repository.md), [T-05-3](T-05-3-document-item-ui.md), [T-05-4](T-05-4-document-authz-tests.md) |
| US-06 | Xoá tài liệu | [T-06-1](T-06-1-document-mark-deleting.md), [T-06-2](T-06-2-document-service-delete.md), [T-06-3](T-06-3-purge-job-handler.md), [T-06-4](T-06-4-citation-deleted-computed.md), [T-06-5](T-06-5-delete-confirm-dialog.md), [T-06-6](T-06-6-delete-effect-tests.md) |
| US-07 | Hỏi bằng câu tự nhiên | [T-07-1](T-07-1-qa-schemas.md), [T-07-2](T-07-2-qa-service-ask.md), [T-07-3](T-07-3-redis-guard.md), [T-07-4](T-07-4-composer-ui.md), [T-07-5](T-07-5-submit-flow-ui.md), [T-07-6](T-07-6-lazy-conversation-create.md) |
| US-08 | Chỉ dựa trên tài liệu | [T-08-1](T-08-1-prompt-file-loader.md), [T-08-2](T-08-2-prompt-builder.md), [T-08-3](T-08-3-llm-adapter-fake.md), [T-08-4](T-08-4-eval-counter-factual.md) |
| US-09 | Tổng hợp nhiều tài liệu | [T-09-1](T-09-1-retriever.md), [T-09-2](T-09-2-retrieval-benchmark.md) |
| US-10 | Trích dẫn tên + trang | [T-10-1](T-10-1-citation-validator.md), [T-10-2](T-10-2-citation-assembler.md), [T-10-3](T-10-3-strip-markers-stream.md), [T-10-4](T-10-4-citation-chip-ui.md), [T-10-5](T-10-5-answer-view-ui.md), [T-10-6](T-10-6-citation-tests.md) |
| US-11 | Không tìm thấy | [T-11-1](T-11-1-not-found-no-hits.md), [T-11-2](T-11-2-not-found-llm-and-invalid.md), [T-11-3](T-11-3-detect-language.md), [T-11-4](T-11-4-not-found-message-ui.md) |
| US-12 | Chất lượng cam kết (eval) | [T-12-1](T-12-1-eval-dataset-format.md), [T-12-2](T-12-2-eval-runner.md), [T-12-3](T-12-3-eval-metrics.md), [T-12-4](T-12-4-eval-human-grading.md), [T-12-5](T-12-5-eval-gate-ci.md), [T-12-6](T-12-6-prompt-injection-corpus.md) |
| US-13 | Trả lời nhanh, streaming, Dừng | [T-13-1](T-13-1-streaming-spike.md), [T-13-2](T-13-2-redis-token-stream.md), [T-13-3](T-13-3-answer-generate-handler.md), [T-13-4](T-13-4-qa-read-tokens-get-answer.md), [T-13-5](T-13-5-qa-cancel.md), [T-13-6](T-13-6-streaming-fragment-ui.md), [T-13-7](T-13-7-answer-variants-ui.md), [T-13-8](T-13-8-answer-reaper-hook.md), [T-13-9](T-13-9-qa-metrics.md) |
| US-13b | Ngôn ngữ làm việc | [T-13b-1](T-13b-1-same-language-answer.md), [T-13b-2](T-13b-2-no-hardcoded-strings.md), [T-13b-3](T-13b-3-text-expansion-check.md), [T-13b-4](T-13b-4-eval-language.md) |
| US-13c | Giới hạn phạm vi | [T-13c-1](T-13c-1-scope-checkbox-ui.md), [T-13c-2](T-13c-2-resolve-scope.md), [T-13c-3](T-13c-3-scope-tests.md) |
| US-13d | Mở tài liệu gốc đúng trang | [T-13d-1](T-13d-1-pdf-render-page.md), [T-13d-2](T-13d-2-document-service-render-page.md), [T-13d-3](T-13d-3-source-panel-ui.md), [T-13d-4](T-13d-4-citation-click-telemetry-audit.md), [T-13d-5](T-13d-5-source-viewer-e2e.md) |
| US-14 | Hỏi tiếp | [T-14-1](T-14-1-recent-turns-history.md), [T-14-2](T-14-2-followup-retrieval-query.md), [T-14-3](T-14-3-eval-followup.md) |
| US-15 | Lịch sử hội thoại | [T-15-1](T-15-1-conversation-service-list-get.md), [T-15-2](T-15-2-history-dialog-ui.md), [T-15-3](T-15-3-retention-sweep-job.md), [T-15-4](T-15-4-history-tests.md) |
| US-16 | Hội thoại mới | [T-16-1](T-16-1-new-conversation-button.md), [T-16-2](T-16-2-new-conversation-context-test.md) |
| US-17 | Tóm tắt (P2) | [T-17-1](T-17-1-qa-summarize-service.md), [T-17-2](T-17-2-summarize-worker-mode.md), [T-17-3](T-17-3-summarize-menu-ui.md), [T-17-4](T-17-4-summarize-expert-eval.md) |
| US-18 | Gợi ý câu hỏi (P2) | [T-18-1](T-18-1-suggestions-table.md), [T-18-2](T-18-2-suggest-job.md), [T-18-3](T-18-3-suggested-questions-ui.md), [T-18-4](T-18-4-suggestions-eval.md) |
| US-19 | Đánh giá câu trả lời | [T-19-1](T-19-1-feedback-service.md), [T-19-2](T-19-2-feedback-bar-ui.md), [T-19-3](T-19-3-feedback-silent-retry.md) |
| US-20 | Số câu hỏi/người/tuần | [T-20-1](T-20-1-telemetry-emit-points.md), [T-20-2](T-20-2-weekly-questions-view.md), [T-20-3](T-20-3-weekly-report-cli.md), [T-20-4](T-20-4-weekly-count-scenario-test.md) |
| US-21 | Xác thực, phân quyền | [T-21-1](T-21-1-oidc-secrets-entrypoint.md), [T-21-2](T-21-2-auth-guard-login.md), [T-21-3](T-21-3-identity-resolve-actor.md), [T-21-4](T-21-4-session-timeout.md), [T-21-5](T-21-5-forbidden-403.md), [T-21-6](T-21-6-session-expired-draft.md), [T-21-7](T-21-7-user-menu-logout.md), [T-21-8](T-21-8-authz-matrix-tests.md) |
| US-22 | Tuân thủ dữ liệu AI | [T-22-1](T-22-1-data-flow-compliance-doc.md), [T-22-2](T-22-2-allow-external-ai-guard.md), [T-22-3](T-22-3-egress-allowlist.md), [T-22-4](T-22-4-no-content-in-logs-test.md) |
| US-23 | Dữ liệu xoá không còn dùng | [T-23-1](T-23-1-integrity-check-job.md), [T-23-2](T-23-2-delete-ui-latency-test.md), [T-23-3](T-23-3-old-conversation-deleted-doc.md) |
| US-24 | Giới hạn vận hành | [T-24-1](T-24-1-limits-from-config-ui.md), [T-24-2](T-24-2-budget-service.md), [T-24-3](T-24-3-admin-page.md), [T-24-4](T-24-4-load-harness.md), [T-24-5](T-24-5-load-test-run.md) |

## 5. Ghi chú nhất quán với Implement_plan

- Mã `T-xx-n` và `F-xx` giữ nguyên như Implement_plan Phần II; mã `PLT-xx` là mới, ánh xạ tới các mục của Phần I §4 (ví dụ PLT-08 = S1 mục 1.1, PLT-14 = S5 mục 5.3).
- T-06-1 chuyển từ S4 sang **S2** vì T-01-5 (Thay thế tệp trùng tên) cần `mark_deleting`.
- T-13-4 tự viết biểu thức `deleted` tính động cho citation (đặc tả ở T-06-4) để không phụ thuộc vòng tròn với T-06-4.
- Bổ sung so với Phần II: `UnitOfWork.after_commit` (F-07), `Job.last_error` (F-08), sửa DDL `documents.updated_at` (PLT-08), role DB `retention` cho xoá audit (T-15-3), cờ `RATE_LIMIT_EXEMPT_SUBJECTS` cho eval/load (T-12-2, T-24-4).
- Khi đổi phạm vi một task, cập nhật file task trước, rồi Implement_plan nếu ảnh hưởng mốc hoặc ước lượng.
