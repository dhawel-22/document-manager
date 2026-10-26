"""Progress: what a long run has read so far, kept so that the next run
picks up where it stopped (spec/long-runs.md).

The progress file is next to the register file, with ".progress" added to
its name. It's the program's own working file, never part of the register
file (LR-6).
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from typing import NamedTuple

KEEP_EVERY = 60  # seconds: progress is kept at least this often while files are read (LR-2)
VERSION = 1
TABLES = """
BEGIN;
CREATE TABLE run (
    id      INTEGER PRIMARY KEY,
    kind    TEXT NOT NULL,  -- 'register' or 'check' (spec/long-runs.md, Details)
    folder  TEXT NOT NULL,  -- the folder's full path
    kept_at TEXT NOT NULL,  -- when its progress was last kept: date and time, UTC
    UNIQUE (kind, folder)
);
CREATE TABLE file (
    run_id      INTEGER NOT NULL REFERENCES run (id),
    path        TEXT NOT NULL,  -- place in the folder, like letters/note.txt
    size        INTEGER,        -- as the folder's listing gave it when the file was read (LR-3)
    changed     INTEGER,        -- its last-changed time, the same way, in nanoseconds
    read_size   INTEGER,        -- the size the list gets (RG-1, BF-6)
    fingerprint TEXT,           -- NULL if it couldn't be read
    reason      TEXT,           -- why it couldn't be read; NULL if it was read
    PRIMARY KEY (run_id, path)
);
PRAGMA user_version = 1;
COMMIT;
"""


class Earlier(NamedTuple):
    """A file as the run before this one read it (LR-3)."""

    size: int | None  # as the listing gave it then
    changed: int | None
    read_size: int | None
    fingerprint: str | None
    reason: str | None


@dataclass
class PickedUp:
    """How a run picked up where the run before it stopped (LR-4)."""

    stopped_at: str  # when that run's progress was last kept: date and time, UTC
    kept: int  # files it had read that weren't read again
    read_again: int  # files it had that were read again: changed since, or not read then


class Progress:
    """The progress of one kind of run, Register or Check, on one folder."""

    def __init__(self, register_file: Path, kind: str, folder: Path) -> None:
        self.path = register_file.with_name(register_file.name + ".progress")
        self.kind = kind
        self.folder = str(folder)
        self.waiting = []  # files read since the progress was last kept
        self.kept_when = monotonic()

    def earlier(self) -> tuple[str | None, dict[str, Earlier]]:
        """When the run before this one stopped, and each file it had read
        (LR-3); None and nothing if there's no such run."""
        if not self.path.exists():
            return None, {}
        con = sqlite3.connect(f"{self.path.as_uri()}?mode=ro", uri=True)
        try:
            self._check_version(con)
            row = con.execute("SELECT id, kept_at FROM run WHERE kind = ? AND folder = ?",
                              (self.kind, self.folder)).fetchone()
            if row is None:
                return None, {}
            rows = con.execute("SELECT path, size, changed, read_size, fingerprint, reason"
                               " FROM file WHERE run_id = ?", (row[0],))
            return row[1], {path: Earlier(*rest) for path, *rest in rows}
        finally:
            con.close()

    def add(self, place: str, size: int | None, changed: int | None,
            read_size: int | None, fingerprint: str | None, reason: str | None) -> None:
        """A file just read. The progress is kept once a minute has passed (LR-2)."""
        self.waiting.append((place, size, changed, read_size, fingerprint, reason))
        if monotonic() - self.kept_when >= KEEP_EVERY:
            self.keep()

    def keep(self) -> None:
        """Keep the files read since the last time in the progress file
        (LR-1, LR-2). A run that hasn't read a file yet makes no file."""
        if self.waiting:
            con = sqlite3.connect(self.path)
            try:
                if con.execute("PRAGMA user_version").fetchone()[0] == 0:
                    con.executescript(TABLES)
                self._check_version(con)
                with con:
                    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
                    con.execute("INSERT INTO run (kind, folder, kept_at) VALUES (?, ?, ?)"
                                " ON CONFLICT (kind, folder) DO UPDATE SET kept_at = excluded.kept_at",
                                (self.kind, self.folder, now))
                    run_id = con.execute("SELECT id FROM run WHERE kind = ? AND folder = ?",
                                         (self.kind, self.folder)).fetchone()[0]
                    con.executemany("INSERT OR REPLACE INTO file VALUES (?, ?, ?, ?, ?, ?, ?)",
                                    [(run_id, *row) for row in self.waiting])
            finally:
                con.close()
            self.waiting = []
        self.kept_when = monotonic()

    def remove(self) -> None:
        """The run has finished, or can never finish: its progress is removed,
        and the progress file is deleted when no unfinished run is left (LR-5)."""
        self.waiting = []
        if not self.path.exists():
            return
        con = sqlite3.connect(self.path)
        try:
            self._check_version(con)
            with con:
                row = con.execute("SELECT id FROM run WHERE kind = ? AND folder = ?",
                                  (self.kind, self.folder)).fetchone()
                if row is not None:
                    con.execute("DELETE FROM file WHERE run_id = ?", row)
                    con.execute("DELETE FROM run WHERE id = ?", row)
                left = con.execute("SELECT COUNT(*) FROM run").fetchone()[0]
        finally:
            con.close()
        if not left:
            self.path.unlink()

    def _check_version(self, con: sqlite3.Connection) -> None:
        """A progress file of a version this program doesn't know is refused."""
        version = con.execute("PRAGMA user_version").fetchone()[0]
        if version != VERSION:
            raise ValueError(f"Unknown progress file version: {version} ({self.path})")
