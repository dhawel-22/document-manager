"""Register: the program's list of files (spec/register.md), read so that a
busy folder doesn't stop a run (spec/busy-folders.md)."""

import os
import sqlite3
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from document_manager.fingerprint import fingerprint_of

# Each step brings a register file up one version: register.sql makes
# version 1, register-2.sql adds the summaries (version 2), register-3.sql
# adds accepted lists (version 3), and register-4.sql adds the files that
# couldn't be read (version 4).
STEPS = [
    Path(__file__).with_name(name)
    for name in ("register.sql", "register-2.sql", "register-3.sql", "register-4.sql")
]
VERSION = len(STEPS)

# Why a file couldn't be read, in plain words (spec/busy-folders.md, Details).
# Windows gives Python the same answer for a file in use and for one with no
# permission, so the words name both.
IN_USE = "in use by another program, or no permission"
CHANGED = "changed while it was read"  # BF-2

# A counter is told how far a run has got (spec/window.md, WN-13): the files
# found so far, with no total yet, then the files read out of the total.
# The window's counter can stop the run, always before anything is saved
# (WN-14). The commands pass no counter.
Counter = Callable[[int, int | None], None]


@dataclass
class Files:
    """A folder's files, as read now (RG-1, BF-6). Places are like
    letters/note.txt."""

    read: list[tuple[str, int, str]]  # each file's place, size and fingerprint
    unread: list[tuple[str, int | None, str]]  # place, size if Windows gave it, and why (BF-1)

    @property
    def count(self) -> int:
        """Every file on the list, those that couldn't be read included."""
        return len(self.read) + len(self.unread)


class ChangedWhileRead(Exception):
    """A file whose size or last-changed time was different just after it
    was read than just before. Its fingerprint isn't used (BF-2)."""

    def __init__(self, size: int) -> None:
        super().__init__(CHANGED)
        self.size = size  # just after it was read


def register_folder(folder: Path | str, register_file: Path | str,
                    counter: Counter | None = None) -> Files:
    """List every file in the folder and save the list (RG-1, RG-2, BF-6).

    Returns the files listed.
    """
    folder = Path(folder).resolve(strict=True)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")
    register_file = Path(register_file).resolve()
    if register_file.is_relative_to(folder):
        raise ValueError(f"The register file can't be inside {folder} (RG-4)")

    # Read every file before saving anything, so a subfolder that can't be
    # read stops the whole run with nothing saved (RG-6, BF-5).
    files = list_files(folder, counter)

    con = sqlite3.connect(register_file)
    try:
        with con:
            # Refuse before the register file is brought up to date, so a
            # refused folder leaves it exactly as it was (RG-5).
            if is_registered(con, folder):
                raise ValueError(f"{folder} is already registered (RG-5)")
            prepare_register(con)
            now = datetime.now(timezone.utc).isoformat(timespec="seconds")
            folder_id = con.execute(
                "INSERT INTO folder (path, registered_at) VALUES (?, ?)",
                (str(folder), now),
            ).lastrowid
            con.executemany(
                "INSERT INTO file (folder_id, path, size, fingerprint)"
                " VALUES (?, ?, ?, ?)",
                [(folder_id, *f) for f in files.read],
            )
            con.executemany(
                "INSERT INTO unread (folder_id, path, size, reason) VALUES (?, ?, ?, ?)",
                [(folder_id, *f) for f in files.unread],
            )
    finally:
        con.close()
    return files


def is_registered(con: sqlite3.Connection, folder: Path) -> bool:
    """Whether the folder is in the register file. A new register file has
    no folder table yet."""
    has_table = con.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'folder'"
    ).fetchone()
    if not has_table:
        return False
    return con.execute(
        "SELECT 1 FROM folder WHERE path = ?", (str(folder),)
    ).fetchone() is not None


def list_files(folder: Path, counter: Counter | None = None) -> Files:
    """Every file's place in the folder, size and fingerprint (RG-1). A file
    that can't be read is listed with the reason instead (BF-1, BF-2), and
    one that's gone when its turn comes is left out (BF-3)."""
    files = Files(read=[], unread=[])
    for path in counted(all_files(folder, counter), counter):
        place = path.relative_to(folder).as_posix()
        try:
            files.read.append((place, *read_file(path)))
        except ChangedWhileRead as changed:
            files.unread.append((place, changed.size, CHANGED))
        except OSError as error:
            if not gone(folder, path):
                files.unread.append((place, size_of(path), reason(error)))
    return files


def read_file(path: Path) -> tuple[int, str]:
    """A file's size and fingerprint. The size and last-changed time are read
    from the open file just before and just after its contents (BF-2)."""
    with open(path, "rb") as f:
        before = os.fstat(f.fileno())
        fp = fingerprint_of(f)
        after = os.fstat(f.fileno())
    if (after.st_size, after.st_mtime_ns) != (before.st_size, before.st_mtime_ns):
        raise ChangedWhileRead(after.st_size)
    return after.st_size, fp


def gone(folder: Path, path: Path | str) -> bool:
    """Whether a file or subfolder that couldn't be read is gone: deleted or
    renamed while the run ran (BF-3). The folder itself is looked at first:
    if it can't be reached any more, the run stops and nothing is saved
    (BF-4)."""
    try:
        folder.stat()
    except OSError as error:
        raise OSError(f"{folder} can't be reached any more. Nothing was saved (BF-4)") from error
    return not os.path.lexists(path)


def reason(error: OSError) -> str:
    """Why a file couldn't be read: in plain words where the program knows
    them, else the error word for word, without the file's path (BF-1)."""
    if isinstance(error, PermissionError):
        return IN_USE
    return f"{type(error).__name__}: {error.strerror or error}"


def size_of(path: Path) -> int | None:
    """A file's size, if Windows gives it (BF-6)."""
    try:
        return path.stat().st_size
    except OSError:
        return None


def all_files(folder: Path, counter: Counter | None = None) -> list[Path]:
    """Every file in the folder and its subfolders. A subfolder that's gone
    is passed over (BF-3); one that can't be read raises an error instead of
    being skipped (RG-6, BF-5). The counter is told the files found so far,
    after each folder."""

    def problem(error: OSError) -> None:
        if error.filename is None or not gone(folder, error.filename):
            raise error

    found = []
    for root, _dirs, names in os.walk(folder, onerror=problem):
        found.extend(Path(root, name) for name in names)
        if counter:
            counter(len(found), None)
    return sorted(found)


def counted(paths: list[Path], counter: Counter | None) -> Iterator[Path]:
    """The paths one at a time. The counter is told none read, then one more
    after each, so it's told about the last one before anything is saved."""
    total = len(paths)
    if counter:
        counter(0, total)
    for done, path in enumerate(paths, start=1):
        yield path
        if counter:
            counter(done, total)


def prepare_register(con: sqlite3.Connection) -> None:
    """Create the tables in a new register file, or bring an older one up to
    the current version, one step at a time."""
    version = con.execute("PRAGMA user_version").fetchone()[0]
    if version > VERSION:
        raise ValueError(f"Unknown register file version: {version}")
    for step in STEPS[version:]:
        con.executescript(step.read_text(encoding="utf-8"))
