"""Run the program (spec/report.md, spec/summaries.md, spec/window.md,
spec/accept.md, spec/overview.md, spec/long-runs.md, spec/ai-summaries.md):

    python -m document_manager register <folder> <register file>
    python -m document_manager check <folder> <register file>
    python -m document_manager summarize <folder> <register file>
    python -m document_manager summaries <folder> <register file>
    python -m document_manager accept <folder> <register file>
    python -m document_manager ai-summarize <folder> <register file>
    python -m document_manager ai-summaries <folder> <register file>
    python -m document_manager overview <register file>
    python -m document_manager window
"""

import sys

from document_manager.commands import (
    ACCEPT_QUESTION, AI_COMMANDS, AI_STOPPED, COMMANDS, NOTHING_SAVED, PICKS_UP, accept,
    changes_to_accept, run, run_overview, stopped,
)

USAGE = ("Use: python -m document_manager"
         " register|check|summarize|summaries|accept|ai-summarize|ai-summaries"
         " <folder> <register file>, or: python -m document_manager overview <register file>,"
         " or: python -m document_manager window")


def main(args: list[str]) -> int:
    """Run one command. Returns 0 when it worked, 1 on a problem (RP-4)."""
    if args == ["window"]:
        # The window's library is loaded only when the window is wanted.
        from document_manager.window import open_window

        return open_window()  # WN-1
    if len(args) == 2 and args[0] == "overview":
        code, words = run_overview(args[1])  # OV-12
        print(words)
        return code
    if len(args) != 3 or args[0] not in (*COMMANDS, "accept", *AI_COMMANDS):
        print(USAGE)
        return 2
    command, folder, register_file = args
    if command == "accept":
        return accept_command(folder, register_file)
    try:
        code, words = run(command, folder, register_file)
    except KeyboardInterrupt:  # Ctrl+C
        if command == "ai-summarize":
            print(AI_STOPPED)  # AI-7
            return 1
        if command not in PICKS_UP:
            raise
        print(f"{command.capitalize()} stopped. {stopped(command)}")  # spec/long-runs.md
        return 1
    print(words)
    return code


def accept_command(folder: str, register_file: str) -> int:
    """Show the changes, then accept them only if the answer is yes (AC-1)."""
    code, words, found = changes_to_accept(folder, register_file)
    print(words)
    if found is None:  # nothing to accept, or a problem
        return code
    try:
        answer = input(ACCEPT_QUESTION)
    except EOFError:  # no answer at all
        answer = ""
    if answer.strip().lower() != "yes":
        print(NOTHING_SAVED)
        return 0
    code, words = accept(folder, register_file, found)
    print(words)
    return code


if __name__ == "__main__":
    # Characters PowerShell can't show print as "?" instead of stopping the program.
    sys.stdout.reconfigure(errors="replace")
    sys.exit(main(sys.argv[1:]))
