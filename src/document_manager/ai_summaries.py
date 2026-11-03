"""AI summaries: a model in LM Studio on this computer summarizes a
registered folder's Word documents into the register file
(spec/ai-summaries.md, AI-1 to AI-11).

The documents are only read (AI-10); the register file is the only file
written. The program talks only to LM Studio's server at 127.0.0.1, this
computer (AI-1): the address is fixed here, and Python's http.client never
uses a proxy or follows a redirect to another address.
"""

import http.client
import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from document_manager.fingerprint import fingerprint
from document_manager.register import Counter, all_files, counted, gone, prepare_register
from document_manager.summaries import WORD_FILES, folder_order, registered_id
from document_manager.word import CouldNotRead, document_text

HOST = "127.0.0.1"  # this computer, and nowhere else (AI-1)
PORT = 1234  # LM Studio's server
MODEL = "qwen/qwen3.8-27b"  # Qwen3.8 27B, as LM Studio names it (AI-2)
METHOD = "ai"  # how the summaries are made (AI-7)
INSTRUCTIONS_VERSION = 1  # AI-4
INSTRUCTIONS = (  # word for word as in spec/ai-summaries.md (AI-4)
    "You write summaries for a document register. Summarize the document"
    " below in 3 to 5 plain sentences.\n"
    "Say what kind of document it is, who it is from and to, its date, and"
    " its main points.\n"
    "Use only facts stated in the document. If something is not stated,"
    ' write "unavailable". Do not guess.'
)
MOST_WORDS = 3000  # AI-6
CHECK_WAIT = 10  # seconds to wait for LM Studio to say whether the model is loaded
SUMMARY_WAIT = 30 * 60  # seconds to wait for one summary
THINKING = re.compile(r"<think>.*?</think>", re.DOTALL)  # never saved (On trust)
TOO_BIG = "too big for the model's reading space"  # AI-11
CUT_OFF = "the model's answer was cut off"  # AI-11
NO_ANSWER = "the model gave no answer"
UNREACHABLE = (OSError, http.client.HTTPException)


class LMStudioProblem(Exception):
    """LM Studio can't be used; the message says why, in plain words (AI-9)."""


class NotMade(Exception):
    """No summary was made for one document; the message is why (AI-11)."""


@dataclass
class AiSummarizeResult:
    """What an AI summaries run found. Places are like letters/report.docx."""

    made: list[str]  # summarized now, each one saved as soon as it was made (AI-7)
    unchanged: int  # skipped: unchanged since their last AI summary (AI-8)
    too_long: list[tuple[str, int]]  # (place, words) (AI-6)
    could_not_read: list[tuple[str, str]]  # (place, reason) (SM-6)
    not_made: list[tuple[str, str]]  # (place, reason) (AI-11)


def ai_summarize_folder(folder: Path | str, register_file: Path | str,
                        counter: Counter | None = None) -> AiSummarizeResult:
    """Summarize every Word document in a registered folder with the model
    (AI-3), saving each summary as soon as it's made (AI-7)."""
    folder = Path(folder).resolve(strict=True)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")
    register_file = Path(register_file).resolve(strict=True)  # never made here
    con = sqlite3.connect(register_file)
    try:
        folder_id = registered_id(con, folder, register_file)  # RG-7, SM-7, before any change
        model_ready()  # AI-9, before any document is read
        latest = _latest(con, folder_id)
        result = AiSummarizeResult(made=[], unchanged=0, too_long=[], could_not_read=[],
                                   not_made=[])
        documents = [found.path for found in all_files(folder, counter)
                     if found.path.suffix.lower() in WORD_FILES]
        for path in counted(documents, counter):
            _summarize(con, folder, folder_id, path, latest, result)
    finally:
        con.close()
    return result


def model_ready() -> None:
    """Stop with one plain line if LM Studio's server isn't running, or the
    model isn't loaded (AI-9)."""
    try:
        status, reply = _ask("GET", f"/api/v0/models/{MODEL}", None, CHECK_WAIT)
    except UNREACHABLE as error:
        raise LMStudioProblem(
            "LM Studio's server isn't running on this computer. Turn it on in"
            " LM Studio, then try again. Nothing was saved (AI-9).") from error
    except ValueError as error:
        raise LMStudioProblem(
            f"The program on port {PORT} didn't answer like LM Studio."
            " Nothing was saved (AI-9).") from error
    if status != 200:
        raise LMStudioProblem(f"LM Studio doesn't have {MODEL}. Nothing was saved (AI-9).")
    if reply.get("state") != "loaded":
        raise LMStudioProblem(f"{MODEL} isn't loaded in LM Studio. Load it, then try"
                              " again. Nothing was saved (AI-9).")


