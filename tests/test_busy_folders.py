"""Tests for busy folders, spec/busy-folders.md (BF-1 to BF-9, BF-11):
Register, Check, Accept and Summarize carry on past a file that's deleted,
renamed, locked or changing. The overview (BF-10) is tested with the overview.

Every folder here is fake, made by the test in a temporary folder. A file is
held open with Windows' own lock, the way Outlook holds its mail files, so
the tests see what Windows really does. A counter, the window's way of
following a run (WN-13), changes the folder at the right moment.
"""

import ctypes
import msvcrt
import os
import shutil
import sqlite3
import subprocess
import sys
from contextlib import contextmanager
from ctypes import wintypes
from pathlib import Path

import docx
import pytest

from document_manager.__main__ import main
from document_manager.accept import accept_folder
from document_manager.check import CheckResult, check_folder
from document_manager.commands import accept, changes_to_accept, run
from document_manager.fingerprint import fingerprint, fingerprint_of
from document_manager.register import CHANGED, IN_USE, read_file, register_folder
from document_manager.summaries import SummarizeResult, summarize_folder
from document_manager.word import CouldNotRead

PROJECT = Path(__file__).resolve().parent.parent
MAIL = "mail/archive.pst"
# The fake folder has one file at the top and one in each of its two
# subfolders. A counter is told 1, 2 and 3 files found, then 0 to 3 read.
TOP_LISTED = (1, None)  # the top folder is listed; its subfolders aren't yet
ALL_FOUND = (0, 3)  # every file is found; none is read yet

# Windows' own way to open a file, so a test can hold one open with no
# sharing.
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.CreateFileW.restype = wintypes.HANDLE
kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                 wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD,
                                 wintypes.HANDLE]
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
GENERIC_READ, OPEN_EXISTING = 0x80000000, 3
INVALID_HANDLE = wintypes.HANDLE(-1).value


@contextmanager
def held_open(path):
    """Hold a file open with no sharing, the way Outlook holds its mail
    files: no other program can read it until it's let go."""
    handle = kernel32.CreateFileW(str(path), GENERIC_READ, 0, None, OPEN_EXISTING, 0, None)
    assert handle != INVALID_HANDLE, f"Windows error {ctypes.get_last_error()}"
    try:
        yield
    finally:
        kernel32.CloseHandle(handle)


@contextmanager
def part_locked(path):
    """Lock a file's bytes, the way a database locks its records: the file
    opens, but reading it fails."""
    size = path.stat().st_size
    with open(path, "r+b") as holder:
        msvcrt.locking(holder.fileno(), msvcrt.LK_NBLCK, size)
        try:
            yield
        finally:
            holder.seek(0)
            msvcrt.locking(holder.fileno(), msvcrt.LK_UNLCK, size)


def make_docs(tmp_path):
    """A small folder of fake files, with a mail file to hold open."""
    docs = tmp_path / "docs"
    (docs / "letters").mkdir(parents=True)
    (docs / "mail").mkdir()
    (docs / "letters" / "note.txt").write_bytes(b"hello\n")  # 6 bytes
    (docs / MAIL).write_bytes(b"fake mail")  # 9 bytes
    (docs / "report.docx").write_bytes(b"fake report")  # 11 bytes
    return docs


def registered_docs(tmp_path):
    """The same folder, already registered."""
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    register_folder(docs, reg)
    return docs, reg


def query(register_file, sql):
    con = sqlite3.connect(register_file)
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


def when(moment, then):
    """A counter that does then() the first time it's told this moment."""
    fired = []

    def counter(done, total):
        if (done, total) == moment and not fired:
            fired.append(moment)
            then()

    return counter


def places(files):
    """The places of the files that were read."""
    return [place for place, _size, _fp in files.read]


def denied(monkeypatch, name):
    """Windows says no to listing the subfolder with this name."""
    scandir = os.scandir

    def stand_in(path):
        if Path(path).name == name:
            raise PermissionError(13, "Access is denied", str(path))
        return scandir(path)

    monkeypatch.setattr(os, "scandir", stand_in)


def word_docs(tmp_path):
    """A folder of two fake Word documents, already registered."""
    docs = tmp_path / "docs"
    docs.mkdir()
    for name in ("a.docx", "b.docx"):
        made = docx.Document()
        made.add_paragraph("A fake document for the tests.")
        made.save(docs / name)
    reg = tmp_path / "register.db"
    register_folder(docs, reg)
    return docs, reg


