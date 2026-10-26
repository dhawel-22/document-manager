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
from document_manager.register import (
    VERSION, Counter, all_files, counted, gone, prepare_register,
)
from document_manager.word import CouldNotRead, Summary, summarize_document

METHOD = "stage-a"  # how the summaries are made (SM-2, SM-3)
WORD_FILES = (".docx", ".doc")  # .doc only to list it as "couldn't read" (SM-6)


@dataclass
class SummarizeResult:
    """What a summarizing run found. Places are like letters/report.docx."""

    summarized: list[str]  # new or changed documents, summarized now (SM-4)
    unchanged: int  # skipped: same fingerprint as their last summary (SM-4)
    could_not_read: list[tuple[str, str]]  # (place, reason) (SM-6)


def summarize_folder(folder: Path | str, register_file: Path | str,
                     counter: Counter | None = None) -> SummarizeResult:
    """Summarize every Word document in a registered folder (SM-1) and save
    the new summaries in the register file (SM-2)."""
    folder = Path(folder).resolve(strict=True)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")
    register_file = Path(register_file).resolve(strict=True)  # never made here
    con = sqlite3.connect(register_file)
    try:
        folder_id = _registered(con, folder)  # SM-7, before any change
        latest = _latest(con, folder_id)
        # Every document is read before anything is saved, and an older
        # register file is brought up to date only then (v1.5).
        rows, result = _summarize(folder, latest, counter)
        with con:
            prepare_register(con)
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
    if not _has_summaries(con):  # a version 1 register file: nothing summarized yet
        return {}
    rows = con.execute(
        "SELECT path, fingerprint, problem FROM summary AS s WHERE folder_id = ?"
        " AND id = (SELECT MAX(id) FROM summary WHERE folder_id = s.folder_id"
        " AND path = s.path)",
        (folder_id,),
    )
    return {path: (fp, problem) for path, fp, problem in rows}


def _has_summaries(con: sqlite3.Connection) -> bool:
    """Whether the register file has the summaries table. A version 1
    register file, made before summaries, doesn't."""
    return con.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'summary'"
    ).fetchone() is not None


def _summarize(folder: Path, latest: dict,
               counter: Counter | None) -> tuple[list[tuple], SummarizeResult]:
    """Read every Word document and work out what to save (SM-1, SM-4, SM-6).
    A document that's gone when its turn comes is left out (v1.6, BF-3).

    The documents are only read (SM-5).
    """
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    result = SummarizeResult(summarized=[], unchanged=0, could_not_read=[])
    documents = [found.path for found in all_files(folder, counter)
                 if found.path.suffix.lower() in WORD_FILES]
    for path in counted(documents, counter):
        place = path.relative_to(folder).as_posix()
        summary = None
        try:
            fp = fingerprint(path)
        except OSError as error:
            if gone(folder, path):  # BF-3, BF-4
                continue
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
                if gone(folder, path):  # gone while it was read (BF-3, BF-4)
                    continue
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


@dataclass
class SavedSummary:
    """A document's latest saved summary (SM-8). Places are like letters/report.docx."""

    place: str
    made_at: str  # date and time, UTC
    title: str | None  # None when it couldn't be read
    headings: list[tuple[int, str]]
    first_words: str | None
    word_count: int | None
    problem: str | None  # why it couldn't be read (SM-6)


def saved_summaries(folder: Path | str, register_file: Path | str) -> list[SavedSummary]:
    """Each document's latest summary, in order of place (SM-8).

    The register file is opened read-only: showing changes nothing. An
    unregistered folder is refused (SM-7).
    """
    folder = Path(folder).resolve(strict=True)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")
    register_file = Path(register_file).resolve(strict=True)
    con = sqlite3.connect(f"{register_file.as_uri()}?mode=ro", uri=True)
    try:
        folder_id = _registered(con, folder)
        if not _has_summaries(con):  # a version 1 register file: nothing summarized yet
            return []
        rows = con.execute(
            "SELECT path, made_at, title, headings, first_words, word_count, problem"
            " FROM summary AS s WHERE folder_id = ? AND id = (SELECT MAX(id) FROM summary"
            " WHERE folder_id = s.folder_id AND path = s.path)",
            (folder_id,),
        )
        summaries = [
            SavedSummary(place, made_at, title,
                         [tuple(h) for h in json.loads(headings)] if headings else [],
                         first_words, word_count, problem)
            for place, made_at, title, headings, first_words, word_count, problem in rows
        ]
    finally:
        con.close()
    return sorted(summaries, key=lambda s: _folder_order(s.place))


def _folder_order(place: str) -> list[str]:
    """The order summarize uses: folder by folder, ignoring capitals."""
    return place.lower().split("/")
