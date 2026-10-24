"""Tests for the window, spec/window.md (WN-1, WN-2, WN-10).

The window is drawn off screen (tests/conftest.py). A test can't click
Windows' own picker, so the picker tests use a stand-in that answers the
way the picker does: the chosen path with forward slashes, or nothing
for Cancel.
"""

import subprocess
import sys
import time
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog

from document_manager.window import OPEN, Window

PROJECT = Path(__file__).resolve().parent.parent


def make_window(qtbot):
    window = Window()
    qtbot.addWidget(window)
    return window


def stand_in(monkeypatch, picker, answer):
    """Replace one of Windows' pickers with a stand-in that gives this answer."""
    monkeypatch.setattr(QFileDialog, picker, lambda *args, **kwargs: answer)


def click(qtbot, button):
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)


def test_wn1_the_command_opens_the_window(tmp_path):
    """Runs the command as written (like RP-5) and waits up to 60 seconds
    for its one line, then closes the window."""
    said = tmp_path / "said.txt"
    with said.open("w") as out:
        running = subprocess.Popen(
            [sys.executable, "-m", "document_manager", "window"],
            cwd=PROJECT, stdout=out, stderr=subprocess.STDOUT,
        )
    try:
        deadline = time.monotonic() + 60
        while OPEN not in said.read_text() and running.poll() is None:
            assert time.monotonic() < deadline, said.read_text()
            time.sleep(0.1)
    finally:
        running.kill()
        running.wait()
    assert OPEN in said.read_text().splitlines(), said.read_text()


def test_wn2_the_boxes_can_be_typed_in(qtbot):
    window = make_window(qtbot)
    qtbot.keyClicks(window.folder, r"D:\fake\docs")
    qtbot.keyClicks(window.register_file, r"D:\fake\register.db")
    assert window.folder.text() == r"D:\fake\docs"
    assert window.register_file.text() == r"D:\fake\register.db"


def test_wn2_choosing_a_folder_fills_the_box(qtbot, monkeypatch, tmp_path):
    window = make_window(qtbot)
    stand_in(monkeypatch, "getExistingDirectory", tmp_path.as_posix())
    click(qtbot, window.choose_folder_button)
    assert window.folder.text() == str(tmp_path)


def test_wn2_choosing_a_new_register_file_makes_no_file(qtbot, monkeypatch, tmp_path):
    window = make_window(qtbot)
    new = tmp_path / "register.db"
    stand_in(monkeypatch, "getSaveFileName", (new.as_posix(), ""))
    click(qtbot, window.choose_register_file_button)
    assert window.register_file.text() == str(new)
    assert list(tmp_path.iterdir()) == []


def test_wn2_choosing_an_existing_register_file_leaves_it_unchanged(qtbot, monkeypatch, tmp_path):
    window = make_window(qtbot)
    existing = tmp_path / "register.db"
    existing.write_bytes(b"fake register")
    before = existing.stat().st_mtime_ns
    stand_in(monkeypatch, "getSaveFileName", (existing.as_posix(), ""))
    click(qtbot, window.choose_register_file_button)
    assert window.register_file.text() == str(existing)
    assert existing.read_bytes() == b"fake register"
    assert existing.stat().st_mtime_ns == before


def test_wn2_cancel_changes_nothing(qtbot, monkeypatch):
    window = make_window(qtbot)
    window.folder.setText(r"D:\fake\docs")
    window.register_file.setText(r"D:\fake\register.db")
    stand_in(monkeypatch, "getExistingDirectory", "")
    stand_in(monkeypatch, "getSaveFileName", ("", ""))
    click(qtbot, window.choose_folder_button)
    click(qtbot, window.choose_register_file_button)
    assert window.folder.text() == r"D:\fake\docs"
    assert window.register_file.text() == r"D:\fake\register.db"


def test_wn10_the_boxes_start_empty_every_time(qtbot):
    first = make_window(qtbot)
    first.folder.setText(r"D:\fake\docs")
    first.register_file.setText(r"D:\fake\register.db")
    first.close()
    second = make_window(qtbot)
    assert second.folder.text() == ""
    assert second.register_file.text() == ""


def test_wn10_the_window_keeps_no_settings():
    """QSettings is Qt's store for remembering things between runs. The
    window's code never uses it."""
    code = (PROJECT / "src" / "document_manager" / "window.py").read_text(encoding="utf-8")
    assert "QSettings" not in code
