"""Tests for the window's buttons, spec/window.md (WN-3 to WN-9, WN-11 to
WN-15), and the Accept button (spec/accept.md).

Some tests click the buttons on fake documents made for the tests. Others
use a stand-in for run() (src/document_manager/commands.py), to see what
the window asks for, how it looks while a command runs, or how it shows
the words it gets back.

The work runs in a second thread (WN-12), so the tests wait for it to end.
A stand-in that waits for a test goes on by itself after HOLD seconds, and
a test waits for the work at most WAIT: if the window stops answering, the
test fails instead of waiting forever.
"""

import hashlib
import re
import socket
import sys
import threading

import docx
from PySide6.QtCore import QPoint, QSize, Qt
from PySide6.QtWidgets import QMessageBox, QPushButton

from document_manager.__main__ import main
from document_manager.check import check_folder
from document_manager.commands import COMMANDS
from document_manager.fingerprint import fingerprint
from document_manager.window import (
    ACCEPT_QUESTION, BUTTONS, CLOSE_QUESTION, RED, TAGS, WORKING, Window, Work,
)

FOLDER, REGISTER = r"D:\fake\docs", r"D:\fake\register.db"
FINISHED = re.compile(r"(Register|Check|Summarize|Summaries|Accept) finished on .+ at \d\d:\d\d"
                      r" \(this computer's time\)\.")
STOPPED = re.compile(r"(Register|Check|Summarize|Summaries|Accept) stopped at \d\d:\d\d"
                     r" \(this computer's time\)\. Nothing was saved\.")
HOLD = 5  # seconds
WAIT = 10_000  # milliseconds
# fake_docs() has two files at the top and one in letters.
FOUND = [f"{WORKING} 2 files found so far.", f"{WORKING} 3 files found so far."]


def make_window(qtbot, folder=FOLDER, register_file=REGISTER):
    window = Window()
    qtbot.addWidget(window, before_close_func=lambda window: end_work(qtbot, window))
    window.folder.setText(str(folder))
    window.register_file.setText(str(register_file))
    return window


def end_work(qtbot, window):
    """Before a test's window closes: stop any work still running and wait
    for it, so even a failed test leaves no work behind."""
    window.stop()
    wait_for_work(qtbot, window)


def wait_for_work(qtbot, window):
    qtbot.waitUntil(lambda: window.work is None, timeout=WAIT)


def click(qtbot, button):
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)


def press(qtbot, window, command):
    """Click a button, then wait until its work has ended."""
    click(qtbot, window.command_buttons[command])
    wait_for_work(qtbot, window)


def can_press(window):
    """The buttons that can be pressed now."""
    return [button for button in window.findChildren(QPushButton) if button.isEnabled()]


def stand_in_run(monkeypatch, answer=(0, "Fake words."), while_running=None):
    """Replace run() with a stand-in. It notes what it was asked, does
    while_running with the window's counter, then gives this answer, or
    raises it if it's an error."""
    asked = []

    def stand_in(command, folder, register_file, counter):
        asked.append((command, folder, register_file))
        if while_running:
            while_running(counter)
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


def statuses(monkeypatch, window):
    """Note every status line the window shows, in order."""
    said = []
    show = window.show_status
    monkeypatch.setattr(window, "show_status",
                        lambda text, problem=False: said.append(text) or show(text, problem))
    return said


def stop_while_reading(qtbot, monkeypatch, window, command, module):
    """Click a button, and press Stop while the engine (in this module) reads
    its first file. Then wait until the work has ended."""
    reading, go_on = threading.Event(), threading.Event()

    def held(path):
        if not reading.is_set():
            reading.set()
            go_on.wait(HOLD)
        return fingerprint(path)

    monkeypatch.setattr(f"document_manager.{module}.fingerprint", held)
    click(qtbot, window.command_buttons[command])
    qtbot.waitUntil(reading.is_set, timeout=WAIT)
    click(qtbot, window.stop_button)
    go_on.set()
    wait_for_work(qtbot, window)


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
    go_on = threading.Event()
    stand_in_run(monkeypatch, (0, "New words."), lambda counter: go_on.wait(HOLD))
    window.results.setPlainText("Old words.")
    click(qtbot, window.command_buttons["check"])
    assert window.results.toPlainText() == ""
    go_on.set()
    wait_for_work(qtbot, window)
    assert window.results.toPlainText() == "New words."


