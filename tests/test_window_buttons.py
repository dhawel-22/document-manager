"""Tests for the window's buttons, spec/window.md (WN-3 to WN-9, WN-11),
and the Accept button (spec/accept.md).

Some tests click the buttons on fake documents made for the tests. Others
use a stand-in for run() (src/document_manager/commands.py), to see what
the window asks for, how it looks while a command runs, or how it shows
the words it gets back.
"""

import hashlib
import re
import socket
import sys

import docx
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox, QPushButton

from document_manager.__main__ import main
from document_manager.check import check_folder
from document_manager.commands import COMMANDS
from document_manager.window import ACCEPT_QUESTION, BUTTONS, RED, TAGS, WORKING, Window

FOLDER, REGISTER = r"D:\fake\docs", r"D:\fake\register.db"
FINISHED = re.compile(r"(Register|Check|Summarize|Summaries|Accept) finished on .+ at \d\d:\d\d"
                      r" \(this computer's time\)\.")


def make_window(qtbot, folder=FOLDER, register_file=REGISTER):
    window = Window()
    qtbot.addWidget(window)
    window.folder.setText(str(folder))
    window.register_file.setText(str(register_file))
    return window


def press(qtbot, window, command):
    qtbot.mouseClick(window.command_buttons[command], Qt.MouseButton.LeftButton)


def stand_in_run(monkeypatch, answer=(0, "Fake words."), while_running=None):
    """Replace run() with a stand-in. It notes what it was asked, looks at
    the window while it runs, then gives this answer, or raises it if it's
    an error."""
    asked = []

    def stand_in(*args):
        asked.append(args)
        if while_running:
            while_running()
        if isinstance(answer, Exception):
            raise answer
        return answer

    monkeypatch.setattr("document_manager.window.run", stand_in)
    return asked


def fake_docs(tmp_path):
    """A small folder of fake documents: two Word documents and a text file."""
    docs = tmp_path / "docs"
    (docs / "letters").mkdir(parents=True)
    for path, title in ((docs / "report.docx", "Report"), (docs / "letters" / "note.docx", "Note")):
        made = docx.Document()
        made.core_properties.title = title
        made.add_paragraph("A fake document for the tests.")
        made.save(path)
    (docs / "notes.txt").write_bytes(b"not a Word document\n")
    return docs


def every_file(docs):
    """Each fake document's fingerprint and last-changed time."""
    return {path: (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns)
            for path in docs.rglob("*") if path.is_file()}


def colours(window):
    """The colour of each results line (None: the usual colour)."""
    found = []
    block = window.results.document().begin()
    while block.isValid():
        brush = block.begin().fragment().charFormat().foreground()
        found.append(None if brush.style() == Qt.BrushStyle.NoBrush else brush.color().name())
        block = block.next()
    return found


def test_wn3_each_button_runs_its_command(qtbot, monkeypatch):
    asked = stand_in_run(monkeypatch)
    window = make_window(qtbot)
    for command in COMMANDS:
        press(qtbot, window, command)
    assert asked == [(command, FOLDER, REGISTER) for command in COMMANDS]


def test_wn3_spaces_and_quotes_around_a_path_are_left_out(qtbot, monkeypatch):
    asked = stand_in_run(monkeypatch)
    window = make_window(qtbot, f'  "{FOLDER}"  ', f'"{REGISTER}"')
    press(qtbot, window, "check")
    assert asked == [("check", FOLDER, REGISTER)]


def test_wn3_wn4_the_buttons_show_the_commands_words(qtbot, tmp_path, capsys):
    docs = fake_docs(tmp_path)
    reg = tmp_path / "register.db"
    window = make_window(qtbot, docs, reg)
    press(qtbot, window, "register")
    assert window.results.toPlainText() == f"Registered {docs}. Files listed: 3."
    press(qtbot, window, "summarize")
    assert window.results.toPlainText() == "Summarized: 2, unchanged: 0, couldn't read: 0."
    (docs / "notes.txt").write_bytes(b"changed\n")
    for command in ("check", "summaries"):  # these only read, so the command can run after
        press(qtbot, window, command)
        main([command, str(docs), str(reg)])
        assert capsys.readouterr().out == window.results.toPlainText() + "\n"


