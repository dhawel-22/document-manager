# Document Manager: plan for reusing the vault

**Version:** 1.0 (draft) · **Owner:** Ernie · **Approved by:** waiting
**Drafted by:** Claude, in thread "04 · Finish Phase 0"

Status labels follow the opening document (D-015).

## 1. Why (Ernie)
The vault (the guards on this computer, the lock on GitHub and the working
method) protects only this project today. Goal: add another project with a
short checklist, proven by drills, without rebuilding anything.

## 2. What exists today
| Part | Covers today |
|---|---|
| Bypass off; the guards can't be changed; no administrator prompt | Every project on this computer |
| Manual only; ask before file changes; the blocked list; commits only as the AI account; Python asks first | This folder only: the check script names it |
| The lock on GitHub (protect-main, only-ernie-merges) | This repository only |
| The working method (CLAUDE.md, working rules, four change steps, thread log) | This project only |
| The engine (register, check) | Any folder, read-only |

## 3. The guards: a list of projects instead of one (On trust)
- A new guard file, `projects.txt`, lists the guarded project folders, one
  per line. It's installed next to the check script, where only an
  administrator can change it. Its reviewed copy lives in `vault/guards/`.
- Every rule that says "this folder" today applies to each folder on the
  list. A thread working in one listed project can't change another's
  files (rule 5).
- Only project folders go on the list, never a folder that holds other
  projects.
- If the list can't be read, the check stops the action (like drill 19).
- The install script copies the list. The tamper check compares it with the
  reviewed copy, and checks each listed project's Git name and email.
- The test cases gain a second listed project, and an unlisted one that
  must keep working as before.
- Adding a project later means one line in the list, through a pull
  request, then a reinstall by Ernie. Claude can't add or remove a project.

## 4. Checklist for adding a project (On trust, proven on the first one)
Before:
1. Ernie picks the project and answers section 7 for it.
2. Claude checks, look-only, whether it's in Git and on GitHub, whether it
   holds any real data, and how big it is.

On this computer:
3. The project's Git name and email are set to the AI account. This has to
   happen before step 5, because rule 6 blocks it afterwards.
4. The project gets its working method: CLAUDE.md, working rules, the four
   change steps and a thread log. They're copied from templates in
   `vault/template/` and adapted.
5. The folder is added to the list (pull request), and Ernie reinstalls.
   The tamper check must say ALL SAME.

On GitHub (Ernie clicks, Claude guides):
6. A repository, with the AI account added as a helper.
7. The two rule sets, protect-main and only-ernie-merges, set up the same
   as here. Merging then needs the "bypass rules" tick, as it does here.

Proof:
8. Drills in the new project: 1, 2, 6, 9, 12, 18 and 20, plus a thread in
   the new project trying to change this one. The results are recorded
   through a pull request.

## 5. Build order (one step at a time, each after a "go")
1. Ernie answers section 7.
2. The guards change from section 3: the list, the check script, its test
   cases, the tamper check, the install script and the guide. Pull
   request. Every test case must pass.
3. Ernie reinstalls. The tamper check must say ALL SAME. Drills 1, 6 and 20
   run again here, to show nothing here got weaker.
4. The templates and the checklist from section 4. Pull request.
5. The first project goes through the checklist.
6. Scorecard: every step and drill passed, or this plan says why not.

## 6. Limits
- A question box still protects only if it's read (drill 20). What
  matters is blocked, or goes through a pull request.
- A project without a GitHub repository gets only the guards on this
  computer, not the lock.
- Command rules match text, so a script can do what its command line
  doesn't show (guards plan, section 6).
- Each new project needs Ernie at an administrator window once, for the
  reinstall. That's deliberate.

## 7. Questions (Waiting)
1. **Which project first?** I suggest a small one with no real data.
2. **Python in added projects:** should it ask first, like here, or keep
   the shortcut? This reopens guards plan question 2 for those projects.
3. **Private projects:** the lock on a private repository needs GitHub
   Pro, about $4 a month (D-009). Is that OK?
4. **Real data:** D-009 says no real data in any repository. A project
   that holds real data must keep it out of Git, or stay off GitHub.
