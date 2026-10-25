"""Tests for the accept rules in spec/accept.md (AC-1 to AC-9)."""

import os
import re
import sqlite3
from pathlib import Path

import pytest

from document_manager.accept import accept_folder
from document_manager.check import CheckResult, check_folder
from document_manager.register import register_folder

NOTHING = CheckResult(changed=[], new=[], missing=[], unchanged=3)


def registered_docs(tmp_path):
    """A small folder of fake documents, already registered."""
    docs = tmp_path / "docs"
    (docs / "letters").mkdir(parents=True)
    (docs / "letters" / "note.txt").write_bytes(b"hello\n")
    (docs / "report.docx").write_bytes(b"fake report")
    (docs / "empty.txt").write_bytes(b"")
    reg = tmp_path / "register.db"
    register_folder(docs, reg)
    return docs, reg


def query(register_file, sql):
    con = sqlite3.connect(register_file)
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


def test_ac1_folder_changed_since_shown_saves_nothing(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "letters" / "note.txt").write_bytes(b"hallo\n")
    shown = check_folder(docs, reg)
    (docs / "report.docx").write_bytes(b"changed after it was shown")
    before = reg.read_bytes()
    with pytest.raises(ValueError, match="AC-1"):
        accept_folder(docs, reg, shown)
    assert reg.read_bytes() == before


def test_ac2_saves_a_new_list_with_the_time(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "letters" / "note.txt").write_bytes(b"hallo\n")
    assert accept_folder(docs, reg, check_folder(docs, reg)).count == 3
    [(accepted_at,)] = query(reg, "SELECT accepted_at FROM accepted")
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+00:00", accepted_at)
    assert sorted(query(reg, "SELECT path, size FROM accepted_file")) == [
        ("empty.txt", 0), ("letters/note.txt", 6), ("report.docx", 11)]
    assert check_folder(docs, reg) == NOTHING


def test_ac3_old_lists_are_kept(tmp_path):
    docs, reg = registered_docs(tmp_path)
    first = query(reg, "SELECT * FROM file")
    (docs / "letters" / "note.txt").write_bytes(b"hallo\n")
    accept_folder(docs, reg, check_folder(docs, reg))
    accepted_once = query(reg, "SELECT * FROM accepted_file")
    (docs / "empty.txt").write_bytes(b"now full")
    accept_folder(docs, reg, check_folder(docs, reg))
    assert query(reg, "SELECT * FROM file") == first
    assert query(reg, "SELECT * FROM accepted_file WHERE accepted_id = 1") == accepted_once
    assert len(query(reg, "SELECT * FROM accepted")) == 2


def test_ac4_check_uses_the_newest_list(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "letters" / "note.txt").write_bytes(b"hallo\n")
    accept_folder(docs, reg, check_folder(docs, reg))
    (docs / "empty.txt").write_bytes(b"now full")
    assert check_folder(docs, reg) == CheckResult(
        changed=["empty.txt"], new=[], missing=[], unchanged=2
    )


def test_ac5_takes_the_whole_folder(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "letters" / "note.txt").write_bytes(b"hallo\n")
    (docs / "letters" / "new.txt").write_bytes(b"new")
    (docs / "report.docx").unlink()
    shown = check_folder(docs, reg)
    assert shown == CheckResult(
        changed=["letters/note.txt"], new=["letters/new.txt"], missing=["report.docx"],
        unchanged=1,
    )
    assert accept_folder(docs, reg, shown).count == 3
    assert check_folder(docs, reg) == NOTHING


def test_ac6_nothing_changed_saves_nothing(tmp_path):
    docs, reg = registered_docs(tmp_path)
    before = reg.read_bytes()
    with pytest.raises(ValueError, match="AC-6"):
        accept_folder(docs, reg, check_folder(docs, reg))
    assert reg.read_bytes() == before


def test_ac7_only_reads_the_files(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "empty.txt").write_bytes(b"changed")

    def snapshot():
        files = [p for p in docs.rglob("*") if p.is_file()]
        return {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}

    before = snapshot()
    accept_folder(docs, reg, check_folder(docs, reg))
    assert snapshot() == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ["docs", "register.db"]


def test_ac8_unregistered_folder_is_refused(tmp_path):
    _, reg = registered_docs(tmp_path)
    other = tmp_path / "other"
    other.mkdir()
    (other / "a.txt").write_bytes(b"a")
    shown = CheckResult(changed=[], new=["a.txt"], missing=[], unchanged=0)
    with pytest.raises(ValueError, match="not in the register file"):
        accept_folder(other, reg, shown)


def test_ac9_unreadable_subfolder_saves_nothing(tmp_path, monkeypatch):
    docs, reg = registered_docs(tmp_path)
    (docs / "empty.txt").write_bytes(b"changed")
    shown = check_folder(docs, reg)
    before = reg.read_bytes()
    scandir = os.scandir

    def denied(path):  # Windows says no to listing letters
        if Path(path).name == "letters":
            raise PermissionError(13, "Access is denied", str(path))
        return scandir(path)

    monkeypatch.setattr(os, "scandir", denied)
    with pytest.raises(PermissionError, match="letters"):
        accept_folder(docs, reg, shown)
    assert reg.read_bytes() == before


def test_accepting_brings_an_older_register_file_up_to_date(tmp_path):
    docs, reg = registered_docs(tmp_path)
    con = sqlite3.connect(reg)
    con.executescript("DROP TABLE unread; DROP TABLE accepted_file; DROP TABLE accepted;"
                      " PRAGMA user_version = 2;")
    con.close()
    assert check_folder(docs, reg) == NOTHING  # a version 2 file is read as it is
    (docs / "empty.txt").write_bytes(b"changed")
    accept_folder(docs, reg, check_folder(docs, reg))
    assert query(reg, "PRAGMA user_version") == [(4,)]
    assert check_folder(docs, reg) == NOTHING
