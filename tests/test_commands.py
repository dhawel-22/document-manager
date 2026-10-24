"""Tests for the commands' words in one place (src/document_manager/commands.py).

The existing command tests (RP-1 to RP-5, SM-8) check the words themselves.
These check that run() gives them back the way the window will need them,
and that the commands print exactly what run() gives.
"""

from document_manager.__main__ import main
from document_manager.commands import run


def make_docs(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "note.txt").write_bytes(b"hello\n")
    return docs


def test_run_gives_the_result_and_the_words(tmp_path):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    assert run("register", str(docs), str(reg)) == (0, f"Registered {docs}. Files listed: 1.")
    assert run("check", str(docs), str(reg)) == (0, "Nothing has changed. Files checked: 1.")


def test_run_says_a_problem_in_one_plain_line(tmp_path):
    docs = make_docs(tmp_path)
    code, words = run("check", str(docs), str(tmp_path / "missing.db"))
    assert code == 1
    assert words.startswith("Problem: ") and "\n" not in words


def test_run_refuses_an_unknown_command(tmp_path):
    docs = make_docs(tmp_path)
    assert run("unknown", str(docs), str(tmp_path / "register.db")) == (
        1, "Problem: Unknown command: unknown")
    assert not (tmp_path / "register.db").exists()


def test_the_commands_print_exactly_what_run_gives(monkeypatch, capsys):
    monkeypatch.setattr("document_manager.__main__.run", lambda *args: (1, "Fake words."))
    assert main(["check", r"D:\fake\docs", r"D:\fake\register.db"]) == 1
    assert capsys.readouterr().out == "Fake words.\n"
