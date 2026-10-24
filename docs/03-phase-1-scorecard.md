# Document Manager: Phase 1 scorecard

**Version:** 1.0 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "07 · The project's own documents"

Phase 1 (opening document, section 5): the window, kept thin, with all
the work in the engine; then the project's own documents. Each phase must
pass a clean scorecard before the next one starts.

## 1. Steps

| Step | Result |
|---|---|
| 1. Automatic checks on GitHub | Done (#47), thread 05 |
| 2. The window's toolkit | PySide6, tested with pytest-qt (D-022, #49); both at exact versions (#52) |
| 3. The window's rules | spec/window.md v1.2, WN-1 to WN-11 (#51, #53, #55) |
| 4. The window | Done (#53 to #55), thread 06 |
| 5. Demo on fake documents | Passed, thread 06 |
| 6. GitHub waits for the green tick | Saved 2026-10-23; one check left (section 3) |
| 7. The project's own documents | Registered and checked 2026-10-23; one check left (section 3) |
| 8. Scorecard | This file |

## 2. Evidence
- Automatic checks: all 20 check runs so far have passed (read from
  GitHub on 2026-10-23). For main at e65e061, 85 tests passed on
  GitHub's computer.
- Every window rule has at least one test: WN-1, WN-2 and WN-10 in
  tests/test_window.py; WN-3 to WN-9 and WN-11 in
  tests/test_window_buttons.py.
- Kept thin: the window uses only run() from commands.py, the same code
  the commands use. For WN-3 and WN-4, the tests check that the window
  shows the commands' exact words.
- GitHub waits for the tick: the rule set protect-main now has "Require
  status checks to pass", with "Run the tests" from GitHub Actions. Its
  bypass list is empty, so the "bypass rules" tick doesn't skip it. Read
  back from GitHub on 2026-10-23.
- The project's own documents: Ernie registered and checked docs (5
  files) and spec (6 files) in the window, with the register file at
  D:\python\document-manager-register.db. Both checks said nothing had
  changed. Every file's fingerprint, size and last-changed time was the
  same before and after. The register's list matched fingerprints worked
  out separately, the project folder still matched GitHub, and the
  register file was the only new file.

## 3. Shown by this file's own pull request
- GitHub keeps the merge button locked until "Run the tests" passes.
- After the merge, Check on docs shows this file as new, and nothing else.

The thread log entry for thread 07 records what happened.

## 4. Limits
- No way to accept a change yet. A registered folder can't be registered
  again (RG-5), so once a pull request changes a document, every later
  Check shows that change, until a new register file is made.
- Register takes whole folders. Files at the top of the project, like
  CLAUDE.md, aren't covered. The whole project folder has about 10,700
  files, mostly Python's and Git's own, which would bury the documents.
- Big folders: the window waits while a command runs (spec/window.md,
  "Left for later").
- Summaries were tried only on fake documents: the project has no Word
  documents.
- The register file picker's button says "Save". "Starts" in a summary
  includes headings (SM-3), for Ernie to decide.

## 5. Result
Steps 1 to 5 and 8 are done. Steps 6 and 7 each have one check left,
shown when this file's pull request is merged (section 3). Phase 1 passes
when both show as expected. Phase 2 starts only when Ernie says so.
