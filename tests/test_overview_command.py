"""Tests for the overview's words and its command, spec/overview.md v1.2
(OV-2, OV-10 to OV-12, the example, and the details of the words), and
v1.3 (files that couldn't be read).

The register files here are fakes made by the tests: some by registering
fake folders, some written straight in, since the overview never opens the
folders (OV-1).
"""

import hashlib
import sqlite3
import subprocess
import sys
from pathlib import Path

from document_manager.__main__ import USAGE, main
from document_manager.commands import run_overview
from document_manager.overview import overview
from document_manager.overview_report import NOTE, overview_report, size_words
from document_manager.register import IN_USE, prepare_register, register_folder

PROJECT = Path(__file__).resolve().parent.parent
KB = 1024
EMPTY = hashlib.sha256(b"").hexdigest()  # every empty file's fingerprint


def fp(number):
    """A made-up fingerprint: 64 characters, like a real one (FP-1)."""
    return f"{number:064x}"


def fake_register(path, folders):
    """A register file written straight in. Each folder is its path and its
    lists, oldest first: (date, {place: (size, fingerprint)}). The first
    list is the one saved when it was registered; the others were accepted.
    A fingerprint of None is a file that couldn't be read (BF-6)."""
    con = sqlite3.connect(path)
    try:
        prepare_register(con)
        with con:
            for folder_id, (folder, lists) in enumerate(folders, start=1):
                (registered_at, first), *accepted = lists
                con.execute("INSERT INTO folder (id, path, registered_at) VALUES (?, ?, ?)",
                            (folder_id, folder, registered_at))
                fake_list(con, folder_id, None, first)
                for accepted_at, files in accepted:
                    accepted_id = con.execute(
                        "INSERT INTO accepted (folder_id, accepted_at) VALUES (?, ?)",
                        (folder_id, accepted_at)).lastrowid
                    fake_list(con, folder_id, accepted_id, files)
    finally:
        con.close()
    return path


def fake_list(con, folder_id, accepted_id, files):
    """One of fake_register's lists: the first (accepted_id None), or an
    accepted one."""
    read = [(place, size, fp) for place, (size, fp) in files.items() if fp is not None]
    if accepted_id is None:
        con.executemany("INSERT INTO file VALUES (?, ?, ?, ?)",
                        [(folder_id, *row) for row in read])
    else:
        con.executemany("INSERT INTO accepted_file VALUES (?, ?, ?, ?)",
                        [(accepted_id, *row) for row in read])
    con.executemany("INSERT INTO unread VALUES (?, ?, ?, ?, ?)",
                    [(folder_id, accepted_id, place, size, IN_USE)
                     for place, (size, fp) in files.items() if fp is None])


def example_register(tmp_path):
    """The fake folders of the example in the spec."""
    letters = {"report.pdf": (2048 * KB, fp(1)), "letter.docx": (512 * KB, fp(2)),
               "notes.txt": (0, EMPTY), "holiday.jpg": (400 * KB, fp(3)),
               "readme": (12 * KB, fp(4))}
    accepted = {**letters, "letter.docx": (512 * KB, fp(5)), "plan.xlsx": (64 * KB, fp(6))}
    photos = {"holiday.jpg": (400 * KB, fp(3)), "beach.jpg": (600 * KB, fp(7)),
              "sunset.png": (300 * KB, fp(8))}
    return fake_register(tmp_path / "register.db", [
        (r"C:\Example\Letters", [("2026-10-24T15:20:00+00:00", letters),
                                 ("2026-10-24T16:05:00+00:00", accepted)]),
        (r"C:\Example\Photos", [("2026-10-24T15:22:00+00:00", photos)]),
    ])


def spec_example():
    """The example overview in spec/overview.md, without its indent."""
    lines = (PROJECT / "spec" / "overview.md").read_text(encoding="utf-8").splitlines()
    start = lines.index("Example overview, on fake folders:") + 2
    end = lines.index("How it's proven:") - 1
    return "\n".join(line[4:] for line in lines[start:end])


