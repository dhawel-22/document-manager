# Document Manager: Claude Code guards plan

**Version:** 1.1 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "01 · Standing instructions and guards"
**Changes:** v1.1 (2026-09-25): question 1 answered: administrator. Made
through a pull request.

Status labels follow the opening document (D-015). Every guard stays
"On trust" until its fire drill passes.

## 1. Why
Today, two things stop unapproved changes: Claude following the rules, and
the GitHub lock. The lock protects main on GitHub, not the files on this
computer. In "accept edits" mode, Claude's edits don't even ask first. The
guards make this computer enforce the rules too.

## 2. Decisions (Ernie)
- **D-016:** Claude asks before every file change and every command that
  changes something. Look-only commands, like checking status, run without
  a click.
- **D-017:** The guards live in a settings file that Windows protects.
  Changing it needs Ernie to approve an administrator prompt.

Both join the decision register in the opening document at the end of this
thread.

## 3. The guards (On trust)
1. Ask-first mode is the default, and "bypass permissions" mode is switched
   off.
2. Blocked outright, even if Ernie clicks "allow":
   - pushing straight to main, overwriting history on GitHub (force pushes),
     deleting branches on GitHub
   - merging pull requests (only Ernie merges)
   - changing Git settings or the app's permission mode
   - editing the installed guard files
   - commands that wipe out work, like deleting a whole folder
3. Hooks: small fixed scripts that check each command before it runs, for
   what plain rules can't see. First job: every commit and push must use the
   AI account, never Ernie's.
4. This project's Git settings use the AI account by default, so a forgotten
   flag can't commit as Ernie.
5. A copy of every guard file is kept in this project and reviewed through
   pull requests. A tamper check compares the installed files with that copy.
6. The protected settings apply to every Claude Code thread on this computer.
   Checks that only make sense for this project act only inside its folder.
7. Rewind and plan mode: how to undo Claude's edits in the app, and a
   look-only mode for bigger changes. Each is tried once and written down.
8. On GitHub: only Ernie can merge into main, if GitHub allows that for a
   personal account; and the AI account gives up permissions it doesn't need.

## 4. Fire drills
Each guard is proven by a test that tries the forbidden thing, with real
output recorded. A guard that fails its drill is fixed before anything else.

| # | Try this | Must happen |
|---|---|---|
| 1 | Claude edits a file | The app asks Ernie first |
| 2 | Same, with the app set to "accept edits" | Still asks, or the gap is written down |
| 3 | Switch on bypass mode | Not available |
| 4 | Claude changes its own permission mode | Blocked |
| 5 | Claude edits an installed guard file | Blocked |
| 6 | Push straight to main | Blocked |
| 7 | Force push | Blocked |
| 8 | Claude merges a pull request | Blocked |
| 9 | Commit as Ernie | Blocked |
| 10 | Delete a whole folder | Blocked |
| 11 | A helper agent edits a file | Same rules apply |
| 12 | Check status | Runs without a click |
| 13 | Ernie changes an installed guard file on purpose | The tamper check reports it |

## 5. Build order
One step at a time, each after a "go":
1. Check what this version of Claude Code supports on Windows. Record the
   findings in this plan through a pull request. Nothing is installed.
2. Write the guard files and the tamper check in the project. Pull request.
3. Install the guards in the protected folder. Ernie approves the
   administrator prompt.
4. GitHub website steps: Ernie clicks, Claude guides.
5. Run the fire drills and record the results. Pull request.
6. Scorecard: every drill passes, or this plan says why not.

## 6. Limits
- Guards check what Claude does, not what Claude says. A false "done" in chat
  is caught by the evidence rules and Ernie's review.
- Command rules match text, and an unusual spelling of a command can slip
  past them. That's why "ask first" is the main guard and the blocked list is
  the backup.
- Ernie can still click "allow" on a harmful request. The blocked list covers
  the worst cases.

## 7. Open question (Waiting)
1. Answered 2026-09-25: administrator (Windows asks only "Yes or No").
   When you install a program, does Windows ask only "Yes or No", or does it
   ask for a password? The answer tells us whether your account is an
   administrator.