def problem_line(folder):
    """What a run says when the folder can't be reached any more (BF-4)."""
    return f"Problem: {folder} can't be reached any more. Nothing was saved (BF-4)"


def test_bf1_a_file_held_open_is_listed_as_could_not_read(tmp_path):
    docs = make_docs(tmp_path)
    with held_open(docs / MAIL):
        files = register_folder(docs, tmp_path / "register.db")
    assert files.unread == [(MAIL, 9, IN_USE)]
    assert places(files) == ["letters/note.txt", "report.docx"]


def test_bf1_check_carries_on_past_a_file_held_open(tmp_path):
    docs, reg = registered_docs(tmp_path)
    with held_open(docs / MAIL):
        assert check_folder(docs, reg) == CheckResult(
            changed=[], new=[], missing=[], unchanged=2, could_not_read=[(MAIL, IN_USE)])


def test_bf1_a_file_with_a_locked_part_is_listed_as_could_not_read(tmp_path):
    docs, reg = registered_docs(tmp_path)
    with part_locked(docs / "report.docx"):
        assert check_folder(docs, reg).could_not_read == [("report.docx", IN_USE)]


def test_bf1_any_other_reason_is_word_for_word_without_the_path(tmp_path, monkeypatch):
    docs = make_docs(tmp_path)

    def fault(path):
        if path.name == "report.docx":
            raise OSError(22, "Invalid argument", str(path))
        return read_file(path)

    monkeypatch.setattr("document_manager.register.read_file", fault)
    files = register_folder(docs, tmp_path / "register.db")
    assert files.unread == [("report.docx", 11, "OSError: Invalid argument")]


def grows(f):
    """Read a file while another program adds to note.txt."""
    if Path(f.name).name == "note.txt":
        with open(f.name, "ab") as writer:
            writer.write(b"more\n")
    return fingerprint_of(f)


def test_bf2_a_file_that_grows_while_it_is_read(tmp_path, monkeypatch):
    docs, reg = registered_docs(tmp_path)
    monkeypatch.setattr("document_manager.register.fingerprint_of", grows)
    assert check_folder(docs, reg) == CheckResult(
        changed=[], new=[], missing=[], unchanged=2,
        could_not_read=[("letters/note.txt", CHANGED)])


def test_bf2_register_keeps_its_size_just_after_it_was_read(tmp_path, monkeypatch):
    docs = make_docs(tmp_path)
    monkeypatch.setattr("document_manager.register.fingerprint_of", grows)
    files = register_folder(docs, tmp_path / "register.db")
    assert files.unread == [("letters/note.txt", 11, CHANGED)]


def test_bf2_a_file_rewritten_with_the_same_size_while_it_is_read(tmp_path, monkeypatch):
    docs, reg = registered_docs(tmp_path)

    def rewritten(f):
        if Path(f.name).name == "note.txt":
            with open(f.name, "r+b") as writer:  # other bytes, the same number of them
                writer.write(b"HELLO\n")
        return fingerprint_of(f)

    monkeypatch.setattr("document_manager.register.fingerprint_of", rewritten)
    assert check_folder(docs, reg).could_not_read == [("letters/note.txt", CHANGED)]


def test_bf3_a_file_deleted_after_it_was_found_is_left_out(tmp_path):
    docs = make_docs(tmp_path)
    deletes = when(ALL_FOUND, (docs / "report.docx").unlink)
    files = register_folder(docs, tmp_path / "register.db", deletes)
    assert files.unread == []
    assert places(files) == ["letters/note.txt", MAIL]


def test_bf3_check_shows_a_file_deleted_while_it_ran_as_missing(tmp_path):
    docs, reg = registered_docs(tmp_path)
    deletes = when(ALL_FOUND, (docs / "report.docx").unlink)
    assert check_folder(docs, reg, deletes) == CheckResult(
        changed=[], new=[], missing=["report.docx"], unchanged=2)


def test_bf3_a_file_renamed_while_it_ran_is_missing_at_its_old_place(tmp_path):
    docs, reg = registered_docs(tmp_path)
    # letters was already listed, so the new place isn't found in this run.
    renames = when(ALL_FOUND, lambda: (docs / "report.docx").rename(docs / "letters" / "r.docx"))
    assert check_folder(docs, reg, renames) == CheckResult(
        changed=[], new=[], missing=["report.docx"], unchanged=2)


