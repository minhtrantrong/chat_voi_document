from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app" / "main.py"


def test_app_empty_state_renders_without_exception(qdrant_settings):
    app = AppTest.from_file(APP, default_timeout=30)
    app.run()

    assert not app.exception
    assert app.title[0].value == "Chat với tài liệu"
    assert len(app.chat_input) == 1
    assert app.chat_input[0].disabled is True
    assert app.info
