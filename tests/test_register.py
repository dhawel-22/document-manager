"""Tests for the register rules in spec/register.md (RG-1 to RG-6)."""

import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from document_manager.fingerprint import fingerprint
from document_manager.register import register_folder


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
    assert register_folder(docs, reg) == 3
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


def test_rg6_unreadable_file_saves_nothing(tmp_path, monkeypatch):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"

    def cannot_read(path):
        raise PermissionError(f"can't read {path}")

    monkeypatch.setattr("document_manager.register.fingerprint", cannot_read)
    with pytest.raises(PermissionError, match="empty.txt"):
        register_folder(docs, reg)
    assert not reg.exists()


def test_rg6_missing_folder_saves_nothing(tmp_path):
    reg = tmp_path / "register.db"
    with pytest.raises(FileNotFoundError):
        register_folder(tmp_path / "not-there", reg)
    assert not reg.exists()
