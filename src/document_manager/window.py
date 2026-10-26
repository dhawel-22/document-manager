"""The window: the commands as buttons (spec/window.md).

Kept thin: the window fills in the folder and the register file, runs the
command with run() or run_overview(), and shows the words they give back:
the same code and the same words as the commands
(src/document_manager/commands.py).
The work runs in a second thread, so the window keeps answering (WN-12).
"""

import sys
import threading
from collections.abc import Callable
from datetime import datetime
from time import monotonic

from PySide6.QtCore import QDir, Qt, QThread, Signal
from PySide6.QtGui import QCloseEvent, QColor, QFontDatabase, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QWidget,
)

from document_manager.commands import (
    COMMANDS, NOTHING_SAVED, PICKS_UP, accept, changes_to_accept, run, run_overview, stopped,
)
from document_manager.register import Counter

OPEN = "The window is open. Close it to finish."  # WN-1
WORKING = "Working…"  # WN-6
BUTTONS = (*COMMANDS, "accept", "overview")  # WN-3
ACCEPT_QUESTION = "Accept the changes shown?"  # AC-1
CLOSE_QUESTION = "Work is still running. Stop it and close the window?"  # WN-15
RED = "#d13438"  # problems (WN-7)
# The colour of each tag, found by how its lines start in the commands'
# words (WN-4). Couldn't read has two: a line in summarize's words, and the
# heading in summaries' words.
TAGS = {
    "  changed  ": "#c87000",
    "  new      ": "#2a7fd4",
    "  missing  ": RED,
    "  couldn't read  ": "#9a4fd0",
    "Couldn't read:": "#9a4fd0",
}


class Stopped(Exception):
    """Raised by the window's counter once Stop was pressed (WN-14). The
    engine counts only before it saves, so nothing is saved."""


class Work(QThread):
    """One button's work, run in a second thread so the window keeps
    answering (WN-12). Qt's signals bring the counts, and what the work gave
    back, to the window."""

    counted = Signal(int, object)  # files done, and the total (None while finding them)
    ended = Signal(object)  # what the work gave back, or the error it raised
    # The count goes to the window at most ten times a second, so showing it
    # doesn't slow the work. The first and the last count always go.
    EVERY = 0.1  # seconds

    def __init__(self, job: Callable[[Counter], object]) -> None:
        super().__init__()
        self.job = job
        self.stop_wanted = threading.Event()
        self.sent = 0.0  # when the count last went to the window

    def run(self) -> None:
        try:
            outcome = self.job(self.counter)
        except Exception as error:  # Stopped, or an error the commands don't expect
            outcome = error
        self.ended.emit(outcome)

    def counter(self, done: int, total: int | None) -> None:
        """The engine's counter (WN-13). Once Stop was pressed, it stops the
        work instead (WN-14)."""
        if self.stop_wanted.is_set():
            raise Stopped
        now = monotonic()
        if done in (0, total) or now - self.sent >= self.EVERY:
            self.sent = now
            self.counted.emit(done, total)


