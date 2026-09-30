"""First test: the tests must run from the project's own Python (D-019)."""

import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent


def test_runs_from_the_project_venv():
    assert Path(sys.prefix).resolve() == PROJECT / ".venv"
