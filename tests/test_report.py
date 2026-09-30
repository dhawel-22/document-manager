"""Tests for the report rules in spec/report.md (RP-1 to RP-5)."""

import subprocess
import sys
from pathlib import Path

from document_manager.__main__ import main

PROJECT = Path(__file__).resolve().parent.parent


def make_docs(tmp_path):
    """A small folder of fake documents."""
    docs = tmp_path / "docs"
    (docs / "letters").mkdir(parents=True)
    (docs / "letters" / "note.txt").write_bytes(b"hello\n")
    (docs / "report.docx").write_bytes(b"fake report")
    (docs / "empty.txt").write_bytes(b"")
    return docs


def test_rp1_register_says_how_many(tmp_path, capsys):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    assert main(["register", str(docs), str(reg)]) == 0
    assert capsys.readouterr().out == f"Registered {docs}. Files listed: 3.\n"


def test_rp2_check_shows_every_finding(tmp_path, capsys):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    main(["register", str(docs), str(reg)])
    (docs / "letters" / "note.txt").write_bytes(b"hallo\n")
    (docs / "letters" / "new.txt").write_bytes(b"new")
    (docs / "report.docx").unlink()
    capsys.readouterr()
    assert main(["check", str(docs), str(reg)]) == 0
    assert capsys.readouterr().out == (
        "Changed: 1, new: 1, missing: 1, unchanged: 1.\n"
        "  changed  letters/note.txt\n"
        "  new      letters/new.txt\n"
        "  missing  report.docx\n"
    )


def test_rp3_nothing_changed_is_one_line(tmp_path, capsys):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    main(["register", str(docs), str(reg)])
    capsys.readouterr()
    assert main(["check", str(docs), str(reg)]) == 0
    assert capsys.readouterr().out == "Nothing has changed. Files checked: 3.\n"


def test_rp4_problem_in_one_plain_line(tmp_path, capsys):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    main(["register", str(docs), str(reg)])
    other = tmp_path / "other"
    other.mkdir()
    capsys.readouterr()
    assert main(["check", str(other), str(reg)]) == 1
    out = capsys.readouterr().out
    assert out.startswith("Problem: ") and "CK-7" in out
    assert out.count("\n") == 1


def test_rp5_the_commands_work_as_written(tmp_path):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    command = [sys.executable, "-m", "document_manager"]
    registered = subprocess.run(
        [*command, "register", str(docs), str(reg)],
        cwd=PROJECT, capture_output=True, text=True,
    )
    checked = subprocess.run(
        [*command, "check", str(docs), str(reg)],
        cwd=PROJECT, capture_output=True, text=True,
    )
    assert registered.returncode == 0, registered.stderr
    assert checked.returncode == 0, checked.stderr
    assert checked.stdout == "Nothing has changed. Files checked: 3.\n"
