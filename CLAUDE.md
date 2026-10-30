# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Use the agent-memory MCP tools for project knowledge:
- Before a task, call query_memory with the task topic.
- After a task, call ingest_memory with a summary and source="<repo>@<branch>".
- End a session with consolidate_memories when memory_stats reports >= 2 unconsolidated.

## Project

Single-page Streamlit app: upload PDFs, ask an LLM about them (RAG), see sources (file + page). No authentication by design (localhost / trusted network only). UI strings, error messages, prompts and comments are in Vietnamese — keep new user-facing text and docstrings in Vietnamese to match.

## Commands

```bash
pip install -e ".[dev]"            # or: uv sync --extra dev
# Qdrant chạy như system service (không dùng Docker); health: curl -f http://localhost:6333/healthz
streamlit run app/main.py          # http://localhost:8501

pytest -q                          # all tests (integration tests auto-skip if Qdrant is down)
pytest -q -m "not integration"     # unit only
pytest -q -m integration           # needs Qdrant
pytest tests/test_rag.py::test_name -q   # single test
pytest --cov=app                   # coverage (omits app/main.py, app/shared/*)

ruff check . && ruff format --check .   # line-length 100, rules E,F,I,UP,B,SIM; app/shared excluded
mypy app

python tests/eval/generate_fixtures.py          # build sample PDFs
python -m app.eval --reindex --out eval_report  # 30-question eval; needs LLM server + Qdrant
```

## Architecture

Pipeline modules in `app/` form two flows that share `config.py`, `embeddings.py` and `vector_store.py`:

- **Ingest** (`ingest.py`): validate/save PDF to `data/uploads/<uuid>.pdf` → SQLite doc row (`db.py`) → `pdf.py` extract per page → `chunking.py` (token-based, page-aware, tiktoken) → `embeddings.py` → `vector_store.py` upsert to Qdrant → `mark_ready`. On any failure the doc is marked `ERROR` with a code and its Qdrant points are cleaned up. Processing is synchronous inside the Streamlit request.
- **Chat** (`rag.py`): `embed_query` → `search_chunks` (score threshold, optional `doc_ids` filter) → `select_hits` (dedupe + `max_chunks_per_doc` diversity) → `build_context` (labels `[S1]…`, capped by `max_context_chars`) → `SYSTEM_PROMPT` (`prompts.py`) → `llm.stream_chat`. Empty retrieval short-circuits to `NOT_FOUND`; the model signals "not found" by emitting the sentinel `KHONG_TIM_THAY`, which `finalize_answer` converts into `NOT_FOUND` and drops sources.

Errors: pipeline exceptions carry a `.code` (e.g. `PDF_NO_TEXT`, `EMBEDDING_FAILED`); `errors.py` maps codes to user-facing Vietnamese messages. Add new codes to `ERROR_MESSAGES` or they fall back to `INTERNAL`.

`app/main.py` + `ui.py` are the Streamlit layer (chat history lives only in session state). `app/shared/` is legacy code excluded from lint and coverage.

## LLM / embedding configuration

Both chat and embeddings use the `openai` client against any OpenAI-compatible endpoint, configured only via env / `.env` (see `.env.example`, `app/config.py`). **Default is LM Studio** (`http://localhost:1234/v1`, key `lm-studio`, `LLM_MODEL=qwen/qwen3-1.7b`, `EMBEDDING_MODEL=text-embedding-nomic-embed-text-v1.5`, `EMBEDDING_DIM=768`). Ollama and OpenAI are supported by overriding env vars; model names must match the server's identifiers.

`EMBEDDING_DIM` must match the embedding model. Changing the model/dimension requires deleting the Qdrant collection and re-indexing all PDFs.

## Testing notes

`tests/conftest.py` provides a `settings` fixture that isolates `DATA_DIR` in tmp, uses a unique Qdrant collection per test and sets `EMBEDDING_DIM=8`; use it rather than touching real `data/`. `get_settings()` is `lru_cache`d, so tests that change env vars must go through the fixture (or clear the cache). Unit tests mock the OpenAI client; real LLM runs are only for eval/E2E.

`docs/testing/` holds the test plans and `test_reports/<ID>/` holds E2E run artifacts; `.claude/skills/test-report-*` automate running and reviewing those reports. Those docs describe runs done with Ollama — don't rewrite them to LM Studio (they are historical records).