def test_wn6_working_while_a_command_runs(qtbot, monkeypatch):
    window = make_window(qtbot)
    go_on = threading.Event()
    stand_in_run(monkeypatch, while_running=lambda counter: go_on.wait(HOLD))
    click(qtbot, window.command_buttons["check"])
    assert window.status.text() == WORKING
    assert can_press(window) == [window.stop_button]
    qtbot.keyClicks(window.folder, "typed while working")
    qtbot.keyClicks(window.register_file, "typed while working")
    assert (window.folder.text(), window.register_file.text()) == (FOLDER, REGISTER)
    go_on.set()
    wait_for_work(qtbot, window)
    assert window.stop_button not in can_press(window)
    assert len(can_press(window)) == len(BUTTONS) + 2  # and the two Choose… buttons
    assert not window.folder.isReadOnly() and not window.register_file.isReadOnly()
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
    assert len(can_press(window)) == len(BUTTONS) + 2


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


def answer_question(monkeypatch, answer):
    """Click this answer in the window's question box. Notes what the box asked."""
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
    asked = answer_question(monkeypatch, QMessageBox.StandardButton.Yes)
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
    answer_question(monkeypatch, QMessageBox.StandardButton.No)
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
    answer_question(monkeypatch, AssertionError("asked when nothing had changed"))
    press(qtbot, window, "accept")
    assert window.results.toPlainText() == "Nothing has changed. Files checked: 3."
    assert FINISHED.fullmatch(window.status.text())


def test_accept_a_problem_shows_in_red(qtbot, tmp_path, monkeypatch):
    docs = fake_docs(tmp_path)
    answer_question(monkeypatch, AssertionError("asked when there was a problem"))
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


def test_wn12_the_window_keeps_answering_while_the_work_runs(qtbot, monkeypatch):
    window = make_window(qtbot)
    window.show()
    go_on = threading.Event()
    stand_in_run(monkeypatch, while_running=lambda counter: go_on.wait(HOLD))
    click(qtbot, window.command_buttons["check"])
    assert window.work.isRunning()  # the click came back while the work runs
    window.move(40, 50)
    window.resize(900, 600)
    window.results.setPlainText("\n".join(f"Line {number}" for number in range(200)))
    bar = window.results.verticalScrollBar()
    bar.setValue(bar.maximum())
    qtbot.waitUntil(lambda: window.pos() == QPoint(40, 50) and window.size() == QSize(900, 600))
    assert bar.value() == bar.maximum() > 0
    assert window.work.isRunning()
    go_on.set()
    wait_for_work(qtbot, window)


def test_wn13_the_status_line_counts(qtbot, tmp_path, monkeypatch):
    docs = fake_docs(tmp_path)  # two of the three files are Word documents
    window = make_window(qtbot, docs, tmp_path / "register.db")
    monkeypatch.setattr(Work, "EVERY", 0)  # every count goes to the window
    said = statuses(monkeypatch, window)
    press(qtbot, window, "register")
    assert said[:-1] == [WORKING, *FOUND, *(f"{WORKING} {n} of 3 files read." for n in range(4))]
    said.clear()
    press(qtbot, window, "summarize")
    assert said[:-1] == [WORKING, *FOUND,
                         *(f"{WORKING} {n} of 2 Word documents read." for n in range(3))]
    said.clear()
    press(qtbot, window, "summaries")  # it reads only the register file
    assert said[:-1] == [WORKING]
    assert FINISHED.fullmatch(said[-1])


def test_wn13_accept_counts_twice(qtbot, tmp_path, monkeypatch):
    docs, reg, window = registered_and_changed(qtbot, tmp_path)
    answer_question(monkeypatch, QMessageBox.StandardButton.Yes)
    monkeypatch.setattr(Work, "EVERY", 0)  # every count goes to the window
    said = statuses(monkeypatch, window)
    press(qtbot, window, "accept")
    reading = [WORKING, *FOUND, *(f"{WORKING} {n} of 3 files read." for n in range(4))]
    assert said[:-1] == reading + reading
    assert FINISHED.fullmatch(said[-1])


def test_wn13_the_count_changes_at_most_ten_times_a_second(qtbot, tmp_path, monkeypatch):
    docs = fake_docs(tmp_path)
    window = make_window(qtbot, docs, tmp_path / "register.db")
    monkeypatch.setattr("document_manager.window.monotonic", lambda: 1000.0)  # time stands still
    said = statuses(monkeypatch, window)
    press(qtbot, window, "register")
    assert said[:-1] == [WORKING, f"{WORKING} 2 files found so far.",  # the first count
                         f"{WORKING} 0 of 3 files read.", f"{WORKING} 3 of 3 files read."]


def test_wn14_stop_stops_the_work_and_nothing_is_saved(qtbot, monkeypatch):
    window = make_window(qtbot)
    go_on = threading.Event()

    def counting(counter):
        counter(0, 3)
        go_on.wait(HOLD)
        counter(1, 3)  # Stop was pressed: the work stops here

    stand_in_run(monkeypatch, while_running=counting)
    click(qtbot, window.command_buttons["check"])
    qtbot.waitUntil(lambda: window.status.text() == f"{WORKING} 0 of 3 files read.")
    click(qtbot, window.stop_button)
    assert not window.stop_button.isEnabled()
    go_on.set()
    wait_for_work(qtbot, window)
    assert STOPPED.fullmatch(window.status.text())
    assert window.status.text().startswith("Check stopped at ")
    assert RED not in window.status.styleSheet()
    assert window.results.toPlainText() == ""


