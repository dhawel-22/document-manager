"""Register: the program's list of files (spec/register.md)."""

import os
import sqlite3
from collections.abc import Callable, Iterator
from datetime import datetime, timezone
from pathlib import Path

from document_manager.fingerprint import fingerprint

# Each step brings a register file up one version: register.sql makes
# version 1, register-2.sql adds the summaries (version 2), and
# register-3.sql adds accepted lists (version 3).
STEPS = [
    Path(__file__).with_name(name)
    for name in ("register.sql", "register-2.sql", "register-3.sql")
]
VERSION = len(STEPS)

# A counter is told how far a run has got (spec/window.md, WN-13): the files
# found so far, with no total yet, then the files read out of the total.
# The window's counter can stop the run, always before anything is saved
# (WN-14). The commands pass no counter.
Counter = Callable[[int, int | None], None]


def register_folder(folder: Path | str, register_file: Path | str,
                    counter: Counter | None = None) -> int:
    """List every file in the folder and save the list (RG-1, RG-2).

    Returns the number of files saved.
    """
    folder = Path(folder).resolve(strict=True)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")
    register_file = Path(register_file).resolve()
    if register_file.is_relative_to(folder):
        raise ValueError(f"The register file can't be inside {folder} (RG-4)")

    # Read every file before saving anything, so an unreadable file stops
    # the whole run with nothing saved (RG-6).
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
                [(folder_id, *f) for f in files],
            )
    finally:
        con.close()
    return len(files)


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


def list_files(folder: Path, counter: Counter | None = None) -> list[tuple[str, int, str]]:
    """Every file's place in the folder, size and fingerprint (RG-1)."""
    return [
        (path.relative_to(folder).as_posix(), path.stat().st_size, fingerprint(path))
        for path in counted(all_files(folder, counter), counter)
    ]


def all_files(folder: Path, counter: Counter | None = None) -> list[Path]:
    """Every file in the folder and its subfolders. A subfolder that can't be
    read raises an error instead of being skipped (RG-6). The counter is
    told the files found so far, after each folder."""

    def stop(error: OSError) -> None:
        raise error

    found = []
    for root, _dirs, names in os.walk(folder, onerror=stop):
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
