"""The commands' words, made in one place (spec/report.md, spec/summaries.md,
spec/accept.md, spec/overview.md, spec/busy-folders.md, spec/long-runs.md).

The commands print these words and the window shows them, so both always
say exactly the same (spec/window.md, WN-3, WN-4).
"""

import sqlite3

from document_manager.accept import accept_folder
from document_manager.check import CheckResult, check_folder
from document_manager.overview import overview
from document_manager.overview_report import overview_report
from document_manager.progress import PickedUp
from document_manager.register import Counter, Files, register_folder
from document_manager.report import report
from document_manager.summaries import saved_summaries, summarize_folder
from document_manager.summary_report import summaries_report, summarize_report

COMMANDS = ("register", "check", "summarize", "summaries")
PICKS_UP = ("register", "check")  # the runs that pick up after a stop (LR-8)
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
            files = register_folder(folder, register_file, counter)
            return 0, picked_up(files.picked_up) + listed("Registered", folder, files)  # RP-1
        if command == "check":
            found = check_folder(folder, register_file, counter)
            return 0, picked_up(found.picked_up) + report(found)  # RP-2, RP-3
        if command == "summarize":
            return 0, summarize_report(summarize_folder(folder, register_file, counter))
        if command == "summaries":
            return 0, summaries_report(folder, saved_summaries(folder, register_file))  # SM-8
        raise ValueError(f"Unknown command: {command}")
    except PROBLEMS as error:
        return 1, f"Problem: {error}"  # RP-4


def run_overview(register_file: str) -> tuple[int, str]:
    """The overview of every folder in the register file (OV-12), or one
    plain line when there is a problem (OV-11). It reads only the register
    file, so it has nothing to count."""
    try:
        return 0, overview_report(register_file, overview(register_file))
    except PROBLEMS as error:
        return 1, f"Problem: {error}"  # RP-4


def changes_to_accept(folder: str, register_file: str,
                      counter: Counter | None = None) -> tuple[int, str, CheckResult | None]:
    """What accepting would take, in the check's words (AC-1). The result is
    None when there is nothing to accept (AC-6) or a problem (RP-4)."""
    try:
        found = check_folder(folder, register_file, counter, pick_up=False)  # LR-8
    except PROBLEMS as error:
        return 1, f"Problem: {error}", None
    if not (found.changed or found.new or found.missing):
        if found.could_not_read:  # they aren't changes, so nothing is asked (BF-9)
            return 0, f"{report(found)}\n{NOTHING_SAVED}", None
        return 0, report(found), None
    return 0, report(found), found


def accept(folder: str, register_file: str, shown: CheckResult,
           counter: Counter | None = None) -> tuple[int, str]:
    """Accept the changes the person was shown and said yes to (AC-2)."""
    try:
        files = accept_folder(folder, register_file, shown, counter)
    except PROBLEMS as error:
        return 1, f"Problem: {error}"  # RP-4
    return 0, listed("Accepted", folder, files)


def listed(done: str, folder: str, files: Files) -> str:
    """How many files a new list holds (RP-1, AC-2), then each one that
    couldn't be read, with the reason (spec/busy-folders.md, Details)."""
    if not files.unread:
        return f"{done} {folder}. Files listed: {files.count}."
    lines = [f"{done} {folder}. Files listed: {files.count}, couldn't read: {len(files.unread)}."]
    lines += [f"  couldn't read  {place}  {why}"
              for place, why in sorted((place, why) for place, _size, why in files.unread)]
    return "\n".join(lines)


def picked_up(picked: PickedUp | None) -> str:
    """The line before a run's words when it picked up where the run before
    it stopped (LR-4); nothing when it didn't."""
    if picked is None:
        return ""
    at = f"{picked.stopped_at[:10]} {picked.stopped_at[11:16]} UTC"
    kept = f"{picked.kept} file{'' if picked.kept == 1 else 's'} kept"
    return f"Picked up the run that stopped at {at}: {kept}, {picked.read_again} read again.\n"


def stopped(command: str) -> str:
    """What's said when Register or Check stops before it finishes
    (spec/long-runs.md, Details)."""
    return (f"The register file wasn't changed; the next {command.capitalize()}"
            " on this folder picks up from here.")
