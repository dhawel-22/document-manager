"""Run the program (spec/report.md):

    python -m document_manager register <folder> <register file>
    python -m document_manager check <folder> <register file>
"""

import sqlite3
import sys

from document_manager.check import check_folder
from document_manager.register import register_folder
from document_manager.report import report

USAGE = "Use: python -m document_manager register|check <folder> <register file>"


def main(args: list[str]) -> int:
    """Run one command. Returns 0 when it worked, 1 on a problem (RP-4)."""
    if len(args) != 3 or args[0] not in ("register", "check"):
        print(USAGE)
        return 2
    command, folder, register_file = args
    try:
        if command == "register":
            count = register_folder(folder, register_file)
            print(f"Registered {folder}. Files listed: {count}.")  # RP-1
        else:
            print(report(check_folder(folder, register_file)))  # RP-2, RP-3
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Problem: {error}")  # RP-4
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
