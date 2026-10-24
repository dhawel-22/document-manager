# Thread log

## 00 · Planning talk (2026-09-24 to 2026-09-25)
Purpose: decide how to protect work from silent AI edits; set up the vault.
Decided: D-001 to D-015 (see 00-opening-document.md). D-009 answered: public.
Done:
- Opening document v1.0 saved (entry 8a12299) and put on GitHub, public.
- AI account dhawel-22-claude created by Ernie and added to the project.
- Ernie's GitHub keys removed from this computer; owner work happens on the website.
- Lock "protect-main": pull request required, 1 approval, no bypass,
  no deletions, no force pushes.
- Lock test (2026-09-25): a push from the AI account straight to main was
  refused by GitHub.
Lessons:
- The user is Ernie; "Drew" is only the computer account name.
- Check which account is signed in before authorizing; type addresses into
  the private window, never click them from chat.
- Read settings back to check them: the first check found approvals = 0, not 1.
Open: Claude Code guards plan; line-ending fix; open questions 2–6.

## 01 · Standing instructions and guards (2026-09-25)
Purpose: standing instructions, the line-ending fix, and the guards plan.
Decided: D-016 and D-017 (see 01-guards-plan.md); D-018 (how AI work is
credited).
Done:
- CLAUDE.md added, so every thread gets the standing instructions
  (pull request #2, entry fa090c0).
- Line-ending rules added (.gitattributes, pull request #3, entry 0d368fa).
  This computer's copies were rewritten; every file now has the same bytes
  as GitHub's.
- Guards plan v1.0 added (pull request #4, entry a735f86). Nothing is
  installed yet.
- Guards plan question 1 answered: administrator (plan v1.1).
- Teaching aid added: docs/teaching/how-a-change-happens.md.
- Entries and pull requests now end with a plain model note instead of
  co-author lines (D-018). Earlier entries still list an outside "claude"
  account as a contributor.
Lessons:
- Talking needs no permission; only actions need "go".
- New line-ending rules don't change files already on the computer. They
  must be rewritten once, and Git skips files it thinks are unchanged.
- GitHub's newer "Files changed" page says "Submit review", not "Review
  changes".
- The lock also requires approval from someone other than the last pusher,
  so every new push needs a fresh approval.
- Check the number next to a pull request's title before approving. Two
  approvals once landed on an old, already-merged one; the card now checks it.
- The note at the end of an entry is part of its text too; show it first.
Open: build the guards (plan section 5, step 1 next); open questions 2–6;
old branches on GitHub can be deleted.

## 02 · Guards build (2026-09-25 to 2026-09-27)
Purpose: build the Claude Code guards (guards plan, section 5).
Decided: question 2, Python asks first only in this project (plan v1.3);
D-019, the project's own venv; the guards cover mostly this project (guide,
vault/guards/README.md).
Done:
- Build step 1: what Claude Code 2.1.281 supports on Windows (#10).
- The thread log entry (#11), question 2 (#12) and D-019 (#13).
- Standing instructions: check the mode, and ask GitHub for the account
  (#14). Guard 4: this project's Git name is the AI account's.
- Build step 2: the guide, the protected settings file, the test cases, the
  check script and the tamper check (#15 to #19); the drill list (#20);
  install and undo scripts (#21).
- Build step 3: Ernie installed the guards on 2026-09-27; tamper check ALL
  SAME.
- Build step 5, first pass: 17 of 20 drills passed (#22, #23; plan
  section 9). Every file change here now asks first (#23). Six saved
  "don't ask again" approvals were removed.
Lessons:
- The mode switched to "Accept edits" twice without anyone changing it,
  right after pull requests #10 and #21 were merged, not after a break as
  this entry first said. Cause not found; rule 3 now stops all work here
  when it happens.
- "Always allow" makes the app skip questions, even the guards' own.
  Answer plain Yes or No.
- The desktop app doesn't ask before file changes on its own, even in
  Manual mode. The drills found this; the tests on paper couldn't.
- The desktop app keeps its own copy of the GitHub tool's settings, with an
  old name in it. The reliable account check is `gh api user`.
- Too many steps and long messages lose Ernie. Real work needs a lighter
  routine.
Open: drills 13 and 20, and the other-project half of 18; build step 4
(the GitHub website steps); a lighter routine (one "go" per change); the
proposal for checking code Ernie can't judge; why the mode switches; old
branches on GitHub; the leftover name in the app's copy; open questions
2–6.

## 03 · Lighter routine (2026-09-29)
Purpose: a lighter routine, then start building the engine.
Decided: D-020, one "go" per change, "merged" starts the update of this
computer, and looking needs no "go"; D-021, quality over speed.
Done:
- The lighter routine (#25): the card v1.2, CLAUDE.md, opening document
  v1.5.
- Python set up (#26): the project's own venv, pytest 9.1.1, a first test.
- The engine, each piece with plain rules in spec/ and a test for each
  rule: fingerprint (#27), register (#28), check (#29), and the report with
  two commands, register and check (#30).
- A demo on fake files found that the commands didn't work as written.
  Fixed (#31); a new test now runs them the way Ernie would. 28 tests pass.
Lessons:
- Tests that call the code directly can miss what Ernie actually runs.
  Test commands the way he types them.
- A PowerShell command without named settings wrote three files into the
  project folder instead of the scratch folder, with no error. The next
  check caught it, and the files were moved out. Always name the settings,
  and check where a command wrote, not just whether it did.
- The mode stayed Manual after all seven merges today (#25 to #31).
- Ernie got lost twice. Start each change with one plain line on what it
  gets him, and keep a short "where we are" list.
Open: Phase 0 still needs drills 13 and 20, the other-project half of 18,
build step 4 (the GitHub website steps) and the scorecard before the
window (Phase 1); the proposal for checking code Ernie can't judge (so
far: he reads the rules, and a test checks each rule); why the mode
switched in thread 02; why the PowerShell command swapped the file names
and contents; old branches on GitHub; the leftover name in the app's copy;
open questions 2–6.

## 04 · Finish Phase 0 (2026-09-29 to 2026-10-23)
Purpose: finish the guards plan: the last drills, the GitHub website steps
and the scorecard. Then (2026-10-23) the first feature: summaries of Word
documents.
Decided: rule 5 blocks instead of asking (drill 20); only Ernie can change
main on GitHub (rule set only-ernie-merges); summaries of Word documents,
Stage A only: everything stays on this computer, documents are only read
(SM-5), and AI summaries stay off until Ernie decides (SM-9).
Done:
- Drill 13 passed: the tamper check caught a changed guard file.
- Drill 18 passed in another folder: Python ran with no question.
- Drill 20 failed at first: the check asked, but the questions were
  approved within seconds without being seen. Rule 5 now blocks (#33).
- Build step 4 on GitHub: the rule set only-ernie-merges. As the AI
  account, GitHub reports it can never get past either rule set.
- The scorecard, guards plan section 10 (#34). 50 guard test cases and 28
  engine tests pass.
- A plan for reusing the vault in other projects: version 1.0, a draft
  with four open questions (#35).
- The drill thread "New session" (in D:\python\projects\New folder) was
  archived, then brought back: no archiving until the project is
  operational (CLAUDE.md).
- Summaries of Word documents (spec/summaries.md, #38 to #43): the rules
  (#38); the library that reads Word documents, python-docx 1.2.0 (#39);
  one document's summary (#40); saving summaries in the register file,
  now version 2 (#41); the summarize and summaries commands (#42); both
  lists in the same order (#43).
- A demo on fake documents, run the way Ernie would type it: every rule
  behaved as written, and the fake documents' fingerprints were the same
  before and after. 61 tests pass.
Lessons:
- A question box protects only if it's read. What matters must be
  blocked, or go through a pull request.
- Asked to run a drill, another Claude thread went on to read the app's
  logs, record the mouse, and give an administrator command for Ernie's
  open window; the installed guards then changed. The tamper check caught
  it. Administrator commands now come only from the project's approved
  files.
- Claude stated as fact something it hadn't checked. Say only what the
  evidence shows.
- The guard test runner errors on every case when started from
  PowerShell 7. Run it from Git Bash.
- One step at a time, each confirmed before the next, works for Ernie.
- The rule set only-ernie-merges stops even Ernie until he ticks "bypass
  rules"; only he has that box (how-a-change-happens v1.3).
- After a three-week break, the thinking setting was "medium", not "max"
  (D-021). Check it at the start, like the mode.
- The Word library makes up the title "Word Document" for a document that
  has none. Read the library's own code before trusting what it returns.
- Splitting the biggest step into three small pull requests (#40 to #42)
  kept each one short enough to show in full.
- The demo found the sort order that the tests missed. Keep running
  demos the way Ernie types.
- pip used copies already on this computer instead of downloading. Say
  what actually happened, not what was planned.
Open: whether to start Phase 1 (the window), with or without GitHub
Actions first; trying summaries on a real folder, read-only; AI summaries
(Stage B); numbers in names sort character by character ("Report 10"
before "Report 2"); the four questions of the reuse plan
(docs/02-reuse-plan.md, section 7); a drill where the AI account tries to
merge; rules 4 and 7 still only ask; the flashing check script window;
tools from the opening document not set up yet (GitHub Actions,
pre-commit, Pydantic/pandera, check-out/check-in scripts); why the mode
switched in thread 02; why the PowerShell command swapped the file names
and contents (thread 03); old branches on GitHub; the leftover name in the
app's copy; open questions 2–6.
Next: 05 · The window (Phase 1). First, Ernie decides whether GitHub
Actions (automatic checks on GitHub) comes first; then the window toolkit
(PySide6 or Tkinter); then the window's rules in spec/, for his approval.

## 05 · Automatic checks and the toolkit (2026-10-23)
Purpose: start Phase 1: decide on automatic checks, then the window
toolkit. The window itself moved to thread 06 (Ernie).
Decided: automatic checks before the window, and D-022, the window uses
PySide6, tested with pytest-qt. Both On trust: Claude recommended, Ernie
accepted (D-015).
Done:
- Automatic checks (#47): on every pull request and every change to
  main, GitHub runs the tests on its own Windows computer, with Python
  3.12.8 as here, and shows a green tick or a red cross. The checks can
  only read the project.
- The AI account got the "workflow" permission that check files need,
  through a new sign-in that Ernie approved as dhawel-22-claude.
- The card v1.4 (#48): step 3 checks that GitHub shows dhawel-22 and
  waits for the green tick.
- D-022 in the opening document v1.7 (#49).
- All six check runs passed: on #47, #48 and #49, and on main after
  each merge.
Lessons:
- At the start, the mode was "Accept edits" and thinking "medium" again.
  The start-of-thread check caught both; Ernie switched them.
- Check files need the "workflow" permission. GitHub refused the first
  send; Claude missed it when drafting.
- The GitHub tool here still has the old name "dhawel-22" saved, so a
  quick refresh of the sign-in can't work (read in the tool's own code).
  A fresh sign-in worked: '' | gh auth login --hostname github.com
  --git-protocol https --scopes workflow --web. It asks nothing and
  opens no browser.
- The guards block Claude from changing the GitHub sign-in (rule 6), so
  that step is Ernie's.
- GitHub's sign-in page offered dhawel-22 twice. Approving there would
  have given Claude Ernie's account. Read the name on every page.
- GitHub never lets the author approve a pull request: approve as
  dhawel-22 (card v1.4).
- Steps without the reason lost Ernie, and he stopped the thread. Say
  why first, in a few lines. Open the terminal beside the chat and read
  it, instead of asking Ernie to copy what it says.
- "I followed your recommendation" is On trust (D-015). The first D-022
  draft said "Ernie picked"; it was corrected before the change.
- #49 was merged before its check finished. It passed, but wait for the
  tick once code changes start.
Open: the old name "dhawel-22" saved in the GitHub tool; old branches on
GitHub, now also automatic-checks, card-v1-4 and d-022-pyside6; making
the check required before merging (a website step for Ernie); trying
summaries on a real folder, read-only; AI summaries (Stage B); numbers
in names sort character by character ("Report 10" before "Report 2");
the four questions of the reuse plan (docs/02-reuse-plan.md, section 7);
a drill where the AI account tries to merge; rules 4 and 7 still only
ask; the flashing check script window; tools from the opening document
not set up yet (pre-commit, Pydantic/pandera, check-out/check-in
scripts); why the mode switched in thread 02; why the PowerShell command
swapped the file names and contents (thread 03); open questions 2–6.
Next: 06 · The first window. First, the window's rules in spec/, for
Ernie's approval (a picture of the planned window can come first, in
chat); then PySide6 and pytest-qt at exact versions; then the first
window and its tests.

## 06 · The first window (2026-10-23)
Purpose: the window's rules, its tools, and the first window, then a demo.
Decided: the window's rules, spec/window.md, now v1.2 (Ernie); the main
part of PySide6 (PySide6_Essentials 6.11.2) and pytest-qt 4.5.0 (On
trust); the rest of the window in one pull request (Ernie); the process
stays as it is for now (Ernie).
Done:
- The window's rules, WN-1 to WN-11 (#51), with v1.1 (#53) and v1.2 (#55).
- The window tools (#52). Tests draw windows off screen; the automatic
  check showed this works on GitHub's computer too.
- The window opens (#53); the commands' words in one place (#54); the
  four buttons, results, status line and colours (#55). 85 tests pass.
- A demo on fake documents in D:\python\demo-window, clicked through by
  Ernie with the real pickers: every button worked; the Word documents'
  fingerprints were the same before and after; the register file was the
  only file the window made.
Lessons:
- At the start, thinking was "medium" again; Ernie switched it to "max".
- pip installed PySide6 from a copy stored by another project
  (structure_reporting, 2026-09-24). Its fingerprints matched PyPI's.
  Check where a library came from, not only that it installed.
- Four of five merges (#51, #53, #54, #55) came before the check
  finished; all passed. The GitHub setting that waits for the tick was
  tried once but didn't save; the cause is unknown.
- Ernie found the pace too slow. Shorter messages and fewer separate
  steps helped; two bigger speed-ups (a summary instead of the full code,
  one "go" per feature) were offered and not taken for now.
- Testing a draft against draft code in the scratch folder, before
  showing it, meant no corrections after "go".
- The entry's note and pull request text weren't shown before #51,
  against the thread 01 lesson; from #52 on they were.
- Claude once counted the early merges wrong ("four out of four"); it was
  four out of five. Count from the record.
Open: GitHub waiting for the green tick (rule set protect-main); the two
speed-ups, if the pace stays too slow; big folders (the window waits
while a command runs); the register file picker's button says "Save";
"Starts" in a summary includes headings (SM-3), Ernie to decide; the demo
folder D:\python\demo-window stays until Ernie deletes it; old branches
on GitHub, now also window-rules, window-tools, window-opens,
commands-words and window-buttons; the old name "dhawel-22" saved in the
GitHub tool; trying summaries on a real folder, read-only; AI summaries
(Stage B); numbers in names sort character by character ("Report 10"
before "Report 2"); the four questions of the reuse plan
(docs/02-reuse-plan.md, section 7); a drill where the AI account tries to
merge; rules 4 and 7 still only ask; the flashing check script window;
tools from the opening document not set up yet (pre-commit,
Pydantic/pandera, check-out/check-in scripts); why the mode switched in
thread 02; why the PowerShell command swapped the file names and contents
(thread 03); open questions 2–6.
Next: 07 · The project's own documents (Phase 1). First, GitHub waits
for the green tick, one screen at a time; then the window on the
project's own documents, read-only; then the Phase 1 scorecard.

## 07 · The project's own documents (2026-10-23)
Purpose: GitHub waits for the green tick; the window on the project's
own documents, read-only; the Phase 1 scorecard.
Decided, all On trust (Claude recommended, Ernie accepted, D-015): the
project's own documents are docs and spec, with the register file at
D:\python\document-manager-register.db, outside the project; the rule
that waits for the tick leaves its two smaller options off; the card
change as the test of the lock.
Done:
- GitHub waits for the green tick: Ernie added "Require status checks
  to pass" to the rule set protect-main, with "Run the tests" from
  GitHub Actions. Read back from GitHub; Ernie's picture shows its
  bypass list is empty.
- The window on the project's own documents: Ernie registered and
  checked docs (5 files) and spec (6 files). Every file's fingerprint,
  size and last-changed time was the same before and after, the
  register's list matched fingerprints worked out separately, and the
  register file was the only new file.
- The Phase 1 scorecard, docs/03-phase-1-scorecard.md (#57). After the
  merge, Check on docs found exactly the new file, and nothing else.
- The card v1.5 (#58): GitHub won't merge until the tick is green.
- On #58, GitHub marked "Run the tests" Required, and merging stayed
  blocked after Ernie approved, while the check ran. The "bypass rules"
  tick wasn't tried in that time.
Lessons:
- At the start, thinking was "medium" again; Ernie switched it to "max".
- In thread 06, nine website steps in one message failed without a
  trace. One screen at a time, with a picture of each, worked: twice the
  small "Add checks" box was still open, and the save went through once
  it was closed. Whether that box caused the old failure is unknown.
- The database tool's output has Windows line endings, so the first
  comparison said "different". Find out why before reporting a
  difference.
- The check takes about a minute, so the lock is hard to catch. On #57
  the check finished first; on #58, half of the test was seen.
- After the check finished, the bypass box appeared only after a reload.
Open: whether the "bypass rules" tick can skip the check, tried on this
entry's pull request; Phase 1 passes when that shows as expected
(scorecard section 5); a way to accept a change before Phase 2
(scorecard section 4), Ernie to decide; the register file
D:\python\document-manager-register.db stays; the two speed-ups, if the
pace stays too slow; big folders (the window waits while a command
runs); the register file picker's button says "Save"; "Starts" in a
summary includes headings (SM-3), Ernie to decide; the demo folder
D:\python\demo-window stays until Ernie deletes it; old branches on
GitHub, now also thread-06-log, phase-1-scorecard and card-v1-5; the old
name "dhawel-22" saved in the GitHub tool; trying summaries on a real
folder, read-only; AI summaries (Stage B); numbers in names sort
character by character ("Report 10" before "Report 2"); the four
questions of the reuse plan (docs/02-reuse-plan.md, section 7); a drill
where the AI account tries to merge; rules 4 and 7 still only ask; the
flashing check script window; tools from the opening document not set up
yet (pre-commit, Pydantic/pandera, check-out/check-in scripts); why the
mode switched in thread 02; why the PowerShell command swapped the file
names and contents (thread 03); open questions 2–6.
Next: 08 · Before Phase 2. First, the bypass test's result and whether
Phase 1 passes (Ernie); then whether the register needs a way to accept
a change (Ernie); then the rules for it in spec/, if so.

## 08 · Before Phase 2 (2026-10-23)
Purpose: the bypass test and whether Phase 1 passes; a way to accept a
change in the register.
Decided: Phase 1 passes, and the bypass rule: wait for the green tick,
then tick "bypass rules", then merge (Ernie); accepting a change,
spec/accept.md, AC-1 to AC-9 (Ernie); the routine stays as it is
(Ernie); Phase 2 starts with a Google Drive test folder (Ernie).
Done:
- The Phase 1 scorecard v1.1 (#60): Phase 1 passes; the bypass rule.
- Accepting a change: the rules (#61); the engine, with register file
  version 3 (#62); the accept command (#63); the Accept button (#64).
- A try-out by Ernie in the window on spec: Check showed 2 changed and 1
  new; Accept saved a new list of 7 files; Check then said nothing had
  changed. Every spec file's fingerprint, size and last-changed time was
  the same before and after.
- The try-out found that a refused Register still brought the register
  file up to version 3. Fixed (#65); its new test failed on the old code
  first. 106 tests pass.
Lessons:
- At the start, thinking was "medium" again.
- The bypass tick showed on #59 while the check ran. Whether it would skip
  the check wasn't tried; the rule above makes it not matter.
- The mode switched to "Accept edits" twice, after #63 and #64 were
  merged. The guards blocked work both times (rule 3). Cause not found.
- Ernie's manager raised the cost; the project is on probation to
  deliver. Too many questions cost Ernie time: bundle the steps, ask once.
- The try-out found a flaw the tests missed, again. Keep the try-outs.
- Copying drafts from the scratch folder brought Windows line endings
  once; they were removed before the commit. The guards blocked a
  forced branch delete and a git checkout; safe ways worked.
- Claude said 3 files had changed in spec; Check showed 2 changed and 1
  new. Count from the record.
Open: Check on docs shows 3 changes and on spec 1 (register.md, #65),
all from merged pull requests, for Ernie to accept; Google Docs and
Sheets show as small shortcut files, and online-only files download when
read; why the mode switches after merges; the register file
D:\python\document-manager-register.db stays (now version 3); big folders
(the window waits while a command runs); the register file picker's
button says "Save"; "Starts" in a summary includes headings (SM-3),
Ernie to decide; the demo folder D:\python\demo-window stays until Ernie
deletes it; old branches on GitHub, now also thread-07-log,
phase-1-result, accept-rules, accept-engine, accept-command,
accept-button and register-refusal; the old name "dhawel-22" saved in
the GitHub tool; AI summaries (Stage B); numbers in names sort character
by character ("Report 10" before "Report 2"); the four questions of the
reuse plan (docs/02-reuse-plan.md, section 7); a drill where the AI
account tries to merge; rules 4 and 7 still only ask; the flashing check
script window; tools from the opening document not set up yet
(pre-commit, Pydantic/pandera, check-out/check-in scripts); why the
PowerShell command swapped the file names and contents (thread 03); open
questions 2–6.
Next: 09 · Phase 2: a Google Drive test folder. First, Ernie picks a
small test folder in G:\My Drive; then Register, Check, Summarize and
Accept on it in the window, read-only, with every file's fingerprint
checked before and after.

## 09 · Phase 2: a Google Drive test folder (2026-10-23)
Purpose: Register, Check, Summarize and Accept on a small Google Drive
folder, read-only.
Decided: the test folder is G:\My Drive\Document manager test (Ernie).
Done:
- A try-out by Ernie in the window on the test folder (6 PDF files):
  Accept then said "Nothing has changed. Files checked: 6." Every
  file's fingerprint, size and last-changed time was the same before
  and after, and the folder still holds only its 6 files.
- The folder was registered in D:\python\document-manager-register.db,
  next to docs and spec, which were left as they were.
Lessons:
- At the start, thinking was "medium" again.
- The folder holds only PDFs, so Summarize had no Word documents to
  read. What it said wasn't seen.
Open: a Word document and a Google Doc in the test folder (how Google
Docs show up, from thread 08); one network folder, read-only (Phase 2);
the open items of thread 08.
Next: 10 · Phase 2, continued. First, a Word document and a Google Doc
in the test folder; then Check, Summarize and Accept on it.
