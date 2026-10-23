# S-26 — README và runbook vận hành

| Thuộc tính | Giá trị |
|---|---|
| Story | Nền tảng (US-01…US-09) |
| Phase | P3 |
| Tầng | DOCS |
| Ước lượng | 0,25d |
| Phụ thuộc | Tất cả task trước |
| Chặn | Demo |
| Owner gợi ý | Full-stack |

## 1. Mục tiêu

Một người mới clone repo có thể chạy app trong **≤ 15 phút**: cài dependency, bật Qdrant, cấu hình model, upload PDF, chat, chạy test. README cũng là runbook xử lý sự cố và ghi rõ giới hạn/bảo mật.

## 2. Phạm vi

**Làm:**

- `README.md` hoàn chỉnh.
- Quickstart 5 lệnh.
- Bảng biến môi trường.
- Ví dụ OpenAI + Ollama.
- Kiến trúc ngắn + luồng.
- Lệnh test/eval.
- Troubleshooting.
- Cảnh báo bảo mật (không auth).
- Giới hạn (scan, history, dedupe, dimension).
- Cấu trúc dữ liệu/backup.

**Không làm:**

- Hướng dẫn deploy production/HTTPS/auth.
- Tài liệu API (không có API công khai).
- Video demo.

## 3. File chính

```text
README.md
```

## 4. Nội dung README

### 4.1 Tiêu đề + mô tả

```markdown
# Chat với tài liệu (PDF + Qdrant)

Ứng dụng một trang: tải PDF lên, hỏi AI về nội dung, xem nguồn.
Không đăng nhập — chỉ dùng localhost hoặc mạng nội bộ tin cậy.
```

### 4.2 Kiến trúc

```text
Streamlit → SQLite (metadata) + local disk (PDF) + Qdrant (vector)
          → OpenAI-compatible API (embedding + chat)
```

### 4.3 Yêu cầu

- Python 3.12+
- Docker + Docker Compose
- API key OpenAI-compatible **hoặc** Ollama local
- RAM/disk gợi ý: 2 GB RAM, 500 MB disk cho demo

### 4.4 Quickstart

```bash
git clone <repo>
cd chat_voi_document

cp .env.example .env
# sửa OPENAI_API_KEY, LLM_MODEL, EMBEDDING_MODEL, EMBEDDING_DIM

docker compose up -d
uv sync                      # hoặc: python -m venv .venv && pip install -e ".[dev]"

uv run streamlit run app/main.py
# mở http://localhost:8501
```

### 4.5 Cấu hình

Bảng đầy đủ từ S-03 §4.1. Nhấn mạnh:

- `EMBEDDING_DIM` phải khớp model.
- Đổi model/chiều → xoá collection + re-index.
- `OPENAI_BASE_URL` cho Ollama: `http://localhost:11434/v1`.
- Không commit `.env`.

### 4.6 Ví dụ Ollama

```bash
ollama pull llama3.1
ollama pull nomic-embed-text
```

```env
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
LLM_MODEL=llama3.1
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIM=768
```

> Nếu đổi từ OpenAI 1536 sang Ollama 768: xoá collection Qdrant cũ trước khi chạy.

### 4.7 Sử dụng

1. Tải PDF ở sidebar.
2. Chờ trạng thái **Sẵn sàng**.
3. Hỏi ở ô chat.
4. Mở **Nguồn** để kiểm tra.
5. Xoá tài liệu khi không cần.

### 4.8 Dữ liệu và backup

```text
data/
├── app.db          # metadata
└── uploads/        # PDF gốc
```

- Backup: copy `data/` + Qdrant volume (`docker run --rm -v ...` hoặc snapshot volume).
- `docker compose down` giữ volume; `down -v` **xoá vector**.
- SQLite WAL: có thể có `app.db-wal`, `app.db-shm`; backup cả 3 hoặc dùng `sqlite3 .backup`.

### 4.9 Test

