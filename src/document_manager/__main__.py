"""Run the program (spec/report.md, spec/summaries.md, spec/window.md):

    python -m document_manager register <folder> <register file>
    python -m document_manager check <folder> <register file>
    python -m document_manager summarize <folder> <register file>
    python -m document_manager summaries <folder> <register file>
    python -m document_manager window
"""

import sys

from document_manager.commands import COMMANDS, run

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
    code, words = run(command, folder, register_file)
    print(words)
    return code


if __name__ == "__main__":
    # Characters PowerShell can't show print as "?" instead of stopping the program.
    sys.stdout.reconfigure(errors="replace")
    sys.exit(main(sys.argv[1:]))
