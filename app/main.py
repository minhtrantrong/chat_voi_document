"""Trang Streamlit duy nhất: upload PDF và chat với tài liệu."""

from __future__ import annotations

import sys
from pathlib import Path

# Cho phép `streamlit run app/main.py` từ repo root.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from app.config import get_settings
from app.db import (
    Document,
    DocumentStatus,
    init_db,
    list_documents,
)
from app.db import (
    delete_document as delete_document_row,
)
from app.errors import ERROR_MESSAGES, error_message, log_error
from app.ingest import IngestResult, ingest_many
from app.rag import (
    NOT_FOUND,
    finalize_answer,
    prepare_answer,
    stream_answer,
)
from app.ui import (
    empty_state_message,
    format_bytes,
    has_ready_documents,
    ingest_stage_text,
    md_escape,
    render_sources,
    source_to_dict,
    status_text,
)
from app.vector_store import (
    delete_document as delete_vector_document,
)
from app.vector_store import (
    ensure_collection,
    health,
)

st.set_page_config(
    page_title="Chat với tài liệu",
    page_icon="📄",
    layout="wide",
)


def _init_state() -> None:
    defaults = {
        "messages": [],
        "uploader_nonce": 0,
        "confirm_delete_id": None,
        "last_ingest": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _delete_document(doc: Document) -> bool:
    try:
        delete_vector_document(doc.id)
    except Exception as exc:
        log_error(exc, context="delete_document")
        st.error("Không xoá được dữ liệu vector. Thử lại sau.")
        return False

    delete_document_row(doc.id)
    try:
        Path(doc.stored_path).unlink(missing_ok=True)
    except OSError:
        st.warning("Đã xoá metadata nhưng không xoá được tệp gốc.")
    st.session_state.messages = []
    return True


def _render_last_ingest() -> None:
    for item in st.session_state.get("last_ingest", []):
        if item["ok"]:
            st.success(f"{item['file_name']}: xử lý xong.")
        else:
            st.error(item["message"])


def _render_sidebar(docs: list[Document], qdrant_ok: bool) -> None:
    with st.sidebar:
        st.header("Tài liệu")
        settings = get_settings()
        if not qdrant_ok:
            st.warning("Qdrant chưa sẵn sàng. Hãy khởi động dịch vụ Qdrant rồi tải lại trang.")

        uploaded = st.file_uploader(
            "Tải PDF",
            type=["pdf"],
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_nonce}",
            help=(f"Tối đa {settings.max_upload_mb} MB, {settings.max_pages} trang mỗi tệp."),
        )

        if uploaded:
            with st.status(f"Đang xử lý {len(uploaded)} tệp…", expanded=True) as status:
                bar = st.progress(0)
                lines = {}
                for index, item in enumerate(uploaded):
                    lines[index] = st.empty()
                    lines[index].markdown(ingest_stage_text(item.name, "pending"))
                queue = iter(range(len(uploaded)))

                def progress_factory(name: str):
                    line = lines[next(queue)]

                    def update(stage: str, percent: int) -> None:
                        percent = max(0, min(100, int(percent)))
                        bar.progress(percent)
                        line.markdown(ingest_stage_text(name, stage, percent))

                    return update

                results: list[IngestResult] = ingest_many(
                    [(item.name, item, item.size) for item in uploaded],
                    progress_factory=progress_factory,
                )
                ok_count = sum(result.ok for result in results)
                fail_count = len(results) - ok_count
                status.update(
                    label=f"Đã xử lý {ok_count} tệp, {fail_count} tệp lỗi.",
                    state="complete" if fail_count == 0 else "error",
                )

            st.session_state.last_ingest = [
                {
                    "file_name": result.file_name,
                    "ok": result.ok,
                    "message": error_message(result.error, result.file_name)
                    if result.error
                    else "",
                }
                for result in results
            ]
            st.session_state.uploader_nonce += 1
            st.rerun()

        _render_last_ingest()

        if not docs:
            st.caption("Chưa có tài liệu. Tải PDF đầu tiên.")
        for doc in docs:
            with st.container(border=True):
                st.markdown(f"**{md_escape(doc.file_name)}**")
                meta = []
                if doc.page_count:
                    meta.append(f"{doc.page_count} trang")
                meta.append(format_bytes(doc.size_bytes))
                if doc.created_at:
                    meta.append(f"tạo {doc.created_at[:10]}")
                st.caption(" · ".join(meta))
                st.caption(status_text(doc))
                if doc.status == DocumentStatus.ERROR and doc.error_code:
                    st.caption(ERROR_MESSAGES.get(doc.error_code, "Không xử lý được tài liệu."))

                if st.button("Xoá", key=f"delete_{doc.id}"):
                    st.session_state.confirm_delete_id = doc.id

                if st.session_state.confirm_delete_id == doc.id:
                    st.warning(f"Xoá **{md_escape(doc.file_name)}**? Không hoàn tác.")
                    col_yes, col_no = st.columns(2)
                    if col_yes.button(
                        "Xác nhận",
                        key=f"confirm_{doc.id}",
                        type="primary",
                    ) and _delete_document(doc):
                        st.session_state.confirm_delete_id = None
                        st.rerun()
                    if col_no.button("Huỷ", key=f"cancel_{doc.id}"):
                        st.session_state.confirm_delete_id = None
                        st.rerun()


def _render_chat(docs: list[Document]) -> None:
    st.title("Chat với tài liệu")
    st.caption("Tải PDF và hỏi AI về nội dung tài liệu.")

    state = empty_state_message(docs)
    if state is not None:
        kind, message = state
        if kind == "warning":
            st.warning(message)
        else:
            st.info(message)

    for message in st.session_state.messages[-50:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                render_sources(message["sources"])

    ready = has_ready_documents(docs)
    question = st.chat_input(
        "Hỏi về nội dung tài liệu…",
        disabled=not ready,
    )
    if not question:
        return

    question = question.strip()[: get_settings().max_question_chars]
    if not question:
        return

    history_before = list(st.session_state.messages)
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            prepared = prepare_answer(question, history_before)
        except Exception as exc:
            log_error(exc, context="prepare_answer")
            st.error(error_message(exc))
            return

        if prepared.not_found:
            st.markdown(NOT_FOUND)
            st.session_state.messages.append(
                {"role": "assistant", "content": NOT_FOUND, "sources": []}
            )
            return

        placeholder = st.empty()
        try:
            with placeholder.container():
                raw = st.write_stream(stream_answer(prepared))
                text = raw if isinstance(raw, str) else "".join(str(part) for part in raw)
        except Exception as exc:
            log_error(exc, context="stream_answer")
            st.error(error_message(exc))
            return

        final_text, final_sources, not_found = finalize_answer(text, prepared.sources)
        if not_found or "KHONG_TIM_THAY" in text:
            placeholder.empty()
            placeholder.markdown(NOT_FOUND)
            final_sources = []

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": final_text,
                "sources": [source_to_dict(source) for source in final_sources],
            }
        )
        render_sources(final_sources)


def main() -> None:
    _init_state()
    init_db()

    qdrant_ok = health()
    if qdrant_ok:
        try:
            ensure_collection()
        except Exception as exc:
            log_error(exc, context="ensure_collection")
            if isinstance(exc, RuntimeError) and "vector size" in str(exc):
                st.sidebar.error(str(exc))
            else:
                st.sidebar.error(error_message(exc))
            qdrant_ok = False

    docs = list_documents()
    _render_sidebar(docs, qdrant_ok)
    _render_chat(docs)


main()
