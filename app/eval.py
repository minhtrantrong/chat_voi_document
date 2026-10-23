"""Chạy bộ eval 30 câu và xuất báo cáo JSON/Markdown.

Cách dùng:
    python -m app.eval --reindex
    python -m app.eval --out eval_report
"""

from __future__ import annotations

import argparse
import json
import unicodedata
from dataclasses import asdict
from pathlib import Path

from app.config import get_settings, require_api_key
from app.db import clear_documents, count_ready_documents, init_db
from app.ingest import ingest_pdf
from app.rag import answer_question
from app.vector_store import ensure_collection, get_client


def normalize(text: str) -> str:
    text = text.lower().replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return " ".join(text.split())


def load_dataset(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Dataset phải là một mảng JSON.")
    return data


def reset_store() -> None:
    settings = get_settings()
    client = get_client()
    if client.collection_exists(settings.qdrant_collection):
        client.delete_collection(settings.qdrant_collection)
    ensure_collection(client)
    init_db()
    clear_documents()


def reindex_fixtures(fixtures_dir: Path) -> None:
    pdfs = sorted(fixtures_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(
            f"Không có PDF trong {fixtures_dir}. Chạy tests/eval/generate_fixtures.py."
        )
    for pdf in pdfs:
        with pdf.open("rb") as file_obj:
            ingest_pdf(pdf.name, file_obj, size_bytes=pdf.stat().st_size)
        print(f"indexed {pdf.name}")


def score_item(
    item: dict,
    answer: str,
    sources: list,
    not_found: bool,
) -> dict:
    normalized_answer = normalize(answer)
    source_docs = {source.file_name for source in sources}
    source_pages = {source.page for source in sources}
    item_type = item["type"]

    if item_type == "out_of_scope":
        ok = not_found and not sources
        doc_ok = page_ok = content_ok = forbidden_ok = ok
    else:
        expected_docs = set(item.get("expected_docs", []))
        if item_type == "multi_doc":
            doc_ok = len(source_docs & expected_docs) >= 2
        else:
            doc_ok = len(source_docs & expected_docs) >= 1
        expected_pages = set(item.get("expected_pages", []))
        page_ok = not expected_pages or bool(source_pages & expected_pages)
        content_ok = all(
            normalize(keyword) in normalized_answer for keyword in item.get("must_contain", [])
        )
        forbidden_ok = all(
            normalize(keyword) not in normalized_answer
            for keyword in item.get("must_not_contain", [])
        )
        ok = doc_ok and page_ok and content_ok and forbidden_ok and not not_found

    return {
        "id": item["id"],
        "type": item_type,
        "ok": bool(ok),
        "doc_ok": bool(doc_ok),
        "page_ok": bool(page_ok),
        "content_ok": bool(content_ok),
        "forbidden_ok": bool(forbidden_ok),
        "not_found": not_found,
        "answer": answer,
        "sources": [asdict(source) for source in sources],
    }


def summarize(results: list[dict]) -> dict:
    def bucket(kind: str) -> dict[str, int]:
        rows = [row for row in results if row["type"] == kind]
        return {"passed": sum(row["ok"] for row in rows), "total": len(rows)}

    in_doc = bucket("in_doc")
    multi_doc = bucket("multi_doc")
    out_of_scope = bucket("out_of_scope")
    source_rows = [row for row in results if row["type"] in {"in_doc", "multi_doc"}]
    source_hit = {
        "passed": sum(bool(row["sources"]) for row in source_rows),
        "total": len(source_rows),
    }
    return {
        "total": len(results),
        "in_doc": in_doc,
        "multi_doc": multi_doc,
        "out_of_scope": out_of_scope,
        "source_hit": source_hit,
        "overall": {
            "passed": sum(row["ok"] for row in results),
            "total": len(results),
        },
    }


def write_report(summary: dict, results: list[dict], out_prefix: Path) -> None:
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = out_prefix.with_suffix(".json")
    md_path = out_prefix.with_suffix(".md")
    json_path.write_text(
        json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Eval report",
        "",
        f"- Tổng: **{summary['overall']['passed']}/{summary['overall']['total']}**",
        f"- In-doc: **{summary['in_doc']['passed']}/{summary['in_doc']['total']}**",
        f"- Multi-doc: **{summary['multi_doc']['passed']}/{summary['multi_doc']['total']}**",
        f"- Out-of-scope: **{summary['out_of_scope']['passed']}/"
        f"{summary['out_of_scope']['total']}**",
        f"- Có nguồn: **{summary['source_hit']['passed']}/{summary['source_hit']['total']}**",
        "",
        "## Câu fail",
        "",
        "| ID | Type | Lý do |",
        "|---|---|---|",
    ]
    for row in results:
        if row["ok"]:
            continue
        reasons = []
        for key in ("doc_ok", "page_ok", "content_ok", "forbidden_ok"):
            if not row[key]:
                reasons.append(key)
        if row["type"] == "out_of_scope" and not row["not_found"]:
            reasons.append("không NOT_FOUND")
        lines.append(f"| {row['id']} | {row['type']} | {', '.join(reasons) or 'unknown'} |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {json_path} and {md_path}")


def run(dataset_path: Path, *, fixtures_dir: Path, reindex: bool, out_prefix: Path) -> dict:
    require_api_key(get_settings())
    init_db()
    if reindex:
        reset_store()
        reindex_fixtures(fixtures_dir)
    elif count_ready_documents() == 0:
        print("CẢNH BÁO: chưa có tài liệu READY; chạy với --reindex hoặc upload PDF trước.")

    dataset = load_dataset(dataset_path)
    results: list[dict] = []
    for item in dataset:
        try:
            answer, sources, not_found = answer_question(item["question"], [])
            results.append(score_item(item, answer, sources, not_found))
        except Exception as exc:
            results.append(
                {
                    "id": item.get("id", "?"),
                    "type": item.get("type", "?"),
                    "ok": False,
                    "doc_ok": False,
                    "page_ok": False,
                    "content_ok": False,
                    "forbidden_ok": False,
                    "not_found": False,
                    "answer": "",
                    "sources": [],
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    summary = summarize(results)
    write_report(summary, results, out_prefix)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Chạy eval RAG.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("tests/eval/dataset.json"),
    )
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=Path("tests/eval/fixtures"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("eval_report"),
    )
    parser.add_argument(
        "--reindex",
        action="store_true",
        help="Xoá collection + DB rồi nạp lại PDF mẫu.",
    )
    args = parser.parse_args()
    run(
        args.dataset,
        fixtures_dir=args.fixtures,
        reindex=args.reindex,
        out_prefix=args.out,
    )


if __name__ == "__main__":
    main()
