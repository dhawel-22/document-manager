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

## 04 · Finish Phase 0 (2026-09-29 to 2026-09-30)
Purpose: finish the guards plan: the last drills, the GitHub website steps
and the scorecard.
Decided: rule 5 blocks instead of asking (drill 20); only Ernie can change
main on GitHub (rule set only-ernie-merges).
Done:
- Drill 13 passed: the tamper check caught a changed guard file.
- Drill 18 passed in another folder: Python ran with no question.
- Drill 20 failed at first: the check asked, but the questions were
  approved within seconds without being seen. Rule 5 now blocks (#33).
- Build step 4 on GitHub: the rule set only-ernie-merges. As the AI
  account, GitHub reports it can never get past either rule set.
- The scorecard, guards plan section 10. 50 guard test cases and 28 engine
  tests pass.
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
Open: a drill where the AI account tries to merge; rules 4 and 7 still
only ask; the flashing check script window; tools from the opening
document not set up yet (GitHub Actions, pre-commit, Pydantic/pandera,
check-out/check-in scripts); why the mode switched in thread 02; why the
PowerShell command swapped the file names and contents (thread 03); old
branches on GitHub; the leftover name in the app's copy; the drill thread
"New session" (in D:\python\projects\New folder) can be archived; open
questions 2–6.
