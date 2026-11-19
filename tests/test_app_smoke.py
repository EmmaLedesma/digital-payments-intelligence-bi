"""Smoke test: cada página de la app corre sin excepciones."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

VIEWS = sorted((Path(__file__).resolve().parents[1] / "views").glob("*.py"))


@pytest.mark.parametrize("view", VIEWS, ids=lambda p: p.name)
def test_view_corre_sin_errores(view):
    at = AppTest.from_file(str(view), default_timeout=60).run()
    assert not at.exception, at.exception
