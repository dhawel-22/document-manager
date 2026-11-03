"""Tests for the register rules in spec/register.md (RG-1 to RG-7)."""

import os
import re
import shutil
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from document_manager.commands import changes_to_accept, run, run_overview
from document_manager.fingerprint import fingerprint
from document_manager.progress import Progress
from document_manager.register import STEP_TABLES, STEPS, prepare_register, register_folder

# Every command that's given a register file (RG-7).
EVERY_COMMAND = ["register", "check", "summarize", "summaries", "accept", "overview",
                 "ai-summarize", "ai-summaries"]


def make_docs(tmp_path):
    """A small folder of fake documents."""
    docs = tmp_path / "docs"
    (docs / "letters").mkdir(parents=True)
    (docs / "letters" / "note.txt").write_bytes(b"hello\n")
    (docs / "report.docx").write_bytes(b"fake report")
    (docs / "empty.txt").write_bytes(b"")
    return docs


def query(register_file, sql):
    con = sqlite3.connect(register_file)
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


def test_rg1_lists_every_file(tmp_path):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    assert register_folder(docs, reg).count == 3
    assert query(reg, "SELECT path, size, fingerprint FROM file ORDER BY path") == [
        ("empty.txt", 0, fingerprint(docs / "empty.txt")),
        ("letters/note.txt", 6, fingerprint(docs / "letters" / "note.txt")),
        ("report.docx", 11, fingerprint(docs / "report.docx")),
    ]


def test_rg2_saves_the_folder_and_the_time(tmp_path):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    register_folder(docs, reg)
    [(path, when)] = query(reg, "SELECT path, registered_at FROM folder")
    assert path == str(docs.resolve())
    age = datetime.now(timezone.utc) - datetime.fromisoformat(when)
    assert timedelta(0) <= age < timedelta(minutes=1)


def test_rg3_only_reads(tmp_path):
    docs = make_docs(tmp_path)

    def snapshot():
        files = [p for p in docs.rglob("*") if p.is_file()]
        return {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}

    before = snapshot()
    register_folder(docs, tmp_path / "register.db")
    assert snapshot() == before


def test_rg4_register_file_cannot_be_inside_the_folder(tmp_path):
    docs = make_docs(tmp_path)
    with pytest.raises(ValueError, match="RG-4"):
        register_folder(docs, docs / "register.db")
    assert not (docs / "register.db").exists()


def test_rg5_same_folder_twice_is_refused(tmp_path):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    register_folder(docs, reg)
    first = query(reg, "SELECT * FROM file")
    (docs / "new.txt").write_bytes(b"new")
    with pytest.raises(ValueError, match="RG-5"):
        register_folder(docs, reg)
    assert query(reg, "SELECT * FROM file") == first


def test_rg5_refused_folder_leaves_the_register_file_as_it_was(tmp_path):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    register_folder(docs, reg)
    con = sqlite3.connect(reg)  # an older register file, made before accepted lists
    con.executescript("DROP TABLE accepted_file; DROP TABLE accepted; PRAGMA user_version = 2;")
    con.close()
    before = reg.read_bytes()
    with pytest.raises(ValueError, match="RG-5"):
        register_folder(docs, reg)
    assert reg.read_bytes() == before


def test_rg6_unreadable_subfolder_saves_nothing(tmp_path, monkeypatch):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    scandir = os.scandir

    def denied(path):  # Windows says no to listing letters
        if Path(path).name == "letters":
            raise PermissionError(13, "Access is denied", str(path))
        return scandir(path)

    monkeypatch.setattr(os, "scandir", denied)
    with pytest.raises(PermissionError, match="letters"):
        register_folder(docs, reg)
    assert not reg.exists()


def test_rg6_missing_folder_saves_nothing(tmp_path):
    reg = tmp_path / "register.db"
    with pytest.raises(FileNotFoundError):
        register_folder(tmp_path / "not-there", reg)
    assert not reg.exists()


def progress_file(tmp_path, docs):
    """A real progress file, like the one a stopped Register leaves next to
    its register file, register.db (spec/long-runs.md)."""
    progress = Progress(tmp_path / "register.db", "register", docs.resolve())
    note = docs / "letters" / "note.txt"
    progress.add("letters/note.txt", note.stat().st_size, note.stat().st_mtime_ns, 6,
                 fingerprint(note), None)
    progress.keep()
    return progress.path


