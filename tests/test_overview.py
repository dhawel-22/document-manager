"""Tests for the overview's engine, spec/overview.md (OV-1 to OV-9, OV-11),
and files that couldn't be read (v1.3, spec/busy-folders.md, BF-10).

Every folder here is fake, made by the test in a temporary folder. The
overview's words and its command (OV-2's first lines, OV-10, OV-12) are
tested with the command.
"""

import sqlite3
from contextlib import contextmanager

import pytest

from document_manager.accept import accept_folder
from document_manager.check import check_folder
from document_manager.overview import (
    BACKUPS, DOCUMENTS, ENDINGS, KIND_OF_ENDING, KINDS, MEDIA, OTHER, PROGRAMS,
    Change, Duplicate, kind_of, overview,
)
from document_manager.register import prepare_register, read_file, register_folder


def make(folder, files):
    """A folder of fake files, from each file's place and contents."""
    for place, contents in files.items():
        path = folder / place
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents)
    return folder


def registered(tmp_path):
    """Two folders of fake files, registered in one register file. If
    capitals counted, Letters would come before archive (OV-3)."""
    letters = make(tmp_path / "Letters", {
        "report.pdf": b"a report",  # 8 bytes
        "letter.docx": b"a letter!",  # 9 bytes
        "notes.txt": b"",  # empty (OV-8)
        "holiday.jpg": b"sunny",  # 5 bytes, and twice more in archive (OV-6)
        "readme": b"read me",  # 7 bytes, no ending
    })
    archive = make(tmp_path / "archive", {
        "holiday.jpg": b"sunny",
        "old/holiday.JPG": b"sunny",
        "backup.zip": b"zipped",  # 6 bytes
        "tools/.git/config": b"[core]",  # 6 bytes, in a program folder (OV-4)
    })
    reg = tmp_path / "register.db"
    register_folder(letters, reg)
    register_folder(archive, reg)
    return letters, archive, reg


def query(register_file, sql):
    con = sqlite3.connect(register_file)
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


@contextmanager
def couldnt_read(monkeypatch, *names):
    """While this holds, Windows says no to reading the files with these
    names, as for a file another program holds open (BF-1)."""

    def stand_in(path):
        if path.name in names:
            raise PermissionError(13, "Permission denied", str(path))
        return read_file(path)

    with monkeypatch.context() as patch:
        patch.setattr("document_manager.register.read_file", stand_in)
        yield


def snapshot(tmp_path):
    """Every file under tmp_path, with its bytes and last-changed time."""
    files = [p for p in tmp_path.rglob("*") if p.is_file()]
    return {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}


def test_ov1_only_reads_the_register_file(tmp_path):
    _, _, reg = registered(tmp_path)
    before = snapshot(tmp_path)
    overview(reg)
    assert snapshot(tmp_path) == before  # nothing changed, and no file was added


def test_ov1_never_opens_the_folders(tmp_path):
    letters, archive, reg = registered(tmp_path)
    before = overview(reg)
    letters.rename(tmp_path / "gone 1")
    archive.rename(tmp_path / "gone 2")
    assert overview(reg) == before


def test_ov2_each_folder_by_its_newest_list(tmp_path):
    letters, _, reg = registered(tmp_path)
    (letters / "readme").unlink()
    (letters / "report.pdf").write_bytes(b"a longer report")  # 15 bytes
    accept_folder(letters, reg, check_folder(letters, reg))
    [(accepted_at,)] = query(reg, "SELECT accepted_at FROM accepted")
    folder = overview(reg).folders[1]
    assert (folder.path, folder.files, folder.size, folder.listed_at) == (
        str(letters), 4, 15 + 9 + 5, accepted_at)


def test_ov3_each_folder_then_the_totals(tmp_path):
    letters, archive, reg = registered(tmp_path)
    registered_at = dict(query(reg, "SELECT path, registered_at FROM folder"))
    result = overview(reg)
    assert [(f.path, f.files, f.size, f.listed_at, f.accepted) for f in result.folders] == [
        (str(archive), 4, 22, registered_at[str(archive)], 0),
        (str(letters), 5, 29, registered_at[str(letters)], 0),
    ]
    assert (result.files, result.size) == (9, 51)


def test_ov4_kinds_by_ending_ignoring_capitals():
    names = ["a.docx", "b.PDF", "c.mp4", "d.zip", "e.py", "f.xyz", "readme", ".gitignore", "g."]
    assert [kind_of(rf"C:\files\{name}") for name in names] == [
        DOCUMENTS, DOCUMENTS, MEDIA, BACKUPS, PROGRAMS, OTHER, OTHER, OTHER, OTHER]


