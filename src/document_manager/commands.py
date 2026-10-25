"""The commands' words, made in one place (spec/report.md, spec/summaries.md,
spec/accept.md).

The commands print these words and the window shows them, so both always
say exactly the same (spec/window.md, WN-3, WN-4).
"""

import sqlite3

from document_manager.accept import accept_folder
from document_manager.check import CheckResult, check_folder
from document_manager.register import Counter, register_folder
from document_manager.report import report
from document_manager.summaries import saved_summaries, summarize_folder
from document_manager.summary_report import summaries_report, summarize_report

COMMANDS = ("register", "check", "summarize", "summaries")
PROBLEMS = (OSError, ValueError, sqlite3.Error)
ACCEPT_QUESTION = "Accept these changes? Type yes to accept: "
NOTHING_SAVED = "Nothing was saved."


def run(command: str, folder: str, register_file: str,
        counter: Counter | None = None) -> tuple[int, str]:
    """Run one command. Returns 0 and its words when it worked, or 1 and one
    plain line when there was a problem (RP-4). Only the window passes a
    counter (spec/window.md, WN-13); Summaries reads only the register file,
    so it has nothing to count."""
    try:
        if command == "register":
            count = register_folder(folder, register_file, counter)
            return 0, f"Registered {folder}. Files listed: {count}."  # RP-1
        if command == "check":
            return 0, report(check_folder(folder, register_file, counter))  # RP-2, RP-3
        if command == "summarize":
            return 0, summarize_report(summarize_folder(folder, register_file, counter))
        if command == "summaries":
            return 0, summaries_report(folder, saved_summaries(folder, register_file))  # SM-8
        raise ValueError(f"Unknown command: {command}")
    except PROBLEMS as error:
        return 1, f"Problem: {error}"  # RP-4


def changes_to_accept(folder: str, register_file: str,
                      counter: Counter | None = None) -> tuple[int, str, CheckResult | None]:
    """What accepting would take, in the check's words (AC-1). The result is
    None when there is nothing to accept (AC-6) or a problem (RP-4)."""
    try:
        found = check_folder(folder, register_file, counter)
    except PROBLEMS as error:
        return 1, f"Problem: {error}", None
    if not (found.changed or found.new or found.missing):
        return 0, report(found), None
    return 0, report(found), found


def accept(folder: str, register_file: str, shown: CheckResult,
           counter: Counter | None = None) -> tuple[int, str]:
    """Accept the changes the person was shown and said yes to (AC-2)."""
    try:
        count = accept_folder(folder, register_file, shown, counter)
    except PROBLEMS as error:
        return 1, f"Problem: {error}"  # RP-4
    return 0, f"Accepted {folder}. Files listed: {count}."
