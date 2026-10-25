"""Check: compare a folder with its list in the register (spec/check.md)."""

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from document_manager.fingerprint import fingerprint
from document_manager.register import VERSION, Counter, all_files, counted


@dataclass
class CheckResult:
    """What the check found. Places are like letters/note.txt."""

    changed: list[str]  # CK-2
    new: list[str]  # CK-4
    missing: list[str]  # CK-3
    unchanged: int  # CK-1


def check_folder(folder: Path | str, register_file: Path | str,
                 counter: Counter | None = None) -> CheckResult:
    """Compare the folder's files now with its list in the register (CK-1)."""
    folder = Path(folder).resolve(strict=True)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")
    listed = listed_files(folder, Path(register_file).resolve(strict=True))
    now = {
        path.relative_to(folder).as_posix(): fingerprint(path)
        for path in counted(all_files(folder, counter), counter)
    }
    return compare(listed, now)


def compare(listed: dict[str, str], now: dict[str, str]) -> CheckResult:
    """Sort each place into changed, new, missing or unchanged (CK-1 to CK-5).
    Both lists give each place's fingerprint."""
    return CheckResult(
        changed=sorted(p for p in now if p in listed and now[p] != listed[p]),
        new=sorted(p for p in now if p not in listed),
        missing=sorted(p for p in listed if p not in now),
        unchanged=sum(1 for p in now if listed.get(p) == now[p]),
    )


def listed_files(folder: Path, register_file: Path) -> dict[str, str]:
    """The folder's newest list from the register file, opened read-only
    (CK-1, CK-6, CK-7, AC-4)."""
    con = sqlite3.connect(f"{register_file.as_uri()}?mode=ro", uri=True)
    try:
        version = con.execute("PRAGMA user_version").fetchone()[0]
        if not 1 <= version <= VERSION:  # version 1 files are read as they are
            raise ValueError(f"Unknown register file version: {version}")
        row = con.execute(
            "SELECT id FROM folder WHERE path = ?", (str(folder),)
        ).fetchone()
        if row is None:
            raise ValueError(f"{folder} is not in the register file (CK-7)")
        if version >= 3:  # accepted lists came in version 3
            newest = con.execute(
                "SELECT id FROM accepted WHERE folder_id = ? ORDER BY id DESC LIMIT 1",
                row,
            ).fetchone()
            if newest is not None:
                rows = con.execute(
                    "SELECT path, fingerprint FROM accepted_file WHERE accepted_id = ?",
                    newest,
                )
                return dict(rows)
        rows = con.execute(
            "SELECT path, fingerprint FROM file WHERE folder_id = ?", row
        )
        return dict(rows)
    finally:
        con.close()