def given(command, docs, register_file):
    """Run one command with this register file, as the window does. Also
    gives back what the counter was told: anything means the folder was
    read."""
    told = []

    def counter(done, total):
        told.append((done, total))

    if command == "overview":
        code, words = run_overview(str(register_file))
    elif command == "accept":
        code, words, _ = changes_to_accept(str(docs), str(register_file), counter)
    else:
        code, words = run(command, str(docs), str(register_file), counter)
    return code, words, told


@pytest.mark.parametrize("command", EVERY_COMMAND)
def test_rg7_every_command_refuses_a_progress_file(tmp_path, command):
    docs = make_docs(tmp_path)
    progress = progress_file(tmp_path, docs)
    before = progress.read_bytes()
    assert given(command, docs, progress) == (
        1, f"Problem: {progress.resolve()} is a progress file, not a register file (RG-7)."
           f" Choose {(tmp_path / 'register.db').resolve()} instead.", [])
    assert progress.read_bytes() == before


def test_rg7_the_progress_file_changed_in_the_try_out_is_refused_too(tmp_path):
    docs = make_docs(tmp_path)
    progress = progress_file(tmp_path, docs)
    con = sqlite3.connect(progress)
    for step in STEPS[1:]:  # what happened to it in thread 14's try-out
        con.executescript(step.read_text(encoding="utf-8"))
    con.close()
    before = progress.read_bytes()
    code, words = run("register", str(docs), str(progress))
    assert code == 1
    assert words.startswith(f"Problem: {progress.resolve()} is a progress file")
    assert progress.read_bytes() == before


def test_rg7_the_register_file_to_choose_has_every_progress_ending_taken_off(tmp_path):
    docs = make_docs(tmp_path)
    twice = tmp_path / "register.db.progress.progress"  # as the try-out made one
    shutil.copy(progress_file(tmp_path, docs), twice)
    code, words = run("check", str(docs), str(twice))
    assert words.endswith(f" Choose {(tmp_path / 'register.db').resolve()} instead.")


@pytest.mark.parametrize("command", EVERY_COMMAND)
def test_rg7_a_file_that_isnt_sqlite_is_refused(tmp_path, command):
    docs = make_docs(tmp_path)
    letter = tmp_path / "letter.docx"
    letter.write_bytes(b"a fake letter, not a register file\n" * 10)
    assert given(command, docs, letter) == (
        1, f"Problem: {letter.resolve()} isn't a register file (RG-7)", [])
    assert letter.read_bytes() == b"a fake letter, not a register file\n" * 10


@pytest.mark.parametrize("command", EVERY_COMMAND)
def test_rg7_another_programs_database_is_refused(tmp_path, command):
    docs = make_docs(tmp_path)
    contacts = tmp_path / "contacts.db"
    con = sqlite3.connect(contacts)
    con.execute("CREATE TABLE contact (name TEXT)")
    con.commit()
    con.close()
    before = contacts.read_bytes()
    assert given(command, docs, contacts) == (
        1, f"Problem: {contacts.resolve()} isn't a register file (RG-7)", [])
    assert contacts.read_bytes() == before  # no register tables were added to it


def test_rg7_an_empty_file_is_made_into_a_register_file_by_register(tmp_path):
    docs = make_docs(tmp_path)
    empty = tmp_path / "register.db"
    empty.write_bytes(b"")
    assert run("check", str(docs), str(empty)) == (
        1, f"Problem: {empty.resolve()} isn't a register file (RG-7)")
    assert empty.read_bytes() == b""
    assert run("register", str(docs), str(empty))[0] == 0
    assert query(empty, "PRAGMA user_version") == [(5,)]


def test_rg7_bringing_a_file_up_to_date_never_changes_one_that_isnt_a_register_file(tmp_path):
    """The last safety net: the step every saving command takes first."""
    progress = progress_file(tmp_path, make_docs(tmp_path))
    before = progress.read_bytes()
    con = sqlite3.connect(progress)
    try:
        with pytest.raises(ValueError, match=r"is a progress file, not a register file \(RG-7\)"):
            prepare_register(con)
    finally:
        con.close()
    assert progress.read_bytes() == before


def test_rg7_each_steps_tables_are_the_ones_its_script_makes():
    for step, tables in zip(STEPS, STEP_TABLES, strict=True):
        assert set(re.findall(r"CREATE TABLE (\w+)", step.read_text(encoding="utf-8"))) == tables
