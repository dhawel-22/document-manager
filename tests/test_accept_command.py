"""Tests for the accept command (spec/accept.md, "The command"). Each one
runs the command the way Ernie types it (like RP-5)."""

import subprocess
import sys
from pathlib import Path

from document_manager.check import check_folder
from document_manager.register import register_folder

PROJECT = Path(__file__).resolve().parent.parent
QUESTION = "Accept these changes? Type yes to accept: "


def registered_docs(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "note.txt").write_bytes(b"hello\n")
    reg = tmp_path / "register.db"
    register_folder(docs, reg)
    return docs, reg


def accept(docs, reg, answer):
    return subprocess.run(
        [sys.executable, "-m", "document_manager", "accept", str(docs), str(reg)],
        cwd=PROJECT, input=answer, capture_output=True, text=True,
    )


def test_yes_accepts(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "note.txt").write_bytes(b"hallo\n")
    done = accept(docs, reg, "yes\n")
    assert done.returncode == 0, done.stderr
    assert done.stdout == (
        "Changed: 1, new: 0, missing: 0, unchanged: 0.\n"
        "  changed  note.txt\n"
        f"{QUESTION}Accepted {docs}. Files listed: 1.\n"
    )
    assert check_folder(docs, reg).changed == []


def test_anything_but_yes_saves_nothing(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "note.txt").write_bytes(b"hallo\n")
    before = reg.read_bytes()
    for answer in ("no\n", "y\n", "\n", ""):
        done = accept(docs, reg, answer)
        assert done.returncode == 0, done.stderr
        assert done.stdout.endswith(f"{QUESTION}Nothing was saved.\n")
        assert reg.read_bytes() == before


def test_nothing_changed_doesnt_ask(tmp_path):
    docs, reg = registered_docs(tmp_path)
    before = reg.read_bytes()
    done = accept(docs, reg, "yes\n")
    assert done.returncode == 0, done.stderr
    assert done.stdout == "Nothing has changed. Files checked: 1.\n"
    assert reg.read_bytes() == before


def test_a_problem_is_one_plain_line(tmp_path):
    docs, _ = registered_docs(tmp_path)
    done = accept(docs, tmp_path / "missing.db", "yes\n")
    assert done.returncode == 1
    assert done.stdout.startswith("Problem: ") and done.stdout.count("\n") == 1
    assert not (tmp_path / "missing.db").exists()
