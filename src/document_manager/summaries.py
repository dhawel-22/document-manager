"""Summaries: summarize a registered folder's Word documents into the register
file (spec/summaries.md, SM-1, SM-2, SM-4, SM-5, SM-6, SM-7, SM-9).

The documents are only read (SM-5); the register file is the only file
written. Nothing is sent anywhere: Stage B is off (SM-9).
"""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from document_manager.fingerprint import fingerprint
from document_manager.register import VERSION, all_files, prepare_register
from document_manager.word import CouldNotRead, Summary, summarize_document

METHOD = "stage-a"  # how the summaries are made (SM-2, SM-3)
WORD_FILES = (".docx", ".doc")  # .doc only to list it as "couldn't read" (SM-6)


@dataclass
class SummarizeResult:
    """What a summarizing run found. Places are like letters/report.docx."""

    summarized: list[str]  # new or changed documents, summarized now (SM-4)
    unchanged: int  # skipped: same fingerprint as their last summary (SM-4)
    could_not_read: list[tuple[str, str]]  # (place, reason) (SM-6)


def summarize_folder(folder: Path | str, register_file: Path | str) -> SummarizeResult:
    """Summarize every Word document in a registered folder (SM-1) and save
    the new summaries in the register file (SM-2)."""
    folder = Path(folder).resolve(strict=True)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")
    register_file = Path(register_file).resolve(strict=True)  # never made here
    con = sqlite3.connect(register_file)
    try:
        with con:
            folder_id = _registered(con, folder)  # SM-7, before any change
            prepare_register(con)
            latest = _latest(con, folder_id)
        # Every document is read before anything is saved.
        rows, result = _summarize(folder, latest)
        with con:
            con.executemany(
                "INSERT INTO summary (folder_id, path, fingerprint, made_at, method,"
                " title, headings, first_words, word_count, problem)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [(folder_id, *row) for row in rows],
            )
    finally:
        con.close()
    return result


def _registered(con: sqlite3.Connection, folder: Path) -> int:
    """The folder's id in the register file; an unregistered folder is refused (SM-7)."""
    version = con.execute("PRAGMA user_version").fetchone()[0]
    if version > VERSION:
        raise ValueError(f"Unknown register file version: {version}")
    row = None
    if version >= 1:
        row = con.execute("SELECT id FROM folder WHERE path = ?", (str(folder),)).fetchone()
    if row is None:
        raise ValueError(f"{folder} is not in the register file (SM-7)")
    return row[0]


def _latest(con: sqlite3.Connection, folder_id: int) -> dict[str, tuple[str | None, str | None]]:
    """Each document's last saved fingerprint and problem (SM-4)."""
    rows = con.execute(
        "SELECT path, fingerprint, problem FROM summary AS s WHERE folder_id = ?"
        " AND id = (SELECT MAX(id) FROM summary WHERE folder_id = s.folder_id"
        " AND path = s.path)",
        (folder_id,),
    )
    return {path: (fp, problem) for path, fp, problem in rows}


def _summarize(folder: Path, latest: dict) -> tuple[list[tuple], SummarizeResult]:
    """Read every Word document and work out what to save (SM-1, SM-4, SM-6).

    The documents are only read (SM-5).
    """
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    result = SummarizeResult(summarized=[], unchanged=0, could_not_read=[])
    for path in all_files(folder):
        if path.suffix.lower() not in WORD_FILES:
            continue
        place = path.relative_to(folder).as_posix()
        summary = None
        try:
            fp = fingerprint(path)
        except OSError as error:
            fp, problem = None, f"{type(error).__name__}: {error}"
        else:
            if place in latest and latest[place][0] == fp:  # unchanged (SM-4)
                if latest[place][1] is None:
                    result.unchanged += 1
                else:
                    result.could_not_read.append((place, latest[place][1]))
                continue
            try:
                summary, problem = summarize_document(path), None
            except CouldNotRead as error:
                problem = str(error)
        if problem is None:
            result.summarized.append(place)
        else:
            result.could_not_read.append((place, problem))
            if latest.get(place) == (None, problem):
                continue  # still can't be read, for the same reason: nothing new to save
        rows.append(_row(place, fp, now, summary, problem))
    return rows, result


def _row(place: str, fp: str | None, now: str, summary: Summary | None,
         problem: str | None) -> tuple:
    """One row for the summary table (SM-2)."""
    if summary is None:
        return (place, fp, now, METHOD, None, None, None, None, problem)
    headings = json.dumps(summary.headings, ensure_ascii=False)
    return (place, fp, now, METHOD, summary.title, headings,
            summary.first_words, summary.word_count, None)