def test_bf3_a_subfolder_deleted_while_files_are_found_is_passed_over(tmp_path):
    docs, reg = registered_docs(tmp_path)
    deletes = when(TOP_LISTED, lambda: shutil.rmtree(docs / "mail"))
    assert check_folder(docs, reg, deletes) == CheckResult(
        changed=[], new=[], missing=[MAIL], unchanged=2)


def test_bf3_summarize_leaves_out_a_document_gone_when_its_turn_comes(tmp_path):
    docs, reg = word_docs(tmp_path)
    deletes = when((0, 2), (docs / "b.docx").unlink)
    assert summarize_folder(docs, reg, deletes) == SummarizeResult(
        summarized=["a.docx"], unchanged=0, could_not_read=[])
    assert query(reg, "SELECT path FROM summary") == [("a.docx",)]


def test_bf3_summarize_leaves_out_a_document_gone_while_it_was_read(tmp_path, monkeypatch):
    docs, reg = word_docs(tmp_path)

    def vanishes(path):
        path.unlink()
        raise CouldNotRead("FileNotFoundError: a fake fault")

    monkeypatch.setattr("document_manager.summaries.summarize_document", vanishes)
    assert summarize_folder(docs, reg) == SummarizeResult(
        summarized=[], unchanged=0, could_not_read=[])
    assert query(reg, "SELECT path FROM summary") == []


@pytest.mark.parametrize("moment", [TOP_LISTED, ALL_FOUND])
def test_bf4_a_folder_that_cant_be_reached_stops_register(tmp_path, moment):
    docs = make_docs(tmp_path)
    folder = docs.resolve()
    reg = tmp_path / "register.db"
    drops = when(moment, lambda: docs.rename(tmp_path / "elsewhere"))  # like a drive that drops
    assert run("register", str(docs), str(reg), drops) == (1, problem_line(folder))
    assert not reg.exists()


@pytest.mark.parametrize("command, moment", [
    ("check", TOP_LISTED), ("check", ALL_FOUND),
    ("summarize", TOP_LISTED), ("summarize", (0, 1)),  # report.docx is its one Word document
])
def test_bf4_a_folder_that_cant_be_reached_stops_check_and_summarize(tmp_path, command, moment):
    docs, reg = registered_docs(tmp_path)
    folder = docs.resolve()
    before = reg.read_bytes()
    drops = when(moment, lambda: docs.rename(tmp_path / "elsewhere"))
    assert run(command, str(docs), str(reg), drops) == (1, problem_line(folder))
    assert reg.read_bytes() == before


def test_bf4_a_folder_that_cant_be_reached_stops_accept(tmp_path):
    docs, reg = registered_docs(tmp_path)
    folder = docs.resolve()
    (docs / "report.docx").write_bytes(b"changed report")
    _, _, shown = changes_to_accept(str(docs), str(reg))
    before = reg.read_bytes()
    drops = when(ALL_FOUND, lambda: docs.rename(tmp_path / "elsewhere"))
    assert accept(str(docs), str(reg), shown, drops) == (1, problem_line(folder))
    assert reg.read_bytes() == before


def test_bf5_a_subfolder_that_cant_be_read_still_stops_summarize(tmp_path, monkeypatch):
    docs, reg = registered_docs(tmp_path)
    before = reg.read_bytes()
    denied(monkeypatch, "letters")
    code, words = run("summarize", str(docs), str(reg))
    assert code == 1 and words.startswith("Problem: ") and "letters" in words
    assert reg.read_bytes() == before


def test_bf6_register_keeps_a_file_that_couldnt_be_read_on_the_list(tmp_path):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    with held_open(docs / MAIL):
        register_folder(docs, reg)
    assert query(reg, "SELECT path FROM file ORDER BY path") == [
        ("letters/note.txt",), ("report.docx",)]
    assert query(reg, "SELECT folder_id, accepted_id, path, size, reason FROM unread") == [
        (1, None, MAIL, 9, IN_USE)]


def test_bf6_accept_keeps_one_too_and_the_older_list_keeps_its_fingerprint(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "report.docx").write_bytes(b"changed report")
    with held_open(docs / MAIL):
        accept_folder(docs, reg, check_folder(docs, reg))
    assert query(reg, "SELECT path FROM accepted_file ORDER BY path") == [
        ("letters/note.txt",), ("report.docx",)]
    assert query(reg, "SELECT folder_id, accepted_id, path, size, reason FROM unread") == [
        (1, 1, MAIL, 9, IN_USE)]
    assert query(reg, f"SELECT fingerprint FROM file WHERE path = '{MAIL}'") == [
        (fingerprint(docs / MAIL),)]


