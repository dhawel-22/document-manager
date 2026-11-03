"""Tests for AI summaries, spec/ai-summaries.md (AI-1 to AI-11, and the
commands).

Every Word document here is a fake, made by the test in a temporary folder.
LM Studio is never used: a stand-in for its server answers instead, on this
computer, so the tests run the same way on GitHub's computer, where there's
no model (How it's proven).
"""

import http.client
import json
import re
import socket
import sqlite3
import subprocess
import sys
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import docx
import pytest

from document_manager import ai_summaries
from document_manager.__main__ import main
from document_manager.ai_summaries import (
    CUT_OFF, INSTRUCTIONS, MODEL, TOO_BIG, AiSummarizeResult, ai_summarize_folder,
    saved_ai_summaries,
)
from document_manager.commands import AI_STOPPED, COMMANDS, run
from document_manager.fingerprint import fingerprint
from document_manager.register import register_folder
from document_manager.summaries import summarize_folder

PROJECT = Path(__file__).resolve().parent.parent
OLD_FORMAT = bytes.fromhex("D0CF11E0A1B11AE1") + bytes(504)
OLD_REASON = "old Word file (.doc); save it as .docx in Word first"
TIME = re.compile(r"\d{4}-\d\d-\d\d \d\d:\d\d UTC")


class StandIn(ThreadingHTTPServer):
    """A stand-in for LM Studio's server, on this computer. It answers the
    two questions the program asks, the way LM Studio did in thread 16."""

    allow_reuse_address = False  # never shares a port that another program is using
    daemon_threads = True

    def server_bind(self):
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):  # Windows: not even a more exact address
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()

    def __init__(self, port=0):
        super().__init__(("127.0.0.1", port), Answers)
        self.has_model = True
        self.state = "loaded"
        self.asked = []  # (method, path, body) for each request, in order
        self.answer = about  # what the model says: text -> (status, reply), or None to hang up

    @property
    def port(self):
        return self.server_address[1]

    def summaries_asked(self):
        """The bodies of the requests for a summary."""
        return [body for method, path, body in self.asked if method == "POST"]


class Answers(BaseHTTPRequestHandler):
    """The stand-in's answers."""

    def do_GET(self):
        self.server.asked.append(("GET", self.path, None))
        if self.server.has_model and self.path == f"/api/v0/models/{MODEL}":
            self.send({"id": MODEL, "object": "model", "state": self.server.state,
                       "loaded_context_length": 8192})
        else:
            name = self.path.removeprefix("/api/v0/models/")
            self.send({"error": f"Model with identifier '{name}' not found"}, 400)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.server.asked.append(("POST", self.path, body))
        answer = self.server.answer(body["messages"][-1]["content"])
        if answer is None:  # LM Studio stops answering
            self.close_connection = True
            return
        self.send(answer[1], answer[0])

    def send(self, reply, status=200):
        data = json.dumps(reply).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass  # quiet