```bash
pytest -q
pytest -q -m integration      # cần Qdrant
pytest --cov=app
python -m app.eval --reindex  # cần API key
```

### 4.10 Troubleshooting

| Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|
| `Connection refused` Qdrant | Qdrant chưa chạy | `docker compose up -d`, `docker compose ps` |
| `collection ... vector size ...` | Đổi embedding model/dim | Xoá collection cũ, re-index; hoặc đặt đúng `EMBEDDING_DIM` |
| `401 Unauthorized` | Sai/thiếu API key | Kiểm tra `.env`, không có khoảng trắng |
| `429 Rate limit` | Quá nhiều request | Giảm batch/top-k, thử lại, dùng Ollama |
| `PDF_NO_TEXT` | PDF scan/ảnh | Chưa hỗ trợ OCR; dùng PDF có text |
| `PDF_ENCRYPTED` | PDF có mật khẩu | Bỏ mật khẩu rồi tải lại |
| Upload không phản hồi | PDF lớn, xử lý sync | Giảm file/trang; xem terminal |
| `database is locked` | Nhiều thao tác đồng thời | Thử lại; tránh nhiều tab cùng upload |
| Port 8501 bận | App khác đang chạy | `streamlit run ... --server.port 8502` |
| Port 6333 bận | Qdrant khác đang chạy | Đổi mapping/container |
| Chat im lặng | LLM timeout/key | Xem terminal; kiểm tra model |
| Nguồn rỗng | Không hit/ngưỡng cao | Hạ `SCORE_THRESHOLD`, kiểm tra PDF có text |
| Câu trả lời bịa | Retrieval/LLM | Giảm temperature, tăng ngưỡng, kiểm tra prompt |

### 4.11 Bảo mật

> **Không có đăng nhập.** Bất kỳ ai truy cập được cổng 8501 đều có thể upload, đọc, xoá tài liệu.
> Chỉ chạy localhost hoặc sau VPN/reverse proxy có auth. Không expose Internet.
> Không dùng dữ liệu thật/nhạy cảm trong bản demo.

### 4.12 Giới hạn đã biết

- Không OCR PDF scan.
- Lịch sử chat mất khi refresh (session state).
- Upload lại cùng file tạo tài liệu mới (không dedupe).
- Xử lý đồng bộ; PDF lớn làm UI chờ.
- Không có phân quyền/chọn tài liệu theo người dùng.
- Không có source viewer (chỉ tên file + trang + snippet).
- Đổi embedding model cần re-index.
- Không có backup tự động.

## 5. Trường hợp biên

- Người dùng chạy `pip` thay `uv` → README có cả hai.
- Windows → lệnh Docker/Streamlit tương tự; lưu ý đường dẫn `data\`; không cần script shell.
- Không có Docker → README ghi Qdrant Cloud/binary là ngoài phạm vi.
- API key trong `.env` bị commit → `.gitignore` chặn; nhắc rotate nếu lỡ.
- Qdrant volume cũ → hướng dẫn xoá/recreate.
- `data/` quyền ghi → hướng dẫn `chmod`/đổi `DATA_DIR`.
- Model không hỗ trợ tiếng Việt tốt → ghi chú chọn model.

## 6. Tiêu chí xong

- [ ] README có quickstart chạy được trên máy sạch.
- [ ] Bảng env khớp S-03.
- [ ] Có ví dụ OpenAI và Ollama.
- [ ] Có troubleshooting tối thiểu 10 mục.
- [ ] Có cảnh báo không auth rõ ràng.
- [ ] Có lệnh test/eval.
- [ ] Có mô tả backup và `down -v`.
- [ ] Không chứa key thật.

## 7. Test

- Làm theo README trên venv mới trong **≤ 15 phút**.
- Chạy `pytest -q`.
- Upload/chat theo hướng dẫn.
- Cố tình gây lỗi Qdrant để kiểm tra troubleshooting.

## 8. Tham chiếu

- Kế hoạch §11, §12, §13.
- S-01, S-03, S-22, S-24, S-25.
