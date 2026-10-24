"""The commands' words, made in one place (spec/report.md, spec/summaries.md).

The commands print these words and the window shows them, so both always
say exactly the same (spec/window.md, WN-3, WN-4).
"""

import sqlite3

from document_manager.check import check_folder
from document_manager.register import register_folder
from document_manager.report import report
from document_manager.summaries import saved_summaries, summarize_folder
from document_manager.summary_report import summaries_report, summarize_report

COMMANDS = ("register", "check", "summarize", "summaries")


def run(command: str, folder: str, register_file: str) -> tuple[int, str]:
    """Run one command. Returns 0 and its words when it worked, or 1 and one
    plain line when there was a problem (RP-4)."""
    try:
        if command == "register":
            count = register_folder(folder, register_file)
            return 0, f"Registered {folder}. Files listed: {count}."  # RP-1
        if command == "check":
            return 0, report(check_folder(folder, register_file))  # RP-2, RP-3
        if command == "summarize":
            return 0, summarize_report(summarize_folder(folder, register_file))
        if command == "summaries":
            return 0, summaries_report(folder, saved_summaries(folder, register_file))  # SM-8
        raise ValueError(f"Unknown command: {command}")
    except (OSError, ValueError, sqlite3.Error) as error:
        return 1, f"Problem: {error}"  # RP-4