def test_ov4_a_file_in_a_program_folder_is_a_program_file():
    paths = [r"C:\code\.git\config", r"C:\code\Node_Modules\lib\guide.pdf",
             r"C:\code\__pycache__\a.pyc", r"C:\code\.venv\notes.txt",
             r"C:\code\venv\notes.txt", r"C:\code\lib\site-packages\read.md",
             r"C:\code\git\notes.txt"]  # "git" without its dot isn't a program folder
    assert [kind_of(path) for path in paths] == [PROGRAMS] * 6 + [DOCUMENTS]


def test_ov4_each_ending_has_one_kind():
    endings = [ending for kind in ENDINGS.values() for ending in kind.split()]
    assert len(endings) == len(set(endings)) == len(KIND_OF_ENDING)
    assert set(ENDINGS) == set(KINDS) - {OTHER}


def test_ov5_each_folders_files_of_each_kind(tmp_path):
    _, _, reg = registered(tmp_path)
    assert [list(f.kinds.items()) for f in overview(reg).folders] == [
        [(DOCUMENTS, 0), (MEDIA, 2), (PROGRAMS, 1), (BACKUPS, 1), (OTHER, 0)],
        [(DOCUMENTS, 3), (MEDIA, 1), (PROGRAMS, 0), (BACKUPS, 0), (OTHER, 1)],
    ]


def test_ov5_each_kind_in_all_folders(tmp_path):
    _, _, reg = registered(tmp_path)
    result = overview(reg)
    assert list(result.kinds.items()) == [
        (DOCUMENTS, (3, 17)), (MEDIA, (3, 15)), (PROGRAMS, (1, 6)), (BACKUPS, (1, 6)),
        (OTHER, (1, 7)),
    ]
    assert result.other_endings == [("", 1)]


def test_ov5_others_ten_most_common_endings(tmp_path):
    files = {"a.zz": b"a", "b.zz": b"b", "c.ZZ": b"c", "readme": b"d", "licence": b"e"}
    # 11 endings with one file each, named so that the folder lists them in
    # the reverse of the endings' alphabetical order
    files |= {f"{11 - n:02}.e{n:02}": b"x" * n for n in range(1, 12)}
    reg = tmp_path / "register.db"
    register_folder(make(tmp_path / "odd", files), reg)
    assert overview(reg).other_endings == (
        [("zz", 3), ("", 2)] + [(f"e{n:02}", 1) for n in range(1, 9)])


def test_ov6_duplicates_the_most_extra_space_first(tmp_path):
    letters, archive, reg = registered(tmp_path)  # "sunny", 5 bytes, 3 times: 10 extra
    more = make(tmp_path / "more", {
        "twelve.txt": b"twelve bytes", "twelve copy.txt": b"twelve bytes",  # 12 extra
        "C.txt": b"8 bytes!", "x.txt": b"8 bytes!",  # 8 extra
        "b.txt": b"8 bytes?", "Y.txt": b"8 bytes?",  # 8 extra, first: b comes before C
    })
    register_folder(more, reg)
    assert overview(reg).duplicates == [
        Duplicate(12, [str(more / "twelve copy.txt"), str(more / "twelve.txt")]),
        Duplicate(5, [str(archive / "holiday.jpg"), str(archive / "old" / "holiday.JPG"),
                      str(letters / "holiday.jpg")]),
        Duplicate(8, [str(more / "b.txt"), str(more / "Y.txt")]),
        Duplicate(8, [str(more / "C.txt"), str(more / "x.txt")]),
    ]


def test_ov7_the_duplicates_totals(tmp_path):
    _, _, reg = registered(tmp_path)
    result = overview(reg)
    assert (len(result.duplicates), result.extra_copies, result.extra_space) == (1, 2, 10)


def test_ov8_empty_files_are_counted_on_their_own(tmp_path):
    _, _, reg = registered(tmp_path)  # notes.txt is empty
    register_folder(make(tmp_path / "more", {"empty.txt": b"", "empty.log": b""}), reg)
    result = overview(reg)
    assert result.empty_files == 3
    assert [d.size for d in result.duplicates] == [5]  # only "sunny"


def test_ov9_each_accepted_list_against_the_list_before(tmp_path):
    letters, _, reg = registered(tmp_path)
    (letters / "letter.docx").write_bytes(b"a new letter")
    (letters / "plan.xlsx").write_bytes(b"a plan")
    accept_folder(letters, reg, check_folder(letters, reg))
    (letters / "plan.xlsx").write_bytes(b"a better plan")
    (letters / "readme").unlink()
    accept_folder(letters, reg, check_folder(letters, reg))
    first, second = [at for (at,) in query(reg, "SELECT accepted_at FROM accepted ORDER BY id")]
    result = overview(reg)
    assert result.changes == [
        Change(str(letters), first, changed=1, new=1, missing=0),
        Change(str(letters), second, changed=1, new=0, missing=1),
    ]
    assert [f.accepted for f in result.folders] == [0, 2]  # archive has none