class Window(QWidget):
    """The two boxes, the six buttons, Stop, the results and the status line
    (WN-2 to WN-8, WN-14). The boxes start empty, and nothing is kept between
    runs (WN-10)."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Document Manager")
        self.setMinimumWidth(700)
        self.work = None  # the work running now, if any (WN-12)
        self.then = None  # what to do when it ends
        self.counting = "files"  # what the status line counts (WN-13)
        self.close_when_done = False  # Yes to closing while the work ran (WN-15)
        self.folder = QLineEdit()
        self.register_file = QLineEdit()
        self.choose_folder_button = QPushButton("Choose…")
        self.choose_folder_button.clicked.connect(self.choose_folder)
        self.choose_register_file_button = QPushButton("Choose…")
        self.choose_register_file_button.clicked.connect(self.choose_register_file)
        buttons = QHBoxLayout()
        self.command_buttons = {}
        for command in BUTTONS:
            button = QPushButton(command.capitalize())
            button.clicked.connect(lambda _checked=False, command=command: self.press(command))
            buttons.addWidget(button)
            self.command_buttons[command] = button
        buttons.addStretch()
        self.stop_button = QPushButton("Stop")  # WN-14
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop)
        buttons.addWidget(self.stop_button)
        self.results = QPlainTextEdit()
        self.results.setReadOnly(True)
        self.results.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self.status = QLabel()
        self.status.setTextFormat(Qt.TextFormat.PlainText)  # names show exactly as they are

        grid = QGridLayout(self)
        grid.addWidget(QLabel("Folder"), 0, 0)
        grid.addWidget(self.folder, 0, 1)
        grid.addWidget(self.choose_folder_button, 0, 2)
        grid.addWidget(QLabel("Register file"), 1, 0)
        grid.addWidget(self.register_file, 1, 1)
        grid.addWidget(self.choose_register_file_button, 1, 2)
        grid.addLayout(buttons, 2, 0, 1, 3)
        grid.addWidget(self.results, 3, 0, 1, 3)
        grid.addWidget(self.status, 4, 0, 1, 3)

    def choose_folder(self) -> None:
        """Fill the folder box from Windows' folder picker. Cancel changes nothing."""
        chosen = QFileDialog.getExistingDirectory(self, "Choose a folder", self.folder.text())
        if chosen:
            self.folder.setText(QDir.toNativeSeparators(chosen))

    def choose_register_file(self) -> None:
        """Fill the register file box from Windows' file picker: an existing
        register file, or a new name. The picker never asks to replace a file,
        and choosing never makes one. Cancel changes nothing."""
        chosen, _ = QFileDialog.getSaveFileName(
            self, "Choose a register file, or name a new one", self.register_file.text(),
            options=QFileDialog.Option.DontConfirmOverwrite,
        )
        if chosen:
            self.register_file.setText(QDir.toNativeSeparators(chosen))

    def press(self, command: str) -> None:
        """Start one command on the folder and register file in the boxes (WN-3)."""
        self.results.clear()  # WN-5
        folder, register_file = box_text(self.folder), box_text(self.register_file)
        boxes = [("folder box", folder), ("register file box", register_file)]
        if command == "overview":  # it uses only the register file box (OV-13)
            boxes = [("register file box", register_file)]
        empty = [name for name, text in boxes if not text]
        if empty:  # WN-8
            self.show_status(f"Fill in the {' and the '.join(empty)} first.")
            return
        self.counting = "Word documents" if command == "summarize" else "files"
        if command == "overview":  # it reads only the register file, so it counts nothing
            self.begin(lambda counter: run_overview(register_file),
                       lambda outcome: self.finish(command, register_file, outcome))
        elif command == "accept":  # the changes first, then the question (AC-1)
            self.begin(lambda counter: changes_to_accept(folder, register_file, counter),
                       lambda outcome: self.ask(folder, register_file, outcome))
        else:
            self.begin(lambda counter: run(command, folder, register_file, counter),
                       lambda outcome: self.finish(command, folder, outcome))

    def begin(self, job: Callable[[Counter], object], then: Callable[[object], None]) -> None:
        """Start the work in a second thread (WN-12). When it ends, then() is
        given what it gave back."""
        self.show_status(WORKING)  # WN-6
        self.lock(True)
        self.then = then
        self.work = Work(job)
        self.work.counted.connect(self.show_count, Qt.ConnectionType.QueuedConnection)
        self.work.ended.connect(self.ended, Qt.ConnectionType.QueuedConnection)
        self.work.start()

    def ended(self, outcome: object) -> None:
        """The work has ended: unlock, then show how it ended, or close (WN-15)."""
        self.work.wait()  # its thread is just finishing
        self.work = None
        self.lock(False)
        if self.close_when_done:
            self.close()
            return
        self.then(outcome)

    def finish(self, command: str, target: str, outcome: object) -> None:
        """Show how the work ended: its words, a problem, or stopped. The
        status line names the folder, or for Overview the register file."""
        self.results.clear()  # Accept showed the changes while it asked
        finished = datetime.now().strftime("%H:%M")
        if isinstance(outcome, Stopped):  # WN-14
            # Register and Check pick up from here next time (spec/long-runs.md)
            then = stopped(command) if command in PICKS_UP else NOTHING_SAVED
            self.show_status(f"{command.capitalize()} stopped at {finished}"
                             f" (this computer's time). {then}")
            return
        if isinstance(outcome, Exception):  # an error the commands don't expect: shown, never hidden
            outcome = 1, f"Problem: {type(outcome).__name__}: {outcome}"
        code, words = outcome
        if code:  # WN-7
            self.show_status(words, problem=True)
            return
        self.show_results(words)  # WN-4
        self.show_status(f"{command.capitalize()} finished on {target} at {finished}"
                         " (this computer's time).")

    def ask(self, folder: str, register_file: str, outcome: object) -> None:
        """Show the changes, then accept them only if Yes is clicked (AC-1).
        Nothing runs while the question is open."""
        if isinstance(outcome, Exception):  # stopped, or an error the commands don't expect
            self.finish("accept", folder, outcome)
            return
        code, words, found = outcome
        if found is None:  # nothing to accept (AC-6), or a problem
            self.finish("accept", folder, (code, words))
            return
        self.show_results(words)
        answer = QMessageBox.question(
            self, "Accept", ACCEPT_QUESTION,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            self.finish("accept", folder, (0, f"{words}\n{NOTHING_SAVED}"))
            return
        self.begin(lambda counter: accept(folder, register_file, found, counter),
                   lambda outcome: self.accepted(folder, words, outcome))

    def accepted(self, folder: str, words: str, outcome: object) -> None:
        """After Yes: the changes shown, then the accept command's last line."""
        if not isinstance(outcome, Exception):
            code, saved = outcome
            outcome = (code, saved) if code else (0, f"{words}\n{saved}")
        self.finish("accept", folder, outcome)

    def stop(self) -> None:
        """Stop the work after the file it's reading (WN-14)."""
        if self.work is not None:
            self.work.stop_wanted.set()
            self.stop_button.setEnabled(False)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Closing while the work runs asks first (WN-15). Yes stops the work,
        and the window closes once it has stopped."""
        if self.work is not None:
            answer = QMessageBox.question(
                self, "Close", CLOSE_QUESTION,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            if self.work is not None:  # it may have ended while the question was open
                self.close_when_done = True
                self.stop()
                event.ignore()
                return
        event.accept()

    def lock(self, locked: bool) -> None:
        """While the work runs, the boxes can't be changed and no button can be
        pressed except Stop (WN-6)."""
        for button in self.findChildren(QPushButton):
            button.setEnabled(not locked)
        self.stop_button.setEnabled(locked)
        self.folder.setReadOnly(locked)
        self.register_file.setReadOnly(locked)

    def show_count(self, done: int, total: int | None) -> None:
        """How far the work has got (WN-13)."""
        if total is None:
            self.show_status(f"{WORKING} {done} files found so far.")
        else:
            self.show_status(f"{WORKING} {done} of {total} {self.counting} read.")

    def show_status(self, text: str, problem: bool = False) -> None:
        """The status line; a problem shows in red (WN-7)."""
        self.status.setText(text)
        self.status.setStyleSheet(f"color: {RED}" if problem else "")

    def show_results(self, words: str) -> None:
        """The command's words, line by line, each tag in its colour (WN-4)."""
        cursor = QTextCursor(self.results.document())
        for number, line in enumerate(words.split("\n")):
            if number:
                cursor.insertBlock()
            look = QTextCharFormat()
            for start, colour in TAGS.items():
                if line.startswith(start):
                    look.setForeground(QColor(colour))
            cursor.insertText(line, look)


def box_text(box: QLineEdit) -> str:
    """A box's path, read the way PowerShell reads a typed one: without the
    spaces around it, or the quotes Windows' "Copy as path" puts around it."""
    text = box.text().strip()
    if len(text) >= 2 and text[0] == text[-1] == '"':
        text = text[1:-1]
    return text


def open_window() -> int:
    """Open the window, say so in one line, and wait until it's closed (WN-1)."""
    app = QApplication(sys.argv[:1])
    window = Window()
    window.show()
    print(OPEN, flush=True)
    return app.exec()