def _summarize(con: sqlite3.Connection, folder: Path, folder_id: int, path: Path,
               latest: dict, result: AiSummarizeResult) -> None:
    """One document: skipped, listed, or summarized and saved (AI-6 to AI-8,
    AI-11). A document that's gone when its turn comes is left out (BF-3).

    The document is only read (AI-10).
    """
    place = path.relative_to(folder).as_posix()
    try:
        fp = fingerprint(path)
        if latest.get(place) == (fp, MODEL, INSTRUCTIONS_VERSION):  # AI-8
            result.unchanged += 1
            return
        text = document_text(path)
    except (OSError, CouldNotRead) as error:
        if _gone(folder, path, result):  # BF-3, BF-4
            return
        why = str(error) if isinstance(error, CouldNotRead) else f"{type(error).__name__}: {error}"
        result.could_not_read.append((place, why))  # SM-6
        return
    words = len(text.split())
    if words > MOST_WORDS:  # AI-6
        result.too_long.append((place, words))
        return
    try:
        summary = summary_of(text)
    except NotMade as why:  # AI-11
        result.not_made.append((place, str(why)))
        return
    except (*UNREACHABLE, ValueError) as error:
        raise LMStudioProblem(
            f"LM Studio stopped answering during {place} ({type(error).__name__}: {error})."
            f" AI summaries saved before then: {len(result.made)}.") from error
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with con:  # saved now, so a stop keeps it (AI-7)
        prepare_register(con)
        con.execute(
            "INSERT INTO ai_summary (folder_id, path, fingerprint, made_at, method, model,"
            " instructions, summary) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (folder_id, place, fp, now, METHOD, MODEL, INSTRUCTIONS_VERSION, summary),
        )
    result.made.append(place)


def summary_of(text: str) -> str:
    """The model's summary of one document's text, from the fixed
    instructions and the text, nothing else (AI-4). Only its final answer
    is kept, not its thinking (On trust)."""
    body = {
        "model": MODEL,
        "temperature": 0,  # the same words each time, as in thread 16's try-out
        "messages": [
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user", "content": text},
        ],
    }
    status, reply = _ask("POST", "/v1/chat/completions", body, SUMMARY_WAIT)
    if status != 200:
        error = " ".join(str(reply.get("error", reply)).split())
        if "exceed_context_size" in error or "exceeds the available context size" in error:
            raise NotMade(TOO_BIG)
        raise NotMade(f"LM Studio refused it: {error}")
    try:
        choice = reply["choices"][0]
        finished = choice.get("finish_reason")
        content = choice["message"].get("content") or ""
    except (KeyError, IndexError, TypeError, AttributeError) as error:
        raise ValueError("its answer wasn't in LM Studio's usual form") from error
    if finished != "stop":
        raise NotMade(CUT_OFF)
    answer = THINKING.sub("", content).strip()
    if not answer:
        raise NotMade(NO_ANSWER)
    return answer


def _ask(method: str, path: str, body: dict | None, wait: int) -> tuple[int, dict]:
    """One request to LM Studio's server on this computer, and its answer
    (AI-1). The address is always HOST and PORT."""
    connection = http.client.HTTPConnection(HOST, PORT, timeout=wait)
    try:
        if body is None:
            connection.request(method, path)
        else:
            connection.request(method, path, body=json.dumps(body).encode("utf-8"),
                               headers={"Content-Type": "application/json"})
        response = connection.getresponse()
        reply = json.loads(response.read().decode("utf-8"))
    finally:
        connection.close()
    if not isinstance(reply, dict):
        raise ValueError("its answer wasn't in LM Studio's usual form")
    return response.status, reply


def _gone(folder: Path, path: Path, result: AiSummarizeResult) -> bool:
    """Whether a document that couldn't be read is gone (BF-3). If the
    folder itself can't be reached any more, the run stops (BF-4), keeping
    the summaries already saved (AI-7)."""
    try:
        return gone(folder, path)
    except OSError as error:
        raise OSError(f"{folder} can't be reached any more. AI summaries saved before"
                      f" then: {len(result.made)} (BF-4, AI-7)") from error


def _latest(con: sqlite3.Connection, folder_id: int) -> dict[str, tuple[str, str, int]]:
    """Each document's last AI summary: its fingerprint, model and
    instructions' version (AI-8)."""
    if not _has_ai_summaries(con):  # a register file before version 5: none yet
        return {}
    rows = con.execute(
        "SELECT path, fingerprint, model, instructions FROM ai_summary AS s"
        " WHERE folder_id = ? AND id = (SELECT MAX(id) FROM ai_summary"
        " WHERE folder_id = s.folder_id AND path = s.path)",
        (folder_id,),
    )
    return {path: (fp, model, version) for path, fp, model, version in rows}


def _has_ai_summaries(con: sqlite3.Connection) -> bool:
    """Whether the register file has the AI summaries table. One made before
    version 5 doesn't."""
    return con.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'ai_summary'"
    ).fetchone() is not None


@dataclass
class SavedAiSummary:
    """A document's latest AI summary. Places are like letters/report.docx."""

    place: str
    made_at: str  # date and time, UTC
    model: str
    summary: str


def saved_ai_summaries(folder: Path | str, register_file: Path | str) -> list[SavedAiSummary]:
    """Each document's latest AI summary, in the order summarize uses.

    The register file is opened read-only: showing changes nothing. An
    unregistered folder is refused (SM-7).
    """
    folder = Path(folder).resolve(strict=True)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")
    register_file = Path(register_file).resolve(strict=True)
    con = sqlite3.connect(f"{register_file.as_uri()}?mode=ro", uri=True)
    try:
        folder_id = registered_id(con, folder, register_file)
        if not _has_ai_summaries(con):
            return []
        rows = con.execute(
            "SELECT path, made_at, model, summary FROM ai_summary AS s WHERE folder_id = ?"
            " AND id = (SELECT MAX(id) FROM ai_summary WHERE folder_id = s.folder_id"
            " AND path = s.path)",
            (folder_id,),
        )
        summaries = [SavedAiSummary(*row) for row in rows]
    finally:
        con.close()
    return sorted(summaries, key=lambda s: folder_order(s.place))
