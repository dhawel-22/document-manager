"""The window: the commands as buttons (spec/window.md).

Kept thin: the window fills in the folder and the register file, runs the
command with run(), and shows the words run() gives back: the same code
and the same words as the commands (src/document_manager/commands.py).
"""

import sys
from datetime import datetime

from PySide6.QtCore import QDir, Qt
from PySide6.QtGui import QColor, QFontDatabase, QTextCharFormat, QTextCursor
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
    COMMANDS, NOTHING_SAVED, accept, changes_to_accept, run,
)

OPEN = "The window is open. Close it to finish."  # WN-1
WORKING = "Working…"  # WN-6
BUTTONS = (*COMMANDS, "accept")  # WN-3
ACCEPT_QUESTION = "Accept the changes shown?"  # AC-1
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


class Window(QWidget):
    """The two boxes, the five buttons, the results and the status line
    (WN-2 to WN-8). The boxes start empty, and nothing is kept between runs
    (WN-10)."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Document Manager")
        self.setMinimumWidth(700)
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
        """Run one command on the folder and register file in the boxes (WN-3)."""
        self.results.clear()  # WN-5
        folder, register_file = box_text(self.folder), box_text(self.register_file)
        empty = [name for name, text in (("folder box", folder),
                                         ("register file box", register_file)) if not text]
        if empty:  # WN-8
            self.show_status(f"Fill in the {' and the '.join(empty)} first.")
            return
        self.show_status(WORKING)  # WN-6
        self.lock(True)
        QApplication.processEvents()  # shows "Working…" before the work starts
        try:
            if command == "accept":
                code, words = self.accept(folder, register_file)
            else:
                code, words = run(command, folder, register_file)
        except Exception as error:  # an error the commands don't expect: shown, never hidden
            code, words = 1, f"Problem: {type(error).__name__}: {error}"
        finally:
            self.lock(False)
        self.results.clear()  # Accept showed the changes while it asked
        if code:  # WN-7
            self.show_status(words, problem=True)
            return
        self.show_results(words)  # WN-4
        finished = datetime.now().strftime("%H:%M")
        self.show_status(f"{command.capitalize()} finished on {folder} at {finished}"
                         " (this computer's time).")

    def accept(self, folder: str, register_file: str) -> tuple[int, str]:
        """Show the changes, then accept them only if Yes is clicked (AC-1).
        Returns the same words as the accept command, without its question."""
        code, words, found = changes_to_accept(folder, register_file)
        if found is None:  # nothing to accept (AC-6), or a problem
            return code, words
        self.show_results(words)
        answer = QMessageBox.question(
            self, "Accept", ACCEPT_QUESTION,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return 0, f"{words}\n{NOTHING_SAVED}"
        code, saved = accept(folder, register_file, found)
        return (code, saved) if code else (0, f"{words}\n{saved}")

    def lock(self, locked: bool) -> None:
        """While a command runs, no button can be pressed (WN-6)."""
        for button in self.findChildren(QPushButton):
            button.setEnabled(not locked)

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
