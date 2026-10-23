# Window

**Version:** 1.0 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "06 · The first window"

The window lets Ernie run the four commands (spec/report.md,
spec/summaries.md) by clicking instead of typing. It's kept thin: the work
is done by the same engine code the commands use, and the window adds no
rules of its own about the files. One command, from PowerShell in the
project folder, opens it:

    .venv\Scripts\python -m document_manager window

| ID | Rule |
|---|---|
| WN-1 | The command above opens the window. A test runs it that way (like RP-5). |
| WN-2 | The window has a folder box and a register file box. Each can be typed in, or filled with "Choose…", which opens Windows' usual picker. Choosing only fills the box: it never opens, changes or makes a file. |
| WN-3 | Four buttons, Register, Check, Summarize and Summaries, each do exactly what the command of the same name does, with the same rules, on the folder and register file in the boxes. |
| WN-4 | The results show the same words, in the same order, as the command prints. The tags changed, new, missing and couldn't read each have their own colour. |
| WN-5 | Pressing a button first clears the old results, so old results are never shown as new ones. |
| WN-6 | While a button's work runs, the status line says "Working…" and no button can be pressed. When it ends, the status line says which button ran, on which folder, and the time it finished (this computer's time). |
| WN-7 | When something goes wrong, the status line shows the same one plain line as the command, in red, and the results stay empty: nothing is reported as fine (RP-4). |
| WN-8 | If a box is empty, nothing runs; the status line says which box to fill. |
| WN-9 | The window never opens, changes, moves or deletes the documents. Only Register and Summarize write anything, and only to the register file, as the commands do. |
| WN-10 | The window saves nothing of its own: no settings and no history. The boxes start empty each time it opens. |
| WN-11 | Nothing leaves this computer. The window doesn't use the internet, and AI summaries stay off (SM-9). |

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

On trust (technical):
- PySide6 and pytest-qt, pinned to exact versions in requirements-dev.txt.
- The window is one small file, src/document_manager/window.py. It calls
  the same engine and report code as the commands, never a copy of it.
- On GitHub's computer, the tests run the window without showing it on a
  screen. The first check run will show whether that works.

Details:
- "Choose…" for the register file can pick an existing one or name a new
  one. It never asks to replace a file, because nothing is replaced: a new
  register file is made only by Register (RG-2).
- Names show with every character as it is. The commands print the same
  words, but PowerShell shows "?" for characters it can't show.
- Windows' own picker may remember the last folder it showed. That's
  Windows, not the program (WN-10).

Left for later:
- Big folders: for now the window waits while the work runs, which is fine
  for fake documents. For real folders, the work should run in the
  background so the window doesn't freeze.
- Sorting, searching, opening a document from the list, and AI summaries.
