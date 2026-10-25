"""Tests for the counter, spec/window.md v1.4 (WN-13, WN-14, On trust): the
engine tells a counter how far a run has got, and a counter that stops the
run stops it before anything is saved. The window's own counter comes with
the window.

Every document here is a fake, made by the test in a temporary folder.
"""

import sqlite3

import docx
import pytest

from document_manager.commands import accept, changes_to_accept, run
from document_manager.register import register_folder

# The fake folder has two files at the top and one in letters. The counter
# is told 2 files found, then 3, then 0 to 3 read. Two of the files are Word
# documents, so Summarize tells it 0 to 2 read.
FOUND = [(2, None), (3, None)]
FILES_READ = FOUND + [(0, 3), (1, 3), (2, 3), (3, 3)]
DOCUMENTS_READ = FOUND + [(0, 2), (1, 2), (2, 2)]


class Stopped(Exception):
    """What a counter raises to stop a run, as the window's will (WN-14)."""


def make_docs(tmp_path):
    """A small folder of fake documents: two Word documents and a text file."""
    docs = tmp_path / "docs"
    (docs / "letters").mkdir(parents=True)
    for path, title in ((docs / "report.docx", "Report"), (docs / "letters" / "note.docx", "Note")):
        made = docx.Document()
        made.core_properties.title = title
        made.add_paragraph("A fake document for the tests.")
        made.save(path)
    (docs / "notes.txt").write_bytes(b"not a Word document\n")
    return docs


def listening():
    """A counter that notes everything it's told."""
    told = []
    return lambda done, total: told.append((done, total)), told


def stops_at(call):
    """A counter that stops the run the nth time it's told something."""
    told = []

    def counter(done, total):
        told.append((done, total))
        if len(told) == call:
            raise Stopped

    return counter


def as_version_1(register_file):
    """Turn a register file back into version 1, as made before summaries."""
    con = sqlite3.connect(register_file)
    try:
        con.executescript(
            "DROP TABLE accepted_file; DROP TABLE accepted; DROP TABLE summary;"
            " PRAGMA user_version = 1;"
        )
    finally:
        con.close()


def test_wn13_the_counter_is_told_the_files_found_then_read(tmp_path):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    heard = {}
    for command in ("register", "check", "summarize", "summaries"):
        counter, told = listening()
        assert run(command, str(docs), str(reg), counter)[0] == 0
        heard[command] = told
    assert heard == {"register": FILES_READ, "check": FILES_READ,
                     "summarize": DOCUMENTS_READ, "summaries": []}


def test_wn13_accept_counts_twice(tmp_path):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    register_folder(docs, reg)
    (docs / "notes.txt").write_bytes(b"changed\n")
    counter, told = listening()
    _, _, found = changes_to_accept(str(docs), str(reg), counter)
    assert accept(str(docs), str(reg), found, counter)[0] == 0
    assert told == FILES_READ + FILES_READ


@pytest.mark.parametrize("call", range(1, len(FILES_READ) + 1))
def test_wn14_a_stopped_register_makes_no_register_file(tmp_path, call):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    with pytest.raises(Stopped):
        run("register", str(docs), str(reg), stops_at(call))
    assert not reg.exists()


@pytest.mark.parametrize("call", range(1, len(FILES_READ) + 1))
def test_wn14_a_stopped_check_leaves_the_register_file_as_it_was(tmp_path, call):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    register_folder(docs, reg)
    before = reg.read_bytes()
    with pytest.raises(Stopped):
        run("check", str(docs), str(reg), stops_at(call))
    assert reg.read_bytes() == before


@pytest.mark.parametrize("call", range(1, len(DOCUMENTS_READ) + 1))
def test_wn14_a_stopped_summarize_saves_nothing(tmp_path, call):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    register_folder(docs, reg)
    as_version_1(reg)  # not even brought up to date (spec/summaries.md v1.5)
    before = reg.read_bytes()
    with pytest.raises(Stopped):
        run("summarize", str(docs), str(reg), stops_at(call))
    assert reg.read_bytes() == before


@pytest.mark.parametrize("call", range(1, len(FILES_READ) + 1))
def test_wn14_a_stopped_accept_saves_nothing(tmp_path, call):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    register_folder(docs, reg)
    (docs / "notes.txt").write_bytes(b"changed\n")
    _, _, found = changes_to_accept(str(docs), str(reg))
    before = reg.read_bytes()
    with pytest.raises(Stopped):
        accept(str(docs), str(reg), found, stops_at(call))
    assert reg.read_bytes() == before
