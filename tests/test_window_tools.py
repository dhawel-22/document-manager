"""Test that the window tools work (D-022, spec/window.md).

The tools are PySide6, which draws windows, and pytest-qt, which clicks
through them. This test makes one fake button, clicks it, and checks that
the click arrived. It also checks that the button is drawn off screen
(tests/conftest.py).
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QPushButton


def test_clicks_a_fake_button(qtbot):
    clicks = []
    button = QPushButton("Fake button")
    button.clicked.connect(lambda: clicks.append("clicked"))
    qtbot.addWidget(button)

    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert clicks == ["clicked"]
    assert QApplication.platformName() == "offscreen"