def registered_docs(tmp_path):
    """A small fake folder, registered."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "note.txt").write_bytes(b"hello\n")
    reg = tmp_path / "register.db"
    register_folder(docs, reg)
    return docs, reg


def test_the_example_in_the_spec_is_exactly_what_it_shows(tmp_path):
    reg = example_register(tmp_path)
    assert overview_report(r"D:\registers\example.db", overview(reg)) == spec_example()


def test_ov2_ov10_the_first_lines_and_the_note(tmp_path):
    _, reg = registered_docs(tmp_path)
    words = overview_report(str(reg), overview(reg))
    assert words.splitlines()[:2] == [
        f"Overview of {reg}", "From the register file only: the folders weren't read."]
    assert words.endswith(f"\nChanges accepted: none.\n{NOTE}")  # said even with none


def test_no_duplicates_say_none(tmp_path):
    _, reg = registered_docs(tmp_path)
    assert "\nDuplicates: none.\n" in overview_report(str(reg), overview(reg))


def test_one_or_more(tmp_path):
    one = {"a.txt": (5, fp(1)), "b.txt": (5, fp(1))}
    two = {"a.txt": (5, fp(1)), "c.txt": (7, fp(2)), "d.txt": (7, fp(2)), "e.txt": (7, fp(2))}
    reg = fake_register(tmp_path / "register.db", [
        (r"C:\One", [("2026-10-24T15:20:00+00:00", one), ("2026-10-24T15:30:00+00:00", one)]),
        (r"C:\Two", [("2026-10-24T15:21:00+00:00", two), ("2026-10-24T15:31:00+00:00", two)]),
    ])
    words = overview_report(str(reg), overview(reg))
    # 3 copies of 5 bytes and 3 copies of 7 bytes: 2 extra copies of each
    assert "\nDuplicates: 2 groups, 4 extra copies, 24 bytes.\n" in words
    assert "\nChanges accepted: 2 lists, in 2 folders. Folders with none: 0.\n" in words


def test_sizes_as_windows_counts_them():
    sizes = [0, 1, 1023, 1024, 1536, 1024 ** 2 - 1, int(47.4 * 1024 ** 3),
             5 * 1024 ** 4, 2048 * 1024 ** 4]
    assert [size_words(size) for size in sizes] == [
        "0 bytes", "1 byte", "1,023 bytes", "1.0 KB", "1.5 KB", "1.0 MB", "47.4 GB",
        "5.0 TB", "2,048.0 TB"]


def test_big_numbers_have_commas_and_line_up(tmp_path):
    files = {f"{n:04}.txt": (1, fp(n)) for n in range(1234)}  # 1,234 files of 1 byte
    files["photo.jpg"] = (2, fp(9999))
    reg = fake_register(tmp_path / "register.db", [
        (r"C:\Many", [("2026-10-24T15:20:00+00:00", files)])])
    lines = overview_report(str(reg), overview(reg)).splitlines()
    assert "Folders: 1, files: 1,235, size: 1.2 KB, empty files: 0." in lines
    assert "  Files: 1,235, size: 1.2 KB. Newest list: 2026-10-24 15:20 UTC." \
           " Changes accepted: 0." in lines
    kinds = lines[lines.index("Kinds:") + 1:lines.index("Kinds:") + 6]
    assert kinds == [
        "  Documents                   1,234 files    1.2 KB",
        "  Pictures, sound and video       1 file    2 bytes",
        "  Program files                   0 files   0 bytes",
        "  Backups and archives            0 files   0 bytes",
        "  Other                           0 files   0 bytes",
    ]


def test_other_endings_show_with_their_dot(tmp_path):
    files = {"a.zz": (1, fp(1)), "b.ZZ": (2, fp(2)), "readme": (3, fp(3))}
    reg = fake_register(tmp_path / "register.db", [
        (r"C:\Odd", [("2026-10-24T15:20:00+00:00", files)])])
    words = overview_report(str(reg), overview(reg))
    assert "  Other                       3 files   6 bytes   endings: .zz 2, (none) 1\n" in words


def test_couldnt_read_shows_only_when_there_are_some(tmp_path):
    busy = {"a.txt": (5, fp(1)), "mail.pst": (9, None), "old.pst": (9, None)}
    reg = fake_register(tmp_path / "register.db", [
        (r"C:\Busy", [("2026-10-25T20:00:00+00:00", busy)]),
        (r"C:\Quiet", [("2026-10-25T20:01:00+00:00", {"c.txt": (3, fp(3))})]),
    ])
    lines = overview_report(str(reg), overview(reg)).splitlines()
    assert "Folders: 2, files: 4, size: 26 bytes, couldn't read: 2, empty files: 0." in lines
    assert "  Files: 3, size: 23 bytes, couldn't read: 2. Newest list: 2026-10-25 20:00 UTC." \
           " Changes accepted: 0." in lines
    assert "  Files: 1, size: 3 bytes. Newest list: 2026-10-25 20:01 UTC." \
           " Changes accepted: 0." in lines
    assert "Duplicates: none." in lines  # with no fingerprints, the two .pst files aren't copies


def test_ov11_a_problem_is_one_plain_line(tmp_path, capsys):
    missing = tmp_path / "missing.db"
    assert main(["overview", str(missing)]) == 1
    out = capsys.readouterr().out
    assert out.startswith("Problem: ") and out.count("\n") == 1
    assert not missing.exists()
    empty = fake_register(tmp_path / "empty.db", [])
    assert main(["overview", str(empty)]) == 1
    assert capsys.readouterr().out == f"Problem: There are no folders in {empty} yet (OV-11)\n"


def test_ov12_the_command_works_as_written(tmp_path):
    _, reg = registered_docs(tmp_path)
    before = (reg.read_bytes(), reg.stat().st_mtime_ns)
    done = subprocess.run(
        [sys.executable, "-m", "document_manager", "overview", str(reg)],
        cwd=PROJECT, capture_output=True, text=True,
    )
    assert done.returncode == 0, done.stderr
    assert done.stdout == overview_report(str(reg), overview(reg)) + "\n"
    assert (reg.read_bytes(), reg.stat().st_mtime_ns) == before  # only read (OV-1)


def test_run_overview_gives_the_result_and_the_words(tmp_path):
    reg = example_register(tmp_path)
    assert run_overview(str(reg)) == (0, overview_report(str(reg), overview(reg)))


def test_the_command_prints_exactly_what_run_overview_gives(monkeypatch, capsys):
    monkeypatch.setattr("document_manager.__main__.run_overview", lambda reg: (1, "Fake words."))
    assert main(["overview", r"D:\fake\register.db"]) == 1
    assert capsys.readouterr().out == "Fake words.\n"


def test_the_command_takes_only_the_register_file(capsys):
    assert main(["overview"]) == 2
    assert main(["overview", r"D:\fake\docs", r"D:\fake\register.db"]) == 2
    assert capsys.readouterr().out == f"{USAGE}\n" * 2
