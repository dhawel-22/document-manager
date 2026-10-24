"""Accept: save a new list of a registered folder (spec/accept.md)."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from document_manager.check import CheckResult, compare, listed_files
from document_manager.register import list_files, prepare_register


def accept_folder(folder: Path | str, register_file: Path | str, shown: CheckResult) -> int:
    """Save a new list of the folder, after the person said yes to the
    changes they were shown (AC-1, AC-2). Returns the number of files listed.

    If the folder is no longer what was shown, nothing is saved: only the
    changes the person saw can be accepted.
    """
    folder = Path(folder).resolve(strict=True)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")
    register_file = Path(register_file).resolve(strict=True)
    listed = listed_files(folder, register_file)  # AC-8

    # Read every file before saving anything, so an unreadable file stops
    # the whole run with nothing saved (AC-9).
    files = list_files(folder)
    found = compare(listed, {place: fingerprint for place, _size, fingerprint in files})
    if found != shown:
        raise ValueError(f"{folder} has changed since it was shown. Nothing was saved (AC-1)")
    if not (found.changed or found.new or found.missing):
        raise ValueError("Nothing has changed. Nothing was saved (AC-6)")

    con = sqlite3.connect(register_file)
    try:
        with con:
            prepare_register(con)
            folder_id = con.execute(
                "SELECT id FROM folder WHERE path = ?", (str(folder),)
            ).fetchone()[0]
            now = datetime.now(timezone.utc).isoformat(timespec="seconds")
            accepted_id = con.execute(
                "INSERT INTO accepted (folder_id, accepted_at) VALUES (?, ?)",
                (folder_id, now),
            ).lastrowid
            con.executemany(
                "INSERT INTO accepted_file (accepted_id, path, size, fingerprint)"
                " VALUES (?, ?, ?, ?)",
                [(accepted_id, *f) for f in files],
            )
    finally:
        con.close()
    return len(files)