def test_wn4_each_tag_has_its_own_colour(qtbot, monkeypatch):
    lines = ["Changed: 1, new: 1, missing: 1, unchanged: 0.", "  changed  a.txt",
             "  new      b.txt", "  missing  c.txt", "  couldn't read  d.docx  old Word file",
             "Couldn't read:"]
    stand_in_run(monkeypatch, (0, "\n".join(lines)))
    window = make_window(qtbot)
    press(qtbot, window, "check")
    assert window.results.toPlainText() == "\n".join(lines)
    assert colours(window) == [None, *TAGS.values()]
    assert len(set(TAGS.values())) == 4  # changed, new, missing, couldn't read


def test_wn5_old_results_are_cleared_first(qtbot, monkeypatch):
    window = make_window(qtbot)
    seen = []
    stand_in_run(monkeypatch, (0, "New words."), lambda: seen.append(window.results.toPlainText()))
    window.results.setPlainText("Old words.")
    press(qtbot, window, "check")
    assert seen == [""]
    assert window.results.toPlainText() == "New words."


def test_wn6_working_while_a_command_runs(qtbot, monkeypatch):
    window = make_window(qtbot)
    buttons = window.findChildren(QPushButton)
    seen = []
    stand_in_run(monkeypatch, while_running=lambda: seen.append(
        (window.status.text(), [button.isEnabled() for button in buttons])))
    press(qtbot, window, "check")
    assert seen == [(WORKING, [False] * 7)]
    assert all(button.isEnabled() for button in buttons)
    assert FINISHED.fullmatch(window.status.text())
    assert window.status.text().startswith(f"Check finished on {FOLDER} at ")


def test_wn7_a_problem_shows_in_red_and_the_results_stay_empty(qtbot, tmp_path, capsys):
    docs = fake_docs(tmp_path)
    reg = tmp_path / "register.db"  # not made yet, so the check can't read it
    window = make_window(qtbot, docs, reg)
    window.results.setPlainText("Old words.")
    press(qtbot, window, "check")
    main(["check", str(docs), str(reg)])
    assert capsys.readouterr().out == window.status.text() + "\n"
    assert window.status.text().startswith("Problem: ")
    assert RED in window.status.styleSheet()
    assert window.results.toPlainText() == ""


def test_wn7_an_error_the_commands_dont_expect_is_shown_too(qtbot, monkeypatch):
    stand_in_run(monkeypatch, RuntimeError("a fake fault"))
    window = make_window(qtbot)
    press(qtbot, window, "check")
    assert window.status.text() == "Problem: RuntimeError: a fake fault"
    assert RED in window.status.styleSheet()
    assert window.results.toPlainText() == ""
    assert all(button.isEnabled() for button in window.findChildren(QPushButton))


def test_wn8_an_empty_box_is_named_and_nothing_runs(qtbot, monkeypatch):
    asked = stand_in_run(monkeypatch)
    window = make_window(qtbot, "", "")
    press(qtbot, window, "check")
    assert window.status.text() == "Fill in the folder box and the register file box first."
    window.folder.setText(FOLDER)
    press(qtbot, window, "check")
    assert window.status.text() == "Fill in the register file box first."
    window.folder.setText("   ")
    window.register_file.setText(REGISTER)
    press(qtbot, window, "check")
    assert window.status.text() == "Fill in the folder box first."
    assert asked == []


def test_wn9_the_documents_are_never_changed(qtbot, tmp_path):
    docs = fake_docs(tmp_path)
    reg = tmp_path / "register.db"
    before = every_file(docs)
    window = make_window(qtbot, docs, reg)
    for command in BUTTONS:
        press(qtbot, window, command)
        assert FINISHED.fullmatch(window.status.text()), window.status.text()
    assert every_file(docs) == before
    assert sorted(path.name for path in tmp_path.iterdir()) == ["docs", "register.db"]


def test_wn11_nothing_leaves_this_computer(qtbot, tmp_path, monkeypatch):
    docs = fake_docs(tmp_path)

    def no_network(*args, **kwargs):
        raise AssertionError("tried to use the network")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)
    window = make_window(qtbot, docs, tmp_path / "register.db")
    for command in BUTTONS:
        press(qtbot, window, command)
        assert FINISHED.fullmatch(window.status.text()), window.status.text()
    assert "PySide6.QtNetwork" not in sys.modules  # Qt's own network part is never loaded