def reply(content, finished="stop"):
    """A summary answer, shaped like LM Studio's, thinking included."""
    return 200, {
        "model": MODEL,
        "choices": [{"index": 0, "finish_reason": finished, "message": {
            "role": "assistant", "content": content,
            "reasoning_content": "First I read the document."}}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
    }


def about(text):
    """The stand-in model's summary: the document's first line."""
    return reply(f"About: {text.splitlines()[0] if text else ''}")


@pytest.fixture
def lm_studio(monkeypatch):
    """The stand-in, running, with the program pointed at its port."""
    server = StandIn()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setattr(ai_summaries, "PORT", server.port)
    yield server
    server.shutdown()
    server.server_close()


def fake_docx(path, text):
    """A fake Word document, one paragraph per line of text."""
    made = docx.Document()
    for line in text.split("\n"):
        made.add_paragraph(line)
    made.save(path)


def registered_docs(tmp_path):
    """A small folder of fake documents, already registered."""
    docs = tmp_path / "docs"
    (docs / "letters").mkdir(parents=True)
    fake_docx(docs / "report.docx", "Markets were calm.")
    fake_docx(docs / "letters" / "note.docx", "Dear Ernie.")
    (docs / "notes.txt").write_bytes(b"not a Word document\n")
    (docs / "old.doc").write_bytes(OLD_FORMAT)
    reg = tmp_path / "register.db"
    register_folder(docs, reg)
    return docs, reg


def query(register_file, sql):
    con = sqlite3.connect(register_file)
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


def as_version_4(register_file):
    """Turn a register file back into version 4, as made before AI summaries."""
    con = sqlite3.connect(register_file)
    try:
        con.executescript("DROP TABLE ai_summary; PRAGMA user_version = 4;")
    finally:
        con.close()


def free_port():
    """A port on this computer that nothing is listening on."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# AI-1 -------------------------------------------------------------------

def test_ai1_talks_only_to_this_computer_even_with_a_proxy_set(tmp_path, lm_studio,
                                                               monkeypatch):
    docs, reg = registered_docs(tmp_path)
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy"):
        monkeypatch.setenv(name, "http://192.0.2.1:9")  # an address that's never used
    connections = []

    class Recorded(http.client.HTTPConnection):
        def __init__(self, host, port=None, **kwargs):
            connections.append((host, port))
            super().__init__(host, port, **kwargs)

    monkeypatch.setattr(http.client, "HTTPConnection", Recorded)
    assert ai_summarize_folder(docs, reg).made == ["letters/note.docx", "report.docx"]
    assert connections == [("127.0.0.1", lm_studio.port)] * 3  # the check, then two summaries
    assert len(lm_studio.asked) == 3


def test_ai1_the_address_is_this_computer():
    assert ai_summaries.HOST == "127.0.0.1"


# AI-2 -------------------------------------------------------------------

def test_ai2_the_model_is_qwen38_27b(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)
    ai_summarize_folder(docs, reg)
    assert MODEL == "qwen/qwen3.8-27b"
    assert lm_studio.asked[0] == ("GET", "/api/v0/models/qwen/qwen3.8-27b", None)
    assert [body["model"] for body in lm_studio.summaries_asked()] == [MODEL, MODEL]


# AI-3 -------------------------------------------------------------------

def test_ai3_every_word_document_in_the_folder_and_its_subfolders(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)
    assert ai_summarize_folder(docs, reg) == AiSummarizeResult(
        made=["letters/note.docx", "report.docx"],
        unchanged=0,
        too_long=[],
        could_not_read=[("old.doc", OLD_REASON)],
        not_made=[],
    )


def test_ai3_unregistered_folder_is_refused_before_lm_studio_is_asked(tmp_path, lm_studio):
    _, reg = registered_docs(tmp_path)
    other = tmp_path / "other"
    other.mkdir()
    with pytest.raises(ValueError, match="SM-7"):
        ai_summarize_folder(other, reg)
    assert lm_studio.asked == []


def test_ai3_missing_register_file_is_not_made(tmp_path, lm_studio):
    docs, _ = registered_docs(tmp_path)
    with pytest.raises(FileNotFoundError):
        ai_summarize_folder(docs, tmp_path / "not-there.db")
    assert not (tmp_path / "not-there.db").exists()


# AI-4 -------------------------------------------------------------------

def test_ai4_the_model_gets_the_instructions_and_the_text_nothing_else(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)
    fake_docx(docs / "report.docx", "Markets were calm.\nRates stayed at 5%.")
    ai_summarize_folder(docs, reg)
    assert lm_studio.summaries_asked() == [
        {"model": MODEL, "temperature": 0, "messages": [
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user", "content": "Dear Ernie."},
        ]},
        {"model": MODEL, "temperature": 0, "messages": [
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user", "content": "Markets were calm.\nRates stayed at 5%."},
        ]},
    ]


def test_ai4_the_instructions_are_word_for_word_as_in_the_rules():
    spec = (PROJECT / "spec" / "ai-summaries.md").read_text(encoding="utf-8")
    block = re.search(r"The instructions \(version 1\), sent to the model word for word:\n\n"
                      r"((?:    .*\n)+)", spec)
    assert block, "the instructions weren't found in spec/ai-summaries.md"
    in_spec = block.group(1).split()
    assert INSTRUCTIONS.split() == in_spec
    assert ai_summaries.INSTRUCTIONS_VERSION == 1


# AI-5 -------------------------------------------------------------------

def test_ai5_the_saved_summary_is_the_models_answer_word_for_word(tmp_path, lm_studio):
    """The program adds nothing and rewords nothing; whether the model keeps
    to what the document states is seen in the try-out."""
    docs, reg = registered_docs(tmp_path)
    answer = 'A letter to Ernie. Its date is "unavailable".'
    lm_studio.answer = lambda text: reply(answer)
    ai_summarize_folder(docs, reg)
    assert query(reg, "SELECT summary FROM ai_summary") == [(answer,), (answer,)]


def test_ai5_the_instructions_ask_for_unavailable_and_no_guessing():
    assert 'If something is not stated, write "unavailable". Do not guess.' in INSTRUCTIONS


# AI-6 -------------------------------------------------------------------

def test_ai6_over_3000_words_is_too_long_and_never_sent(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)
    fake_docx(docs / "longest.docx", " ".join(["word"] * 3001))
    fake_docx(docs / "long.docx", " ".join(["word"] * 2999) + "\nlast line")  # 3,001 too
    fake_docx(docs / "just.docx", " ".join(["word"] * 3000))
    result = ai_summarize_folder(docs, reg)
    assert result.too_long == [("long.docx", 3001), ("longest.docx", 3001)]
    assert "just.docx" in result.made
    sent = [body["messages"][1]["content"] for body in lm_studio.summaries_asked()]
    assert len(sent) == 3 and all(len(text.split()) <= 3000 for text in sent)
    assert query(reg, "SELECT path FROM ai_summary WHERE path LIKE 'long%'") == []


# AI-7 -------------------------------------------------------------------

def test_ai7_each_summary_is_saved_with_how_it_was_made(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)
    ai_summarize_folder(docs, reg)
    assert query(reg, "SELECT path, fingerprint, method, model, instructions, summary"
                      " FROM ai_summary ORDER BY id") == [
        ("letters/note.docx", fingerprint(docs / "letters" / "note.docx"), "ai", MODEL, 1,
         "About: Dear Ernie."),
        ("report.docx", fingerprint(docs / "report.docx"), "ai", MODEL, 1,
         "About: Markets were calm."),
    ]
    for (when,) in query(reg, "SELECT made_at FROM ai_summary"):
        age = datetime.now(timezone.utc) - datetime.fromisoformat(when)
        assert timedelta(0) <= age < timedelta(minutes=1)


def test_ai7_a_summary_is_saved_as_soon_as_it_is_made(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)
    saved_when_asked = []

    def answer(text):  # what the register file holds when each summary is asked for
        saved_when_asked.append(query(reg, "SELECT path FROM ai_summary"))
        return about(text)

    lm_studio.answer = answer
    ai_summarize_folder(docs, reg)
    assert saved_when_asked == [[], [("letters/note.docx",)]]


class Stop(Exception):
    """The window's Stop, as its counter raises it (WN-14)."""


def test_ai7_a_stop_keeps_the_summaries_already_saved(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)

    def counter(done, total):
        if total is not None and done == 1:
            raise Stop

    with pytest.raises(Stop):
        ai_summarize_folder(docs, reg, counter)
    assert query(reg, "SELECT path FROM ai_summary") == [("letters/note.docx",)]


def test_ai7_ctrl_c_keeps_the_summaries_already_saved(tmp_path, lm_studio, monkeypatch,
                                                     capsys):
    docs, reg = registered_docs(tmp_path)
    summary_of = ai_summaries.summary_of

    def ctrl_c_during_the_second(text):  # while the program waits for the model
        if text == "Markets were calm.":
            raise KeyboardInterrupt
        return summary_of(text)

    monkeypatch.setattr(ai_summaries, "summary_of", ctrl_c_during_the_second)
    try:
        code = main(["ai-summarize", str(docs), str(reg)])
    except KeyboardInterrupt:  # fails this test only, not the whole test run
        pytest.fail("Ctrl+C wasn't caught")
    assert code == 1
    assert capsys.readouterr().out == f"{AI_STOPPED}\n"
    assert query(reg, "SELECT path FROM ai_summary") == [("letters/note.docx",)]


def test_ai7_stage_a_summaries_and_older_rows_never_change(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)
    summarize_folder(docs, reg)
    stage_a = query(reg, "SELECT * FROM summary ORDER BY id")
    ai_summarize_folder(docs, reg)
    first = query(reg, "SELECT * FROM ai_summary ORDER BY id")
    fake_docx(docs / "report.docx", "Markets fell sharply today.")
    assert ai_summarize_folder(docs, reg).made == ["report.docx"]
    rows = query(reg, "SELECT * FROM ai_summary ORDER BY id")
    assert rows[:2] == first
    assert [(row[2], row[8]) for row in rows[2:]] == [("report.docx",
                                                        "About: Markets fell sharply today.")]
    assert query(reg, "SELECT * FROM summary ORDER BY id") == stage_a


def test_ai7_an_older_register_file_becomes_version_5_at_the_first_save(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)
    as_version_4(reg)
    files = query(reg, "SELECT * FROM file ORDER BY path")
    ai_summarize_folder(docs, reg)
    assert query(reg, "PRAGMA user_version") == [(5,)]
    assert len(query(reg, "SELECT * FROM ai_summary")) == 2
    assert query(reg, "SELECT * FROM file ORDER BY path") == files


def test_ai7_a_run_that_saves_nothing_leaves_an_older_register_file_as_it_was(tmp_path,
                                                                             lm_studio):
    docs, reg = registered_docs(tmp_path)
    as_version_4(reg)
    before = reg.read_bytes()
    lm_studio.answer = lambda text: reply("Half a sente", "length")
    result = ai_summarize_folder(docs, reg)
    assert result.made == [] and len(result.not_made) == 2
    assert reg.read_bytes() == before


# AI-8 -------------------------------------------------------------------

def test_ai8_unchanged_documents_are_skipped(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)
    ai_summarize_folder(docs, reg)
    before = query(reg, "SELECT * FROM ai_summary")
    asked = len(lm_studio.asked)
    assert ai_summarize_folder(docs, reg) == AiSummarizeResult(
        made=[], unchanged=2, too_long=[], could_not_read=[("old.doc", OLD_REASON)],
        not_made=[])
    assert lm_studio.asked[asked:] == [("GET", f"/api/v0/models/{MODEL}", None)]
    assert query(reg, "SELECT * FROM ai_summary") == before


def test_ai8_a_changed_document_gets_a_new_summary(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)
    ai_summarize_folder(docs, reg)
    fake_docx(docs / "report.docx", "Markets fell sharply today.")
    result = ai_summarize_folder(docs, reg)
    assert (result.made, result.unchanged) == (["report.docx"], 1)


def test_ai8_another_instructions_version_isnt_skipped(tmp_path, lm_studio, monkeypatch):
    docs, reg = registered_docs(tmp_path)
    ai_summarize_folder(docs, reg)
    monkeypatch.setattr(ai_summaries, "INSTRUCTIONS_VERSION", 2)
    result = ai_summarize_folder(docs, reg)
    assert (result.made, result.unchanged) == (["letters/note.docx", "report.docx"], 0)
    assert query(reg, "SELECT instructions FROM ai_summary ORDER BY id") == [
        (1,), (1,), (2,), (2,)]


def test_ai8_another_model_isnt_skipped(tmp_path, lm_studio, monkeypatch):
    docs, reg = registered_docs(tmp_path)
    ai_summarize_folder(docs, reg)
    monkeypatch.setattr(ai_summaries, "MODEL", "another/model")
    monkeypatch.setattr(ai_summaries, "model_ready", lambda: None)  # the stand-in knows only Qwen
    result = ai_summarize_folder(docs, reg)
    assert (result.made, result.unchanged) == (["letters/note.docx", "report.docx"], 0)
    assert query(reg, "SELECT model FROM ai_summary ORDER BY id") == [
        (MODEL,), (MODEL,), ("another/model",), ("another/model",)]


# AI-9 -------------------------------------------------------------------

def no_document_is_read(monkeypatch):
    def read(path):
        raise AssertionError(f"{path} was read")

    monkeypatch.setattr(ai_summaries, "fingerprint", read)
    monkeypatch.setattr(ai_summaries, "document_text", read)


def test_ai9_lm_studio_not_running_stops_the_run_before_any_document_is_read(tmp_path,
                                                                            monkeypatch):
    docs, reg = registered_docs(tmp_path)
    as_version_4(reg)
    before = reg.read_bytes()
    monkeypatch.setattr(ai_summaries, "PORT", free_port())
    no_document_is_read(monkeypatch)
    assert run("ai-summarize", str(docs), str(reg)) == (
        1, "Problem: LM Studio's server isn't running on this computer. Turn it on in"
           " LM Studio, then try again. Nothing was saved (AI-9).")
    assert reg.read_bytes() == before


def test_ai9_model_not_loaded_stops_the_run_before_any_document_is_read(tmp_path, lm_studio,
                                                                       monkeypatch):
    docs, reg = registered_docs(tmp_path)
    as_version_4(reg)
    before = reg.read_bytes()
    lm_studio.state = "not-loaded"
    no_document_is_read(monkeypatch)
    assert run("ai-summarize", str(docs), str(reg)) == (
        1, f"Problem: {MODEL} isn't loaded in LM Studio. Load it, then try again."
           " Nothing was saved (AI-9).")
    assert lm_studio.summaries_asked() == []
    assert reg.read_bytes() == before


def test_ai9_model_not_in_lm_studio_stops_the_run(tmp_path, lm_studio, monkeypatch):
    docs, reg = registered_docs(tmp_path)
    lm_studio.has_model = False
    no_document_is_read(monkeypatch)
    assert run("ai-summarize", str(docs), str(reg)) == (
        1, f"Problem: LM Studio doesn't have {MODEL}. Nothing was saved (AI-9).")


def test_ai9_another_program_on_the_port_stops_the_run(tmp_path, monkeypatch):
    docs, reg = registered_docs(tmp_path)

    class NotLMStudio(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<html>hello</html>")

        def log_message(self, *args):
            pass

    other = ThreadingHTTPServer(("127.0.0.1", 0), NotLMStudio)
    threading.Thread(target=other.serve_forever, daemon=True).start()
    try:
        monkeypatch.setattr(ai_summaries, "PORT", other.server_address[1])
        code, words = run("ai-summarize", str(docs), str(reg))
    finally:
        other.shutdown()
        other.server_close()
    assert (code, words) == (1, f"Problem: The program on port {other.server_address[1]}"
                                " didn't answer like LM Studio. Nothing was saved (AI-9).")


# AI-10 ------------------------------------------------------------------

def test_ai10_only_reads_the_documents(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)

    def snapshot():
        files = [p for p in docs.rglob("*") if p.is_file()]
        return {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}

    before = snapshot()
    ai_summarize_folder(docs, reg)
    assert snapshot() == before


# AI-11 ------------------------------------------------------------------

def test_ai11_too_big_for_the_reading_space_is_listed_and_the_run_carries_on(tmp_path,
                                                                             lm_studio):
    docs, reg = registered_docs(tmp_path)

    def answer(text):
        if text == "Dear Ernie.":  # LM Studio's own words, from thread 16
            return 400, {"error": 'Engine protocol predict request returned 400: {"error":'
                                  '{"code":400,"message":"request (10859 tokens) exceeds the'
                                  ' available context size (8192 tokens), try increasing it",'
                                  '"type":"exceed_context_size_error"}}'}
        return about(text)

    lm_studio.answer = answer
    result = ai_summarize_folder(docs, reg)
    assert result.not_made == [("letters/note.docx", TOO_BIG)]
    assert result.made == ["report.docx"]
    assert query(reg, "SELECT path FROM ai_summary") == [("report.docx",)]


def test_ai11_an_answer_cut_off_is_listed_not_saved(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)
    lm_studio.answer = lambda text: (reply("The document is a monthly report. Its date is",
                                           "length") if text == "Dear Ernie." else about(text))
    result = ai_summarize_folder(docs, reg)
    assert result.not_made == [("letters/note.docx", CUT_OFF)]
    assert query(reg, "SELECT path FROM ai_summary") == [("report.docx",)]


def test_ai11_anything_else_lm_studio_refuses_is_listed_in_its_words(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)
    lm_studio.answer = lambda text: (500, {"error": "Something\nwent wrong"})
    result = ai_summarize_folder(docs, reg)
    assert result.not_made == [("letters/note.docx", "LM Studio refused it: Something went wrong"),
                               ("report.docx", "LM Studio refused it: Something went wrong")]


def test_ai11_no_answer_is_listed_not_saved(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)
    lm_studio.answer = lambda text: reply("<think>Hmm.</think>\n  ")
    result = ai_summarize_folder(docs, reg)
    assert result.not_made == [("letters/note.docx", "the model gave no answer"),
                               ("report.docx", "the model gave no answer")]
    assert query(reg, "SELECT * FROM ai_summary") == []


# On trust, busy folders, and LM Studio stopping ---------------------------

def test_the_models_thinking_is_never_saved(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)
    lm_studio.answer = lambda text: reply("<think>Who is it from?</think>\n\nA short letter.")
    ai_summarize_folder(docs, reg)
    assert query(reg, "SELECT summary FROM ai_summary") == [("A short letter.",)] * 2


def test_lm_studio_stopping_during_a_run_stops_it_and_keeps_what_was_saved(tmp_path,
                                                                           lm_studio):
    docs, reg = registered_docs(tmp_path)
    lm_studio.answer = lambda text: None if text == "Markets were calm." else about(text)
    code, words = run("ai-summarize", str(docs), str(reg))
    assert code == 1
    assert words.startswith("Problem: LM Studio stopped answering during report.docx (")
    assert words.endswith("). AI summaries saved before then: 1.")
    assert "\n" not in words
    assert query(reg, "SELECT path FROM ai_summary") == [("letters/note.docx",)]


def test_bf3_a_document_gone_when_its_turn_comes_is_left_out(tmp_path, lm_studio, monkeypatch):
    docs, reg = registered_docs(tmp_path)

    def deleted_first(path):
        if path.name == "report.docx":
            path.unlink()
        return fingerprint(path)

    monkeypatch.setattr(ai_summaries, "fingerprint", deleted_first)
    result = ai_summarize_folder(docs, reg)
    assert (result.made, result.could_not_read) == (["letters/note.docx"],
                                                    [("old.doc", OLD_REASON)])


def test_bf4_a_folder_that_cant_be_reached_stops_the_run_and_keeps_what_was_saved(
        tmp_path, lm_studio, monkeypatch):
    docs, reg = registered_docs(tmp_path)

    def unreachable(path):
        if path.name == "report.docx":
            raise OSError("the network name is no longer available")
        return fingerprint(path)

    def folder_gone(folder, path):
        raise OSError(f"{folder} can't be reached any more. Nothing was saved (BF-4)")

    monkeypatch.setattr(ai_summaries, "fingerprint", unreachable)
    monkeypatch.setattr(ai_summaries, "gone", folder_gone)
    assert run("ai-summarize", str(docs), str(reg)) == (
        1, f"Problem: {docs.resolve()} can't be reached any more. AI summaries saved before"
           " then: 1 (BF-4, AI-7)")
    assert query(reg, "SELECT path FROM ai_summary") == [("letters/note.docx",)]


# The commands -----------------------------------------------------------

def test_ai_summarize_says_what_it_did(tmp_path, lm_studio, capsys):
    docs, reg = registered_docs(tmp_path)
    fake_docx(docs / "big.docx", " ".join(["word"] * 3001))
    fake_docx(docs / "cut.docx", "cut me off")
    lm_studio.answer = lambda text: reply("Half", "length") if text == "cut me off" else about(text)
    assert main(["ai-summarize", str(docs), str(reg)]) == 0
    assert capsys.readouterr().out == (
        "AI summaries made: 2, unchanged: 0, too long: 1, couldn't read: 1, not made: 1.\n"
        "  too long  big.docx  3001 words\n"
        f"  couldn't read  old.doc  {OLD_REASON}\n"
        f"  not made  cut.docx  {CUT_OFF}\n"
    )


def test_ai_summaries_shows_each_documents_latest_ai_summary(tmp_path, lm_studio, capsys):
    docs, reg = registered_docs(tmp_path)
    ai_summarize_folder(docs, reg)
    fake_docx(docs / "report.docx", "Markets fell sharply today.")
    lm_studio.answer = lambda text: reply(f"About: {text}\nSecond line.")
    ai_summarize_folder(docs, reg)
    assert main(["ai-summaries", str(docs), str(reg)]) == 0
    assert TIME.sub("TIME", capsys.readouterr().out) == (
        f"AI summaries for {docs}. Documents: 2.\n"
        "\n"
        f"letters/note.docx  (made TIME by {MODEL})\n"
        "  About: Dear Ernie.\n"
        "\n"
        f"report.docx  (made TIME by {MODEL})\n"
        "  About: Markets fell sharply today.\n"
        "  Second line.\n"
    )


def test_ai_summaries_none_yet(tmp_path, capsys):
    docs, reg = registered_docs(tmp_path)
    assert main(["ai-summaries", str(docs), str(reg)]) == 0
    assert capsys.readouterr().out == f"No AI summaries yet for {docs}. Run ai-summarize first.\n"
    as_version_4(reg)
    assert main(["ai-summaries", str(docs), str(reg)]) == 0
    assert capsys.readouterr().out == f"No AI summaries yet for {docs}. Run ai-summarize first.\n"


def test_ai_summaries_only_reads_the_register_file(tmp_path, lm_studio):
    docs, reg = registered_docs(tmp_path)
    ai_summarize_folder(docs, reg)
    before = (reg.read_bytes(), reg.stat().st_mtime_ns)
    assert [s.place for s in saved_ai_summaries(docs, reg)] == ["letters/note.docx",
                                                                "report.docx"]
    assert (reg.read_bytes(), reg.stat().st_mtime_ns) == before


def test_ai_summaries_same_order_as_summarize_ignoring_capitals(tmp_path, lm_studio):
    docs = tmp_path / "docs"
    (docs / "letters").mkdir(parents=True)
    for place in ("Weekly.docx", "letters/note.docx", "apple.docx"):
        fake_docx(docs / place, "Text.")
    reg = tmp_path / "register.db"
    register_folder(docs, reg)
    order = ["apple.docx", "letters/note.docx", "Weekly.docx"]
    assert summarize_folder(docs, reg).summarized == order
    assert ai_summarize_folder(docs, reg).made == order
    assert [s.place for s in saved_ai_summaries(docs, reg)] == order


def test_ai_commands_have_no_window_buttons_yet():
    assert "ai-summarize" not in COMMANDS and "ai-summaries" not in COMMANDS


def test_the_commands_work_as_written(tmp_path):
    """Run the way Ernie types them. The stand-in takes LM Studio's own port,
    so this runs only when LM Studio isn't using it, as on GitHub."""
    try:
        server = StandIn(port=ai_summaries.PORT)
    except OSError:
        pytest.skip(f"port {ai_summaries.PORT} is in use, probably by LM Studio")
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        docs = tmp_path / "docs"
        docs.mkdir()
        fake_docx(docs / "odd.docx", "Risk ✓ → watch")
        reg = tmp_path / "register.db"
        command = [sys.executable, "-m", "document_manager"]
        runs = [
            subprocess.run([*command, name, str(docs), str(reg)], cwd=PROJECT,
                           capture_output=True, encoding="utf-8", errors="replace")
            for name in ("register", "ai-summarize", "ai-summaries")
        ]
    finally:
        server.shutdown()
        server.server_close()
    for done in runs:
        assert done.returncode == 0, done.stdout + done.stderr
    assert runs[1].stdout == ("AI summaries made: 1, unchanged: 0, too long: 0,"
                              " couldn't read: 0, not made: 0.\n")
    assert "odd.docx" in runs[2].stdout and "About: Risk" in runs[2].stdout
