# Chat với tài liệu (PDF + Qdrant)

Ứng dụng một trang: tải PDF lên, hỏi AI về nội dung, xem nguồn.
**Không có đăng nhập** — chỉ dùng localhost hoặc mạng nội bộ tin cậy.

## Kiến trúc

```text
Streamlit (1 trang)
├── SQLite          → metadata tài liệu
├── Local disk      → PDF gốc (data/uploads/)
├── Qdrant          → vector + payload chunk
└── LM Studio (mặc định) / Ollama / API OpenAI-compatible → embedding + chat
```

## Yêu cầu

- Python 3.12+
- Qdrant v1.20.0 chạy như system service (binary từ https://github.com/qdrant/qdrant/releases)
- **LM Studio local (mặc định)**, Ollama, hoặc API key OpenAI-compatible
- Tài nguyên: `qwen3-1.7b` + `nomic-embed-text` cần khoảng 4 GB RAM và 5–6 GB disk;
  nếu dùng API cloud chỉ cần khoảng 2 GB RAM, 500 MB disk

## Quickstart

```bash
git clone <repo>
cd chat_voi_document

# 1. LM Studio (mặc định): tải model qwen/qwen3-1.7b và
#    text-embedding-nomic-embed-text-v1.5, rồi bật server
lms get qwen/qwen3-1.7b
lms get nomic-ai/nomic-embed-text-v1.5
lms server start   # mặc định cổng 1234 (hoặc tab Developer → Start Server)

# 2. Tạo môi trường (chọn một)
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
# hoặc: uv sync --extra dev

# 3. Cấu hình (mặc định đã là LM Studio; chỉ sửa nếu cần)
cp .env.example .env

# 4. Qdrant: cài binary v1.20.0 và chạy như system service
#    (Linux: systemd unit; Windows: NSSM/Task Scheduler), lưu dữ liệu ở thư mục riêng
curl -f http://localhost:6333/healthz

# 5. Chạy app
streamlit run app/main.py
# mở http://localhost:8501
```

## Cấu hình

Các biến chính trong `.env` (xem đầy đủ ở `.env.example`):

| Biến | Mặc định | Ghi chú |
|---|---|---|
| `QDRANT_URL` | `http://localhost:6333` | |
| `QDRANT_COLLECTION` | `document_chunks` | |
| `OPENAI_BASE_URL` | `http://localhost:1234/v1` | LM Studio mặc định; đổi sang Ollama/OpenAI/vLLM nếu cần |
| `OPENAI_API_KEY` | `lm-studio` | LM Studio không cần key thật; dùng giá trị giả này |
| `LLM_MODEL` | `qwen/qwen3-1.7b` | Phải khớp identifier trong LM Studio |
| `EMBEDDING_MODEL` | `text-embedding-nomic-embed-text-v1.5` | Phải khớp identifier trong LM Studio |
| `EMBEDDING_DIM` | `768` | **phải khớp model** |
| `MAX_UPLOAD_MB` | `25` | |
| `MAX_PAGES` | `400` | |
| `TOP_K` | `8` | |
| `SCORE_THRESHOLD` | `0.25` | |
| `DATA_DIR` | `./data` | SQLite + PDF gốc |

> Đổi embedding model/chiều vector → xoá collection Qdrant cũ và re-index toàn bộ PDF.

### Mặc định: LM Studio

Trong LM Studio: tải một model chat và một model embedding, vào tab **Developer**
→ **Start Server** (cổng `1234`). Có thể bật *Just-in-Time model loading* để
server tự nạp model khi có request.

```env
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio
LLM_MODEL=qwen/qwen3-1.7b
EMBEDDING_MODEL=text-embedding-nomic-embed-text-v1.5
EMBEDDING_DIM=768
```

LM Studio không cần API key thật; giá trị `lm-studio` chỉ để thỏa mãn client
OpenAI-compatible. `LLM_MODEL`/`EMBEDDING_MODEL` phải đúng identifier hiển thị
trong LM Studio (xem `curl http://localhost:1234/v1/models`). Chọn model
chat/embedding hỗ trợ tiếng Việt tốt nếu tài liệu chủ yếu là tiếng Việt.

### Tuỳ chọn: Ollama

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

### Tuỳ chọn: OpenAI

```env
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536
```

Nếu đổi model/chiều vector (ví dụ LM Studio 768 sang OpenAI 1536), xoá collection
Qdrant cũ trước khi chạy và re-index toàn bộ PDF.

## Sử dụng

1. Tải PDF ở sidebar.
2. Chờ trạng thái **Sẵn sàng**.
3. Hỏi ở ô chat.
4. Mở **Nguồn** để kiểm tra tên tệp + trang.
5. Bấm **Xoá** khi không cần; lịch sử chat trong phiên cũng được xoá.

## Dữ liệu và backup

```text
data/
├── app.db          # metadata
└── uploads/        # PDF gốc
```

- Backup: copy `data/` + thư mục storage của Qdrant (dừng service trước khi copy).
- Xoá thư mục storage của Qdrant sẽ **xoá vector** — cẩn thận.
- SQLite WAL có thể tạo `app.db-wal`, `app.db-shm`; backup cả bộ hoặc dùng `sqlite3 .backup`.

## Test

```bash
pytest -q                         # unit + integration (integration tự skip nếu Qdrant tắt)
pytest -q -m "not integration"    # chỉ unit test
pytest -q -m integration          # cần Qdrant
pytest --cov=app                  # coverage (bỏ qua main.py/shared cũ)

# Eval: tạo PDF mẫu rồi nạp + chấm 30 câu
.venv/bin/python tests/eval/generate_fixtures.py
python -m app.eval --reindex --out eval_report  # cần LM Studio/API + Qdrant
```

## Troubleshooting

| Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|
| `Connection refused` Qdrant | Qdrant chưa chạy | Khởi động service Qdrant (`systemctl status qdrant` hoặc tương đương) |
| `Connection refused` cổng `1234` | LM Studio server chưa chạy | Tab Developer → Start Server, hoặc `lms server start` |
| `model ... not found` | Chưa tải/nạp model hoặc sai identifier | Kiểm tra `curl http://localhost:1234/v1/models`, chỉnh `LLM_MODEL`/`EMBEDDING_MODEL` |
| `Connection refused` cổng `11434` | (Nếu dùng Ollama) Ollama chưa chạy | Chạy `ollama serve` |
| `collection ... vector size ...` | Đổi model/dim | Xoá collection cũ, re-index; hoặc đặt đúng `EMBEDDING_DIM` |
| `401 Unauthorized` | Sai/thiếu API key | Kiểm tra `.env`, không có khoảng trắng |
| `429 Rate limit` | Quá nhiều request | Giảm batch/top-k, thử lại, dùng LM Studio/Ollama local |
| `PDF_NO_TEXT` | PDF scan/ảnh | Chưa hỗ trợ OCR; dùng PDF có text |
| `PDF_ENCRYPTED` | PDF có mật khẩu | Bỏ mật khẩu rồi tải lại |
| Upload lâu | Xử lý đồng bộ | Giảm file/trang; xem terminal |
| `database is locked` | Nhiều thao tác đồng thời | Thử lại; tránh nhiều tab cùng upload |
| Port 8501 bận | App khác đang chạy | `streamlit run ... --server.port 8502` |
| Port 6333 bận | Qdrant khác đang chạy | Đổi cổng trong cấu hình Qdrant và `QDRANT_URL` |
| Chat im lặng | LLM timeout/key | Xem terminal; kiểm tra model |
| Câu trả lời bịa | Model yếu/không theo prompt | Đổi model; giảm `TOP_K`; kiểm tra nguồn |
| Nguồn rỗng | Không hit/ngưỡng cao | Hạ `SCORE_THRESHOLD`, kiểm tra PDF có text |

## Bảo mật

> **Không có đăng nhập.** Bất kỳ ai truy cập được cổng 8501 đều có thể upload, đọc, xoá tài liệu.
> Chỉ chạy localhost hoặc sau VPN/reverse proxy có auth. Không expose Internet.
> Không dùng dữ liệu thật/nhạy cảm trong bản demo.

## Giới hạn đã biết

- Không OCR PDF scan.
- Lịch sử chat mất khi refresh (session state).
- Upload lại cùng file tạo tài liệu mới (không dedupe).
- Xử lý đồng bộ; PDF lớn làm UI chờ.
- Không phân quyền/chọn tài liệu theo người dùng.
- Không có source viewer (chỉ tên file + trang + snippet).
- Đổi embedding model cần re-index.
- Không có backup tự động.

## Cấu trúc code

```text
app/
├── main.py          # trang Streamlit
├── config.py        # Settings
├── db.py            # SQLite
├── pdf.py           # validate/extract PDF
├── chunking.py      # chunk theo trang
├── embeddings.py    # embedding API
├── vector_store.py  # Qdrant
├── ingest.py        # pipeline upload → READY/ERROR
├── llm.py           # LLM streaming
├── rag.py           # retrieval + prompt + NOT_FOUND
├── prompts.py       # prompt template
├── errors.py        # mã lỗi/thông điệp
├── ui.py            # component UI
└── eval.py          # runner eval
```