def test_wn14_stop_too_late_the_work_finishes_as_usual(qtbot, monkeypatch):
    window = make_window(qtbot)
    go_on = threading.Event()

    def counting(counter):
        counter(3, 3)  # every file was read
        go_on.wait(HOLD)  # and now it's saving

    stand_in_run(monkeypatch, while_running=counting)
    click(qtbot, window.command_buttons["check"])
    qtbot.waitUntil(lambda: window.status.text() == f"{WORKING} 3 of 3 files read.")
    click(qtbot, window.stop_button)
    go_on.set()
    wait_for_work(qtbot, window)
    assert FINISHED.fullmatch(window.status.text())
    assert window.results.toPlainText() == "Fake words."


def test_wn14_a_stopped_register_makes_no_register_file(qtbot, tmp_path, monkeypatch):
    docs = fake_docs(tmp_path)
    reg = tmp_path / "register.db"
    window = make_window(qtbot, docs, reg)
    stop_while_reading(qtbot, monkeypatch, window, "register", "register")
    assert window.status.text().startswith("Register stopped at ")
    assert not reg.exists()


def test_wn14_a_stopped_summarize_saves_nothing(qtbot, tmp_path, monkeypatch):
    docs = fake_docs(tmp_path)
    reg = tmp_path / "register.db"
    window = make_window(qtbot, docs, reg)
    press(qtbot, window, "register")
    before = reg.read_bytes()
    stop_while_reading(qtbot, monkeypatch, window, "summarize", "summaries")
    assert window.status.text().startswith("Summarize stopped at ")
    assert reg.read_bytes() == before


def test_wn14_a_stopped_accept_saves_nothing(qtbot, tmp_path, monkeypatch):
    docs, reg, window = registered_and_changed(qtbot, tmp_path)
    before = reg.read_bytes()
    answer_question(monkeypatch, QMessageBox.StandardButton.Yes)
    # Accept's second reading, after Yes, is the one held and stopped.
    stop_while_reading(qtbot, monkeypatch, window, "accept", "register")
    assert window.status.text().startswith("Accept stopped at ")
    assert window.results.toPlainText() == ""
    assert reg.read_bytes() == before


def test_wn15_closing_while_nothing_runs_asks_nothing(qtbot, monkeypatch):
    window = make_window(qtbot)
    window.show()
    answer_question(monkeypatch, AssertionError("asked when nothing was running"))
    window.close()
    assert not window.isVisible()


def test_wn15_closing_while_the_work_runs_asks_first(qtbot, monkeypatch):
    window = make_window(qtbot)
    window.show()
    go_on = threading.Event()
    stand_in_run(monkeypatch, while_running=lambda counter: go_on.wait(HOLD))
    asked = answer_question(monkeypatch, QMessageBox.StandardButton.No)
    click(qtbot, window.command_buttons["check"])
    window.close()
    [(_, _, question, _, picked)] = asked
    assert question == CLOSE_QUESTION
    assert picked == QMessageBox.StandardButton.No  # No unless Yes is clicked
    assert window.isVisible()  # No: the window stays open, and the work goes on
    go_on.set()
    wait_for_work(qtbot, window)
    assert FINISHED.fullmatch(window.status.text())


def test_wn15_yes_stops_the_work_then_closes(qtbot, monkeypatch):
    window = make_window(qtbot)
    window.show()
    go_on = threading.Event()
    stopped = []

    def counting(counter):
        go_on.wait(HOLD)
        try:
            counter(1, 3)
        except Exception as error:
            stopped.append(type(error).__name__)
            raise

    stand_in_run(monkeypatch, while_running=counting)
    answer_question(monkeypatch, QMessageBox.StandardButton.Yes)
    click(qtbot, window.command_buttons["check"])
    window.close()
    assert window.isVisible()  # it closes once the work has stopped
    go_on.set()
    qtbot.waitUntil(lambda: not window.isVisible(), timeout=WAIT)
    assert stopped == ["Stopped"]
    assert window.work is None


def test_wn15_yes_after_the_work_ended_closes_at_once(qtbot, monkeypatch):
    window = make_window(qtbot)
    window.show()
    go_on = threading.Event()
    stand_in_run(monkeypatch, while_running=lambda counter: go_on.wait(HOLD))

    def ended_while_asking(*args):
        go_on.set()
        wait_for_work(qtbot, window)
        return QMessageBox.StandardButton.Yes

    monkeypatch.setattr(QMessageBox, "question", ended_while_asking)
    click(qtbot, window.command_buttons["check"])
    window.close()
    assert not window.isVisible()