def answer_accept(monkeypatch, answer):
    """Click this answer in Accept's question box. Notes what the box asked."""
    asked = []

    def stand_in(*args):
        asked.append(args)
        if isinstance(answer, Exception):
            raise answer
        return answer

    monkeypatch.setattr(QMessageBox, "question", stand_in)
    return asked


def registered_and_changed(qtbot, tmp_path):
    docs = fake_docs(tmp_path)
    reg = tmp_path / "register.db"
    window = make_window(qtbot, docs, reg)
    press(qtbot, window, "register")
    (docs / "notes.txt").write_bytes(b"changed\n")
    return docs, reg, window


def test_accept_yes_saves_and_says_so(qtbot, tmp_path, monkeypatch):
    docs, reg, window = registered_and_changed(qtbot, tmp_path)
    asked = answer_accept(monkeypatch, QMessageBox.StandardButton.Yes)
    press(qtbot, window, "accept")
    assert window.results.toPlainText() == (
        "Changed: 1, new: 0, missing: 0, unchanged: 2.\n"
        "  changed  notes.txt\n"
        f"Accepted {docs}. Files listed: 3."
    )
    assert FINISHED.fullmatch(window.status.text())
    assert check_folder(docs, reg).changed == []
    [(_, _, question, _, picked)] = asked
    assert question == ACCEPT_QUESTION
    assert picked == QMessageBox.StandardButton.No  # No unless Yes is clicked


def test_accept_no_saves_nothing(qtbot, tmp_path, monkeypatch):
    docs, reg, window = registered_and_changed(qtbot, tmp_path)
    before = reg.read_bytes()
    answer_accept(monkeypatch, QMessageBox.StandardButton.No)
    press(qtbot, window, "accept")
    assert window.results.toPlainText().endswith("  changed  notes.txt\nNothing was saved.")
    assert reg.read_bytes() == before


def test_accept_shows_the_changes_while_it_asks(qtbot, tmp_path, monkeypatch):
    docs, reg, window = registered_and_changed(qtbot, tmp_path)
    seen = []
    monkeypatch.setattr(QMessageBox, "question", lambda *args: seen.append(
        window.results.toPlainText()) or QMessageBox.StandardButton.No)
    press(qtbot, window, "accept")
    assert seen == ["Changed: 1, new: 0, missing: 0, unchanged: 2.\n  changed  notes.txt"]


def test_accept_nothing_changed_doesnt_ask(qtbot, tmp_path, monkeypatch):
    docs = fake_docs(tmp_path)
    window = make_window(qtbot, docs, tmp_path / "register.db")
    press(qtbot, window, "register")
    answer_accept(monkeypatch, AssertionError("asked when nothing had changed"))
    press(qtbot, window, "accept")
    assert window.results.toPlainText() == "Nothing has changed. Files checked: 3."
    assert FINISHED.fullmatch(window.status.text())


def test_accept_a_problem_shows_in_red(qtbot, tmp_path, monkeypatch):
    docs = fake_docs(tmp_path)
    answer_accept(monkeypatch, AssertionError("asked when there was a problem"))
    window = make_window(qtbot, docs, tmp_path / "register.db")  # not made yet
    press(qtbot, window, "accept")
    assert window.status.text().startswith("Problem: ")
    assert RED in window.status.styleSheet()
    assert window.results.toPlainText() == ""
    assert not (tmp_path / "register.db").exists()


def test_accept_folder_changed_while_asking_saves_nothing(qtbot, tmp_path, monkeypatch):
    docs, reg, window = registered_and_changed(qtbot, tmp_path)
    before = reg.read_bytes()
    monkeypatch.setattr(QMessageBox, "question", lambda *args: (
        (docs / "report.docx").write_bytes(b"changed while asking")
        and QMessageBox.StandardButton.Yes))
    press(qtbot, window, "accept")
    assert window.status.text().startswith("Problem: ")
    assert "AC-1" in window.status.text()
    assert window.results.toPlainText() == ""
    assert reg.read_bytes() == before
