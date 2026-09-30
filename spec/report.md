# Report and commands

**Version:** 1.1 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "03 · Lighter routine"
**Changes:** v1.1 (2026-09-29): RP-5 added, because the commands didn't work
as written. Made through a pull request.

The report puts what the check finds (spec/check.md) into plain words. Two
commands run the program, from PowerShell in the project folder:

    .venv\Scripts\python -m document_manager register <folder> <register file>
    .venv\Scripts\python -m document_manager check <folder> <register file>

| ID | Rule |
|---|---|
| RP-1 | `register` registers the folder (spec/register.md) and says how many files it listed. |
| RP-2 | `check` checks the folder (spec/check.md) and shows the report: one line with the counts, then every changed, new and missing file by its place in the folder. |
| RP-3 | When nothing has changed, the report is one line that says so. |
| RP-4 | When something goes wrong, the program says what and where in one plain line, and reports nothing as fine. |
| RP-5 | The two commands above work exactly as written. A test runs them that way. |

Example report:

    Changed: 1, new: 1, missing: 1, unchanged: 1.
      changed  letters/note.txt
      new      letters/new.txt
      missing  report.docx