def test_bf6_a_size_windows_doesnt_give_is_saved_as_unknown(tmp_path, monkeypatch):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    monkeypatch.setattr("document_manager.register.size_of", lambda path: None)
    with held_open(docs / MAIL):
        register_folder(docs, reg)
    assert query(reg, "SELECT path, size FROM unread") == [(MAIL, None)]


def test_bf7_a_new_file_that_cant_be_read_is_only_couldnt_read(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "mail" / "new.pst").write_bytes(b"new mail")
    with held_open(docs / "mail" / "new.pst"):
        assert check_folder(docs, reg) == CheckResult(
            changed=[], new=[], missing=[], unchanged=3,
            could_not_read=[("mail/new.pst", IN_USE)])


def test_bf7_a_file_listed_without_a_fingerprint_is_new_once_it_can_be_read(tmp_path):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    with held_open(docs / MAIL):
        register_folder(docs, reg)
    shown = check_folder(docs, reg)
    assert shown == CheckResult(changed=[], new=[MAIL], missing=[], unchanged=2)
    accept_folder(docs, reg, shown)  # accepting gives it a fingerprint
    assert check_folder(docs, reg) == CheckResult(changed=[], new=[], missing=[], unchanged=3)


def test_bf7_a_file_listed_without_a_fingerprint_that_is_gone_is_missing(tmp_path):
    docs = make_docs(tmp_path)
    reg = tmp_path / "register.db"
    with held_open(docs / MAIL):
        register_folder(docs, reg)
    (docs / MAIL).unlink()
    assert check_folder(docs, reg) == CheckResult(
        changed=[], new=[], missing=[MAIL], unchanged=2)


def test_bf7_the_same_for_a_file_an_accepted_list_has_without_a_fingerprint(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "report.docx").write_bytes(b"changed report")
    with held_open(docs / MAIL):
        accept_folder(docs, reg, check_folder(docs, reg))
    (docs / MAIL).unlink()
    assert check_folder(docs, reg) == CheckResult(
        changed=[], new=[], missing=[MAIL], unchanged=2)


def test_bf8_check_never_says_nothing_has_changed_if_a_file_couldnt_be_read(tmp_path, capsys):
    docs, reg = registered_docs(tmp_path)
    with held_open(docs / MAIL):
        assert main(["check", str(docs), str(reg)]) == 0
    assert capsys.readouterr().out == (
        "Changed: 0, new: 0, missing: 0, unchanged: 2, couldn't read: 1.\n"
        f"  couldn't read  {MAIL}  {IN_USE}\n"
    )


def test_bf8_register_says_which_files_couldnt_be_read(tmp_path, capsys):
    docs = make_docs(tmp_path)
    with held_open(docs / MAIL):
        assert main(["register", str(docs), str(tmp_path / "register.db")]) == 0
    assert capsys.readouterr().out == (
        f"Registered {docs}. Files listed: 3, couldn't read: 1.\n"
        f"  couldn't read  {MAIL}  {IN_USE}\n"
    )


def test_bf8_accept_says_which_files_couldnt_be_read(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "report.docx").write_bytes(b"changed report")
    with held_open(docs / MAIL):
        code, words, shown = changes_to_accept(str(docs), str(reg))
        assert (code, words) == (0, (
            "Changed: 1, new: 0, missing: 0, unchanged: 1, couldn't read: 1.\n"
            "  changed  report.docx\n"
            f"  couldn't read  {MAIL}  {IN_USE}"
        ))
        assert accept(str(docs), str(reg), shown) == (0, (
            f"Accepted {docs}. Files listed: 3, couldn't read: 1.\n"
            f"  couldn't read  {MAIL}  {IN_USE}"
        ))