def test_bf10_files_that_couldnt_be_read_are_counted_but_never_duplicates(
        tmp_path, monkeypatch):
    letters, archive, reg = registered(tmp_path)  # "sunny" is in three places
    busy = make(tmp_path / "busy", {
        "holiday.jpg": b"sunny",  # a fourth copy, but it can't be read
        "mail.pst": b"fake mail",  # 9 bytes, and it can't be read either
        "notes.txt": b"notes",  # 5 bytes
    })
    with couldnt_read(monkeypatch, "holiday.jpg", "mail.pst"):
        register_folder(busy, reg)
    result = overview(reg)
    [folder] = [folder for folder in result.folders if folder.path == str(busy)]
    assert (folder.files, folder.size, folder.unread) == (3, 19, 2)
    assert list(folder.kinds.values()) == [1, 1, 0, 0, 1]  # each file has its kind
    assert (result.files, result.unread) == (12, 2)
    assert result.duplicates == [
        Duplicate(5, [str(archive / "holiday.jpg"), str(archive / "old" / "holiday.JPG"),
                      str(letters / "holiday.jpg")])]


def test_bf10_a_size_windows_didnt_give_counts_as_none(tmp_path, monkeypatch):
    _, _, reg = registered(tmp_path)
    busy = make(tmp_path / "busy", {"mail.pst": b"fake mail", "notes.txt": b"notes"})
    monkeypatch.setattr("document_manager.register.size_of", lambda path: None)
    with couldnt_read(monkeypatch, "mail.pst"):
        register_folder(busy, reg)
    result = overview(reg)
    [folder] = [folder for folder in result.folders if folder.path == str(busy)]
    assert (folder.files, folder.size, folder.unread) == (2, 5, 1)
    assert result.kinds[OTHER] == (2, 7)  # mail.pst, and readme's 7 bytes in letters


def test_bf10_an_empty_file_that_couldnt_be_read_is_still_empty(tmp_path, monkeypatch):
    _, _, reg = registered(tmp_path)  # notes.txt is empty
    busy = make(tmp_path / "busy", {"lock.tmp": b""})
    with couldnt_read(monkeypatch, "lock.tmp"):
        register_folder(busy, reg)
    result = overview(reg)
    assert (result.empty_files, result.unread) == (2, 1)


def test_bf10_changes_are_counted_the_way_check_counts_them(tmp_path, monkeypatch):
    letters, _, reg = registered(tmp_path)
    (letters / "letter.docx").write_bytes(b"a new letter")
    with couldnt_read(monkeypatch, "report.pdf"):  # neither changed, new nor missing
        accept_folder(letters, reg, check_folder(letters, reg))
    (letters / "readme").unlink()
    accept_folder(letters, reg, check_folder(letters, reg))  # report.pdf is new to the list
    first, second = [at for (at,) in query(reg, "SELECT accepted_at FROM accepted ORDER BY id")]
    assert overview(reg).changes == [
        Change(str(letters), first, changed=1, new=0, missing=0),
        Change(str(letters), second, changed=0, new=1, missing=1),
    ]


def test_ov11_a_missing_register_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        overview(tmp_path / "not-there.db")
    assert not (tmp_path / "not-there.db").exists()


def test_ov11_a_file_that_isnt_a_register_file(tmp_path):
    text = tmp_path / "notes.db"
    text.write_bytes(b"Just some notes, not a register file.\n" * 20)
    with pytest.raises(sqlite3.DatabaseError):
        overview(text)
    empty = tmp_path / "empty.db"
    empty.write_bytes(b"")
    with pytest.raises(ValueError, match="isn't a register file"):
        overview(empty)


def test_ov11_a_register_file_with_no_folders(tmp_path):
    reg = tmp_path / "register.db"
    con = sqlite3.connect(reg)
    try:
        prepare_register(con)
    finally:
        con.close()
    with pytest.raises(ValueError, match="no folders"):
        overview(reg)


def test_older_register_files_are_read_as_they_are(tmp_path):
    _, _, reg = registered(tmp_path)
    expected = overview(reg)
    for older in ("DROP TABLE unread; PRAGMA user_version = 3;",
                  "DROP TABLE accepted_file; DROP TABLE accepted; PRAGMA user_version = 2;",
                  "DROP TABLE summary; PRAGMA user_version = 1;"):
        con = sqlite3.connect(reg)
        con.executescript(older)
        con.close()
        before = reg.read_bytes()
        assert overview(reg) == expected
        assert reg.read_bytes() == before
