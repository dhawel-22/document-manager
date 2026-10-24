"""The window: the four commands as buttons (spec/window.md).

Kept thin: the window only fills in the folder and the register file; the
work is done by the same code as the commands. So far it has the two
boxes; the buttons come next.
"""

import sys

from PySide6.QtCore import QDir
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

OPEN = "The window is open. Close it to finish."  # WN-1


class Window(QWidget):
    """The folder box and the register file box, each with "Choose…" (WN-2).
    Both start empty, and nothing is kept between runs (WN-10)."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Document Manager")
        self.setMinimumWidth(600)
        self.folder = QLineEdit()
        self.register_file = QLineEdit()
        self.choose_folder_button = QPushButton("Choose…")
        self.choose_folder_button.clicked.connect(self.choose_folder)
        self.choose_register_file_button = QPushButton("Choose…")
        self.choose_register_file_button.clicked.connect(self.choose_register_file)

        grid = QGridLayout(self)
        grid.addWidget(QLabel("Folder"), 0, 0)
        grid.addWidget(self.folder, 0, 1)
        grid.addWidget(self.choose_folder_button, 0, 2)
        grid.addWidget(QLabel("Register file"), 1, 0)
        grid.addWidget(self.register_file, 1, 1)
        grid.addWidget(self.choose_register_file_button, 1, 2)

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


def open_window() -> int:
    """Open the window, say so in one line, and wait until it's closed (WN-1)."""
    app = QApplication(sys.argv[:1])
    window = Window()
    window.show()
    print(OPEN, flush=True)
    return app.exec()