def test_the_example_in_the_spec_is_exactly_what_check_shows(tmp_path, capsys):
    spec = (PROJECT / "spec" / "busy-folders.md").read_text(encoding="utf-8")
    example = spec.split("Example report, on fake files:\n\n", 1)[1].split("\n\n", 1)[0]
    expected = "".join(f"{line.removeprefix('    ')}\n" for line in example.splitlines())
    docs = tmp_path / "docs"
    for place in ("letters/note.txt", "letters/old.txt", "letters/plan.txt", MAIL,
                  "photos/beach.jpg", "report.docx"):
        (docs / place).parent.mkdir(parents=True, exist_ok=True)
        (docs / place).write_bytes(place.encode())
    reg = tmp_path / "register.db"
    register_folder(docs, reg)
    (docs / "letters" / "note.txt").write_bytes(b"changed")
    (docs / "letters" / "old.txt").unlink()
    with held_open(docs / MAIL):
        assert main(["check", str(docs), str(reg)]) == 0
    assert capsys.readouterr().out == expected


def test_bf9_files_that_couldnt_be_read_arent_changes(tmp_path):
    docs, reg = registered_docs(tmp_path)
    before = reg.read_bytes()
    with held_open(docs / MAIL):
        assert changes_to_accept(str(docs), str(reg)) == (0, (
            "Changed: 0, new: 0, missing: 0, unchanged: 2, couldn't read: 1.\n"
            f"  couldn't read  {MAIL}  {IN_USE}\n"
            "Nothing was saved."
        ), None)
        with pytest.raises(ValueError, match="AC-6"):
            accept_folder(docs, reg, check_folder(docs, reg))
    assert reg.read_bytes() == before


def test_bf9_the_accept_command_doesnt_ask(tmp_path):
    docs, reg = registered_docs(tmp_path)
    before = reg.read_bytes()
    with held_open(docs / MAIL):
        done = subprocess.run(
            [sys.executable, "-m", "document_manager", "accept", str(docs), str(reg)],
            cwd=PROJECT, input="yes\n", capture_output=True, text=True,
        )
    assert done.returncode == 0, done.stderr
    assert done.stdout == (
        "Changed: 0, new: 0, missing: 0, unchanged: 2, couldn't read: 1.\n"
        f"  couldn't read  {MAIL}  {IN_USE}\n"
        "Nothing was saved.\n"
    )
    assert reg.read_bytes() == before


def test_a_file_that_can_be_read_after_the_yes_is_a_change_since_it_was_shown(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "report.docx").write_bytes(b"changed report")
    with held_open(docs / MAIL):
        shown = check_folder(docs, reg)
    before = reg.read_bytes()
    with pytest.raises(ValueError, match="AC-1"):
        accept_folder(docs, reg, shown)
    assert reg.read_bytes() == before


def as_version_3(register_file):
    """Turn a register file back into version 3, as made before busy folders."""
    con = sqlite3.connect(register_file)
    try:
        con.executescript("DROP TABLE unread; PRAGMA user_version = 3;")
    finally:
        con.close()


def test_bf11_an_older_register_file_keeps_its_lists_and_summaries(tmp_path):
    docs, reg = registered_docs(tmp_path)
    (docs / "report.docx").write_bytes(b"changed report")
    accept_folder(docs, reg, check_folder(docs, reg))
    summarize_folder(docs, reg)  # report.docx is a fake, so it's saved as couldn't read
    as_version_3(reg)
    tables = ("folder", "file", "accepted", "accepted_file", "summary")
    old = {table: query(reg, f"SELECT * FROM {table} ORDER BY rowid") for table in tables}
    assert all(old.values())
    other = make_docs(tmp_path / "other")
    with held_open(other / MAIL):
        register_folder(other, reg)
    assert query(reg, "PRAGMA user_version") == [(4,)]
    for table, rows in old.items():
        assert query(reg, f"SELECT * FROM {table} ORDER BY rowid")[:len(rows)] == rows
    assert query(reg, "SELECT path, reason FROM unread") == [(MAIL, IN_USE)]


def test_check_reads_a_version_3_register_file_as_it_is(tmp_path):
    docs, reg = registered_docs(tmp_path)
    as_version_3(reg)
    before = reg.read_bytes()
    assert check_folder(docs, reg) == CheckResult(changed=[], new=[], missing=[], unchanged=3)
    assert reg.read_bytes() == before


def test_a_file_that_couldnt_be_read_is_counted_as_read(tmp_path):
    docs = make_docs(tmp_path)
    told = []
    with held_open(docs / MAIL):
        run("register", str(docs), str(tmp_path / "register.db"),
            lambda done, total: told.append((done, total)))
    assert told == [(1, None), (2, None), (3, None), (0, 3), (1, 3), (2, 3), (3, 3)]
