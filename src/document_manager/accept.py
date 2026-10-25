"""Accept: save a new list of a registered folder (spec/accept.md)."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from document_manager.check import CheckResult, compare_files, listed_files
from document_manager.register import Counter, Files, list_files, prepare_register


def accept_folder(folder: Path | str, register_file: Path | str, shown: CheckResult,
                  counter: Counter | None = None) -> Files:
    """Save a new list of the folder, after the person said yes to the
    changes they were shown (AC-1, AC-2, BF-6). Returns the files listed.

    If the folder is no longer what was shown, nothing is saved: only the
    changes the person saw can be accepted.
    """
    folder = Path(folder).resolve(strict=True)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")
    register_file = Path(register_file).resolve(strict=True)
    listed = listed_files(folder, register_file)  # AC-8

    # Read every file before saving anything, so a subfolder that can't be
    # read stops the whole run with nothing saved (AC-9, BF-5).
    files = list_files(folder, counter)
    found = compare_files(listed, files)
    if found != shown:
        raise ValueError(f"{folder} has changed since it was shown. Nothing was saved (AC-1)")
    if not (found.changed or found.new or found.missing):  # couldn't read isn't a change (BF-9)
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
                [(accepted_id, *f) for f in files.read],
            )
            con.executemany(
                "INSERT INTO unread (folder_id, accepted_id, path, size, reason)"
                " VALUES (?, ?, ?, ?, ?)",
                [(folder_id, accepted_id, *f) for f in files.unread],
            )
    finally:
        con.close()
    return files
