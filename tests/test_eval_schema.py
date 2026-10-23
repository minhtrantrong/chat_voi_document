from __future__ import annotations

import json
from pathlib import Path

import pytest

from app import eval as module
from app.config import get_settings
from app.eval import load_dataset, normalize, run, score_item, summarize, write_report
from app.rag import Source

DATASET = Path("tests/eval/dataset.json")


def test_dataset_shape_and_schema():
    items = load_dataset(DATASET)
    assert len(items) == 30
    kinds = {item["type"] for item in items}
    assert kinds == {"in_doc", "multi_doc", "out_of_scope"}
    counts = {kind: sum(item["type"] == kind for item in items) for kind in kinds}
    assert counts == {"in_doc": 10, "multi_doc": 10, "out_of_scope": 10}
    assert len({item["id"] for item in items}) == 30

    required = {
        "id",
        "type",
        "question",
        "expected_docs",
        "expected_pages",
        "must_contain",
        "must_not_contain",
    }
    for item in items:
        assert required <= set(item), item["id"]
        assert isinstance(item["question"], str) and item["question"].strip()
        assert isinstance(item["expected_docs"], list)
        assert isinstance(item["expected_pages"], list)
        assert isinstance(item["must_contain"], list)
        assert isinstance(item["must_not_contain"], list)
        assert all(isinstance(page, int) for page in item["expected_pages"])
        if item["type"] == "out_of_scope":
            assert item["expected_docs"] == []
        else:
            assert item["expected_docs"]


def test_load_dataset_rejects_non_list(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        load_dataset(path)


def test_normalize_removes_diacritics_and_spaces():
    assert normalize("  Hạn   chót  ") == "han chot"
    assert normalize("Điều 12") == "dieu 12"


def _source(file_name="hop-dong.pdf", page=1):
    return Source("S1", "d", file_name, page, 0, "text", 0.9)


def test_score_in_doc_pass():
    item = {
        "id": "in-01",
        "type": "in_doc",
        "question": "q",
        "expected_docs": ["hop-dong.pdf"],
        "expected_pages": [1],
        "must_contain": ["30/11/2026"],
        "must_not_contain": [],
    }
    result = score_item(item, "Hạn chót là 30/11/2026 [S1]", [_source()], False)
    assert result["ok"] is True
    assert result["doc_ok"] and result["page_ok"] and result["content_ok"]


def test_score_in_doc_fail_missing_keyword():
    item = {
        "id": "in-02",
        "type": "in_doc",
        "expected_docs": ["hop-dong.pdf"],
        "expected_pages": [1],
        "must_contain": ["1.200.000.000"],
        "must_not_contain": [],
    }
    result = score_item(item, "Không rõ", [_source()], False)
    assert result["ok"] is False
    assert result["content_ok"] is False


def test_score_multi_doc_requires_two_sources():
    item = {
        "id": "multi-01",
        "type": "multi_doc",
        "expected_docs": ["a.pdf", "b.pdf"],
        "expected_pages": [],
        "must_contain": ["x"],
        "must_not_contain": [],
    }
    one = score_item(item, "x", [_source("a.pdf")], False)
    assert one["doc_ok"] is False
    two = score_item(item, "x", [_source("a.pdf"), _source("b.pdf")], False)
    assert two["ok"] is True


def test_score_out_of_scope():
    item = {
        "id": "out-01",
        "type": "out_of_scope",
        "expected_docs": [],
        "expected_pages": [],
        "must_contain": [],
        "must_not_contain": [],
    }
    assert score_item(item, "Không tìm thấy", [], True)["ok"] is True
    assert score_item(item, "Paris", [], False)["ok"] is False


def test_summarize():
    rows = [
        {"type": "in_doc", "ok": True, "sources": [1]},
        {"type": "in_doc", "ok": False, "sources": []},
        {"type": "multi_doc", "ok": True, "sources": [1, 2]},
        {"type": "out_of_scope", "ok": True, "sources": []},
    ]
    summary = summarize(rows)
    assert summary["total"] == 4
    assert summary["in_doc"] == {"passed": 1, "total": 2}
    assert summary["multi_doc"] == {"passed": 1, "total": 1}
    assert summary["out_of_scope"] == {"passed": 1, "total": 1}
    assert summary["overall"] == {"passed": 3, "total": 4}


def test_write_report(tmp_path):
    summary = {
        "total": 1,
        "in_doc": {"passed": 0, "total": 1},
        "multi_doc": {"passed": 0, "total": 0},
        "out_of_scope": {"passed": 0, "total": 0},
        "source_hit": {"passed": 0, "total": 1},
        "overall": {"passed": 0, "total": 1},
    }
    rows = [
        {
            "id": "in-01",
            "type": "in_doc",
            "ok": False,
            "doc_ok": False,
            "page_ok": True,
            "content_ok": False,
            "forbidden_ok": True,
            "not_found": False,
            "answer": "",
            "sources": [],
        }
    ]
    prefix = tmp_path / "report"
    write_report(summary, rows, prefix)
    assert pathlib_json(prefix.with_suffix(".json"))["summary"]["total"] == 1
    assert "in-01" in prefix.with_suffix(".md").read_text(encoding="utf-8")


def pathlib_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_reindex_fixtures_requires_pdfs(tmp_path):
    with pytest.raises(FileNotFoundError):
        module.reindex_fixtures(tmp_path)


def test_reindex_fixtures_calls_ingest(tmp_path, monkeypatch):
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF-1.7\n")
    calls = []
    monkeypatch.setattr(
        module,
        "ingest_pdf",
        lambda name, _file_obj, **_kwargs: calls.append(name),
    )
    module.reindex_fixtures(tmp_path)
    assert calls == ["a.pdf"]


def test_run_requires_api_key(settings, tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()
    with pytest.raises(RuntimeError):
        run(
            tmp_path / "missing.json",
            fixtures_dir=tmp_path,
            reindex=False,
            out_prefix=tmp_path / "report",
        )


def test_run_with_fake_answer(settings, tmp_path, monkeypatch):
    dataset_path = tmp_path / "dataset.json"
    dataset_path.write_text(
        json.dumps(
            [
                {
                    "id": "in-01",
                    "type": "in_doc",
                    "question": "q",
                    "expected_docs": ["a.pdf"],
                    "expected_pages": [1],
                    "must_contain": ["x"],
                    "must_not_contain": [],
                }
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        module,
        "answer_question",
        lambda _question, _history: ("x", [_source("a.pdf")], False),
    )
    summary = run(
        dataset_path,
        fixtures_dir=tmp_path,
        reindex=False,
        out_prefix=tmp_path / "report",
    )
    assert summary["overall"] == {"passed": 1, "total": 1}
    assert (tmp_path / "report.json").exists()
