# Window

**Version:** 1.6 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "06 · The first window"
**Changes:** v1.1 (2026-10-23): the window command says one line when the
window opens. Made through a pull request.
v1.2 (2026-10-23): how a box's path is read, and errors the commands
don't expect. Made through a pull request.
v1.3 (2026-10-23): the Accept button (spec/accept.md). Made through a
pull request.
v1.4 (2026-10-24): big folders: the work runs in the background, with
counts, a Stop button, and a question when closing. Made through a pull
request.
v1.5 (2026-10-25): the Overview button (spec/overview.md). Made through a
pull request.
v1.6 (2026-10-25): WN-9 and WN-14, long runs pick up after a stop
(spec/long-runs.md). Made through a pull request.

The window lets Ernie run the six commands (spec/report.md,
spec/summaries.md, spec/accept.md, spec/overview.md) by clicking instead of typing. It's kept thin: the work
is done by the same engine code the commands use, and the window adds no
rules of its own about the files. One command, from PowerShell in the
project folder, opens it:

    .venv\Scripts\python -m document_manager window

| ID | Rule |
|---|---|
| WN-1 | The command above opens the window. A test runs it that way (like RP-5). |
| WN-2 | The window has a folder box and a register file box. Each can be typed in, or filled with "Choose…", which opens Windows' usual picker. Choosing only fills the box: it never opens, changes or makes a file. |
| WN-3 | Six buttons, Register, Check, Summarize, Summaries, Accept and Overview, each do exactly what the command of the same name does, with the same rules, on the folder and register file in the boxes. Overview uses only the register file box. |
| WN-4 | The results show the same words, in the same order, as the command prints. The tags changed, new, missing and couldn't read each have their own colour. |
| WN-5 | Pressing a button first clears the old results, so old results are never shown as new ones. |
| WN-6 | While a button's work runs, the status line says "Working…", the boxes can't be changed, and no button can be pressed except Stop (WN-14). When it ends, the status line says which button ran, on which folder, and the time it finished (this computer's time). |
| WN-7 | When something goes wrong, the status line shows the same one plain line as the command, in red, and the results stay empty: nothing is reported as fine (RP-4). |
| WN-8 | If a box is empty, nothing runs; the status line says which box to fill. Overview needs only the register file box. |
| WN-9 | The window never opens, changes, moves or deletes the documents. Only Register, Summarize and Accept write anything, and only to the register file, as the commands do; Register and Check also keep a progress file (spec/long-runs.md). |
| WN-10 | The window saves nothing of its own: no settings and no history. The boxes start empty each time it opens. |
| WN-11 | Nothing leaves this computer. The window doesn't use the internet, and AI summaries stay off (SM-9). |
| WN-12 | The work runs in the background, so the window keeps answering while it runs: it can be moved, resized and scrolled. |
| WN-13 | While the work runs, the status line counts: first the files found, "Working… 1500 files found so far.", then the files read, "Working… 120 of 1500 files read." Summarize counts the Word documents it reads: "Working… 12 of 72 Word documents read." |
| WN-14 | A Stop button can be pressed while the work runs. The work stops after the file it's reading, nothing is saved in the register file, the results stay empty, and the status line says "<Button> stopped at <time> (this computer's time). Nothing was saved." For Register and Check, it says instead that the next run picks up from there (spec/long-runs.md). If every file was already read, Stop is too late: the work finishes as usual, and the status line says so (WN-6). |
| WN-15 | Closing the window while the work runs first asks "Work is still running. Stop it and close the window?" with Yes and No; No is picked unless Yes is clicked. Yes stops the work as Stop does, then the window closes. |

How it's proven:
- A test for every rule, with pytest-qt, which fills the boxes and clicks
  the buttons, on fake documents made for the tests. For WN-3 and WN-4,
  each test also runs the command and checks that the window shows the
  same words.
- For WN-11, the test blocks the internet while clicking every button,
  like the SM-9 test.
- A demo run the way Ernie would: he opens the window with the command
  and clicks through on fake documents. The fake documents' fingerprints
  must be the same before and after.
- For WN-12 to WN-15, a stand-in for the work waits while the test moves
  the window, reads the count, presses Stop or closes the window. If the
  window stops answering, the test fails within seconds instead of
  waiting forever.
- For WN-14, on fake documents: after Stop, the register file is the
  same as before, or not made at all.
- A try-out by Ernie on a big real folder he picks, read-only: he moves
  the window while Check runs, watches the count, and presses Stop once.
  Every file's fingerprint must be the same before and after.

On trust (technical):
- PySide6 and pytest-qt, pinned to exact versions in requirements-dev.txt.
- The window is one small file, src/document_manager/window.py. It calls
  the same engine and report code as the commands, never a copy of it.
- On GitHub's computer, the tests run the window without showing it on a
  screen. The first check run will show whether that works.
- The work runs in a second thread; Qt's signals bring the counts and the
  results back to the window.
- The engine's reading steps take an optional counter, called as each
  folder is listed and each file is read. The window's counter updates
  the status line, and stops the work when Stop was pressed, before
  anything is saved. The commands don't pass a counter, so they work and
  print exactly as before.

Details:
- WN-1 (v1.1): when the window opens, the command says so in one line:
  "The window is open. Close it to finish." PowerShell waits until the
  window is closed.
- WN-3 (v1.2): a box's path is read the way PowerShell reads a typed one:
  the spaces around it are left out, and so are the quotes that Windows'
  "Copy as path" puts around it.
- WN-7 (v1.2): an error the commands don't expect is shown the same way,
  starting "Problem:" with the error's name. It's never hidden.
- Accept (v1.3): the changes show in the results, then a box asks
  "Accept the changes shown?" with Yes and No; No is picked unless Yes is
  clicked. The results then end with the command's last line: "Accepted
  <folder>. Files listed: <count>." or "Nothing was saved." The question
  shows in the box, not in the results.
- "Choose…" for the register file can pick an existing one or name a new
  one. It never asks to replace a file, because nothing is replaced: a new
  register file is made only by Register (RG-2).
- Names show with every character as it is. The commands print the same
  words, but PowerShell shows "?" for characters it can't show.
- Windows' own picker may remember the last folder it showed. That's
  Windows, not the program (WN-10).
- Accept (v1.4): Accept reads the folder twice, once to show the changes
  and again after Yes, so it counts twice, and Stop works in both. While
  the question is open, nothing runs.
- Summaries (v1.4): it reads only the register file, so it shows no count.
- Stop (v1.4): a very big file is read to its end before the work stops.
- Overview (v1.5): it reads only the register file, so it shows no count,
  like Summaries. When it ends, the status line names the register file
  instead of a folder.

Left for later:
- Sorting, searching, opening a document from the list, and AI summaries.
