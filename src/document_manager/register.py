"""Register: the program's list of files (spec/register.md)."""

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from document_manager.fingerprint import fingerprint

SCHEMA = Path(__file__).with_name("register.sql")
VERSION = 1


def register_folder(folder: Path | str, register_file: Path | str) -> int:
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
    files = [
        (path.relative_to(folder).as_posix(), path.stat().st_size, fingerprint(path))
        for path in _all_files(folder)
    ]

    con = sqlite3.connect(register_file)
    try:
        with con:
            _prepare(con)
            known = con.execute("SELECT 1 FROM folder WHERE path = ?", (str(folder),))
            if known.fetchone():
                raise ValueError(f"{folder} is already registered (RG-5)")
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


def _all_files(folder: Path) -> list[Path]:
    """Every file in the folder and its subfolders. A subfolder that can't be
    read raises an error instead of being skipped (RG-6)."""

    def stop(error: OSError) -> None:
        raise error

    found = []
    for root, _dirs, names in os.walk(folder, onerror=stop):
        found.extend(Path(root, name) for name in names)
    return sorted(found)


def _prepare(con: sqlite3.Connection) -> None:
    """Create the tables in a new register file, or check an existing one's version."""
    version = con.execute("PRAGMA user_version").fetchone()[0]
    if version == 0:
        con.executescript(SCHEMA.read_text(encoding="utf-8"))
    elif version != VERSION:
        raise ValueError(f"Unknown register file version: {version}")
