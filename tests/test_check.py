"""Tests for the check rules in spec/check.md (CK-1 to CK-8)."""

import pytest

from document_manager.check import CheckResult, check_folder
from document_manager.register import register_folder


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


def test_ck1_nothing_changed(tmp_path):
    docs, reg = registered_docs(tmp_path)
    assert check_folder(docs, reg) == CheckResult(
        changed=[], new=[], missing=[], unchanged=3
    )


def test_ck2_changed_file(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "letters" / "note.txt").write_bytes(b"hallo\n")
    assert check_folder(docs, reg) == CheckResult(
        changed=["letters/note.txt"], new=[], missing=[], unchanged=2
    )


def test_ck3_missing_file(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "report.docx").unlink()
    assert check_folder(docs, reg) == CheckResult(
        changed=[], new=[], missing=["report.docx"], unchanged=2
    )


def test_ck4_new_file(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "letters" / "new.txt").write_bytes(b"new")
    assert check_folder(docs, reg) == CheckResult(
        changed=[], new=["letters/new.txt"], missing=[], unchanged=3
    )


def test_ck5_moved_file_is_missing_and_new(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "report.docx").rename(docs / "letters" / "report.docx")
    assert check_folder(docs, reg) == CheckResult(
        changed=[], new=["letters/report.docx"], missing=["report.docx"], unchanged=2
    )


def test_ck6_only_reads(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "empty.txt").write_bytes(b"changed")

    def snapshot():
        files = [p for p in tmp_path.rglob("*") if p.is_file()]
        return {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}

    before = snapshot()
    check_folder(docs, reg)
    assert snapshot() == before


def test_ck7_unregistered_folder_is_refused(tmp_path):
    _, reg = registered_docs(tmp_path)
    other = tmp_path / "other"
    other.mkdir()
    with pytest.raises(ValueError, match="CK-7"):
        check_folder(other, reg)


def test_ck8_unreadable_file_stops_the_check(tmp_path, monkeypatch):
    docs, reg = registered_docs(tmp_path)

    def cannot_read(path):
        raise PermissionError(f"can't read {path}")

    monkeypatch.setattr("document_manager.check.fingerprint", cannot_read)
    with pytest.raises(PermissionError, match="empty.txt"):
        check_folder(docs, reg)


def test_ck8_missing_register_file(tmp_path):
    docs, _ = registered_docs(tmp_path)
    with pytest.raises(FileNotFoundError):
        check_folder(docs, tmp_path / "not-there.db")
    assert not (tmp_path / "not-there.db").exists()
