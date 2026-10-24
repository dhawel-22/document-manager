"""Run the program (spec/report.md, spec/summaries.md, spec/window.md):

    python -m document_manager register <folder> <register file>
    python -m document_manager check <folder> <register file>
    python -m document_manager summarize <folder> <register file>
    python -m document_manager summaries <folder> <register file>
    python -m document_manager window
"""

import sqlite3
import sys

from document_manager.check import check_folder
from document_manager.register import register_folder
from document_manager.report import report
from document_manager.summaries import saved_summaries, summarize_folder
from document_manager.summary_report import summaries_report, summarize_report

COMMANDS = ("register", "check", "summarize", "summaries")
USAGE = ("Use: python -m document_manager register|check|summarize|summaries"
         " <folder> <register file>, or: python -m document_manager window")


def main(args: list[str]) -> int:
    """Run one command. Returns 0 when it worked, 1 on a problem (RP-4)."""
    if args == ["window"]:
        # The window's library is loaded only when the window is wanted.
        from document_manager.window import open_window

        return open_window()  # WN-1
    if len(args) != 3 or args[0] not in COMMANDS:
        print(USAGE)
        return 2
    command, folder, register_file = args
    try:
        if command == "register":
            count = register_folder(folder, register_file)
            print(f"Registered {folder}. Files listed: {count}.")  # RP-1
        elif command == "check":
            print(report(check_folder(folder, register_file)))  # RP-2, RP-3
        elif command == "summarize":
            print(summarize_report(summarize_folder(folder, register_file)))
        else:
            print(summaries_report(folder, saved_summaries(folder, register_file)))  # SM-8
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Problem: {error}")  # RP-4
        return 1
    return 0


if __name__ == "__main__":
    # Characters the window can't show print as "?" instead of stopping the program.
    sys.stdout.reconfigure(errors="replace")
    sys.exit(main(sys.argv[1:]))
