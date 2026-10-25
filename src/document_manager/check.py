"""Check: compare a folder with its list in the register (spec/check.md)."""

import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from document_manager.register import VERSION, Counter, Files, list_files


@dataclass
class CheckResult:
    """What the check found. Places are like letters/note.txt."""

    changed: list[str]  # CK-2
    new: list[str]  # CK-4
    missing: list[str]  # CK-3
    unchanged: int  # CK-1
    could_not_read: list[tuple[str, str]] = field(default_factory=list)  # (place, reason) (BF-7)


def check_folder(folder: Path | str, register_file: Path | str,
                 counter: Counter | None = None) -> CheckResult:
    """Compare the folder's files now with its list in the register (CK-1)."""
    folder = Path(folder).resolve(strict=True)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")
    listed = listed_files(folder, Path(register_file).resolve(strict=True))
    return compare_files(listed, list_files(folder, counter))


def compare_files(listed: dict[str, str | None], files: Files) -> CheckResult:
    """Compare a list with the folder's files as read now (CK-1 to CK-5, BF-7)."""
    return compare(listed, {place: fp for place, _size, fp in files.read},
                   [(place, why) for place, _size, why in files.unread])


def compare(listed: dict[str, str | None], now: dict[str, str],
            unread: Iterable[tuple[str, str]] = ()) -> CheckResult:
    """Sort each place into changed, new, missing or unchanged (CK-1 to CK-5),
    or couldn't read (BF-7). The list gives each place's fingerprint, or None
    for a file on it that couldn't be read; now gives each place read now,
    and unread each one that can't be read now, with the reason."""
    unread = sorted(unread)
    found = now.keys() | {place for place, _why in unread}
    return CheckResult(
        changed=sorted(p for p in now if listed.get(p) not in (None, now[p])),
        # not on the list, or on it without a fingerprint (BF-7)
        new=sorted(p for p in now if listed.get(p) is None),
        missing=sorted(p for p in listed if p not in found),
        unchanged=sum(1 for p in now if listed.get(p) == now[p]),
        could_not_read=unread,
    )


def listed_files(folder: Path, register_file: Path) -> dict[str, str | None]:
    """The folder's newest list from the register file, opened read-only
    (CK-1, CK-6, CK-7, AC-4): each place's fingerprint, or None for a file on
    it that couldn't be read (BF-6)."""
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
                listed = dict(con.execute(
                    "SELECT path, fingerprint FROM accepted_file WHERE accepted_id = ?",
                    newest,
                ))
                if version >= 4:  # files that couldn't be read came in version 4
                    listed.update(con.execute(
                        "SELECT path, NULL FROM unread WHERE accepted_id = ?", newest
                    ))
                return listed
        listed = dict(con.execute(
            "SELECT path, fingerprint FROM file WHERE folder_id = ?", row
        ))
        if version >= 4:
            listed.update(con.execute(
                "SELECT path, NULL FROM unread WHERE folder_id = ? AND accepted_id IS NULL", row
            ))
        return listed
    finally:
        con.close()
