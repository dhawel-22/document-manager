"""Tests for summarizing a folder, spec/summaries.md (SM-1, SM-2, SM-4 to SM-7,
SM-9), and for bringing older register files up to date.

Every Word document here is a fake, made by the test in a temporary folder.
"""

import socket
import sqlite3
from datetime import datetime, timedelta, timezone

import docx
import pytest

from document_manager.check import CheckResult, check_folder
from document_manager.fingerprint import fingerprint
from document_manager.register import register_folder
from document_manager.summaries import SummarizeResult, summarize_folder

OLD_FORMAT = bytes.fromhex("D0CF11E0A1B11AE1") + bytes(504)
OLD_REASON = "old Word file (.doc); save it as .docx in Word first"


def fake_docx(path, title, text):
    """A fake Word document with a title and one paragraph."""
    made = docx.Document()
    made.core_properties.title = title
    made.add_paragraph(text)
    made.save(path)


def registered_docs(tmp_path):
    """A small folder of fake documents, already registered."""
    docs = tmp_path / "docs"
    (docs / "letters").mkdir(parents=True)
    fake_docx(docs / "report.docx", "Report", "Markets were calm.")
    fake_docx(docs / "letters" / "note.docx", "Note", "Dear Ernie.")
    (docs / "notes.txt").write_bytes(b"not a Word document\n")
    (docs / "old.doc").write_bytes(OLD_FORMAT)
    reg = tmp_path / "register.db"
    register_folder(docs, reg)
    return docs, reg


def query(register_file, sql):
    con = sqlite3.connect(register_file)
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


def as_version_1(register_file):
    """Turn a register file back into version 1, as made before summaries."""
    con = sqlite3.connect(register_file)
    try:
        con.executescript("DROP TABLE summary; PRAGMA user_version = 1;")
    finally:
        con.close()


def test_sm1_finds_every_word_document(tmp_path):
    docs, reg = registered_docs(tmp_path)
    assert summarize_folder(docs, reg) == SummarizeResult(
        summarized=["letters/note.docx", "report.docx"],
        unchanged=0,
        could_not_read=[("old.doc", OLD_REASON)],
    )


def test_sm2_saves_place_fingerprint_summary_method_and_time(tmp_path):
    docs, reg = registered_docs(tmp_path)
    summarize_folder(docs, reg)
    assert query(reg, "SELECT path, fingerprint, method, title, headings,"
                      " first_words, word_count, problem FROM summary ORDER BY path") == [
        ("letters/note.docx", fingerprint(docs / "letters" / "note.docx"), "stage-a",
         "Note", "[]", "Dear Ernie.", 2, None),
        ("old.doc", fingerprint(docs / "old.doc"), "stage-a",
         None, None, None, None, OLD_REASON),
        ("report.docx", fingerprint(docs / "report.docx"), "stage-a",
         "Report", "[]", "Markets were calm.", 3, None),
    ]
    for (when,) in query(reg, "SELECT made_at FROM summary"):
        age = datetime.now(timezone.utc) - datetime.fromisoformat(when)
        assert timedelta(0) <= age < timedelta(minutes=1)


def test_sm4_unchanged_documents_are_skipped(tmp_path):
    docs, reg = registered_docs(tmp_path)
    summarize_folder(docs, reg)
    before = query(reg, "SELECT * FROM summary")
    assert summarize_folder(docs, reg) == SummarizeResult(
        summarized=[], unchanged=2, could_not_read=[("old.doc", OLD_REASON)]
    )
    assert query(reg, "SELECT * FROM summary") == before


def test_sm4_changed_document_gets_a_new_summary_and_keeps_the_old(tmp_path):
    docs, reg = registered_docs(tmp_path)
    summarize_folder(docs, reg)
    fake_docx(docs / "report.docx", "Report", "Markets fell sharply today.")
    assert summarize_folder(docs, reg) == SummarizeResult(
        summarized=["report.docx"], unchanged=1, could_not_read=[("old.doc", OLD_REASON)]
    )
    assert query(reg, "SELECT first_words FROM summary"
                      " WHERE path = 'report.docx' ORDER BY id") == [
        ("Markets were calm.",),
        ("Markets fell sharply today.",),
    ]


def test_sm5_only_reads_the_documents(tmp_path):
    docs, reg = registered_docs(tmp_path)

    def snapshot():
        files = [p for p in docs.rglob("*") if p.is_file()]
        return {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}

    before = snapshot()
    summarize_folder(docs, reg)
    assert snapshot() == before


def test_sm6_unreadable_document_is_listed_and_saved_once(tmp_path, monkeypatch):
    docs, reg = registered_docs(tmp_path)

    def cannot_read(path):
        if path.name == "report.docx":
            raise PermissionError(f"can't read {path}")
        return fingerprint(path)

    monkeypatch.setattr("document_manager.summaries.fingerprint", cannot_read)
    result = summarize_folder(docs, reg)
    assert result.summarized == ["letters/note.docx"]
    assert result.could_not_read[0] == ("old.doc", OLD_REASON)
    place, reason = result.could_not_read[1]
    assert place == "report.docx" and reason.startswith("PermissionError: can't read")
    saved = query(reg, "SELECT COUNT(*) FROM summary")
    summarize_folder(docs, reg)  # the same problem again: nothing new is saved
    assert query(reg, "SELECT COUNT(*) FROM summary") == saved


def test_sm7_unregistered_folder_is_refused(tmp_path):
    _, reg = registered_docs(tmp_path)
    other = tmp_path / "other"
    other.mkdir()
    with pytest.raises(ValueError, match="SM-7"):
        summarize_folder(other, reg)


def test_sm7_missing_register_file_is_not_made(tmp_path):
    docs, _ = registered_docs(tmp_path)
    with pytest.raises(FileNotFoundError):
        summarize_folder(docs, tmp_path / "not-there.db")
    assert not (tmp_path / "not-there.db").exists()


def test_sm9_nothing_is_sent(tmp_path, monkeypatch):
    docs, reg = registered_docs(tmp_path)

    def no_network(*args, **kwargs):
        raise AssertionError("tried to use the network")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)
    assert summarize_folder(docs, reg).summarized == ["letters/note.docx", "report.docx"]


def test_new_register_files_are_version_2(tmp_path):
    _, reg = registered_docs(tmp_path)
    assert query(reg, "PRAGMA user_version") == [(2,)]


def test_version_1_register_file_is_brought_up_to_date(tmp_path):
    docs, reg = registered_docs(tmp_path)
    as_version_1(reg)
    summarize_folder(docs, reg)
    assert query(reg, "PRAGMA user_version") == [(2,)]
    assert len(query(reg, "SELECT * FROM summary")) == 3
    assert len(query(reg, "SELECT * FROM file")) == 4


def test_check_reads_a_version_1_register_file_as_it_is(tmp_path):
    docs, reg = registered_docs(tmp_path)
    as_version_1(reg)
    assert check_folder(docs, reg) == CheckResult(changed=[], new=[], missing=[], unchanged=4)
    assert query(reg, "PRAGMA user_version") == [(1,)]


def test_unknown_register_file_version_is_refused(tmp_path):
    docs, reg = registered_docs(tmp_path)
    con = sqlite3.connect(reg)
    con.execute("PRAGMA user_version = 3")
    con.close()
    with pytest.raises(ValueError, match="Unknown register file version: 3"):
        summarize_folder(docs, reg)
