# The guards: a plain-words guide

**Version:** 1.7 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "02 · Guards build"
**Changes:** v1.1 (2026-09-26): the check script's test cases added. Made
through a pull request.
v1.2 (2026-09-26): the check script and its test runner added. Made through
a pull request.
v1.3 (2026-09-26): the tamper check added. Made through a pull request.
v1.4 (2026-09-26): the plan lists drills 14 to 20; one more open question.
Made through a pull request.
v1.5 (2026-09-27): install and undo scripts, and how Ernie runs them. Made
through a pull request.
v1.6 (2026-09-27): how to answer the app's questions; three open questions
answered. Made through a pull request.
v1.7 (2026-09-29): rule 5 blocks instead of asking (drill 20). Made through a
pull request.

This guide says what each guard does. The other files in this folder must
match it. The plan is `docs/01-guards-plan.md`. Every guard stays "On trust"
until its fire drill passes (plan section 4). Drills 14 to 20 were first
named here; the plan lists them too.

## Where the guards apply (Ernie, 2026-09-26)
Mostly this project. Two rules apply in every Claude project on this
computer, because without them a thread working anywhere could switch the
guards off. The rest act only inside this folder,
`D:\python\projects\document-manager`, and on the files in it. Other
projects keep working as before.

## Everywhere on this computer
1. Bypass mode is switched off. In bypass mode, a thread working anywhere
   could change this folder's files without asking. Drill 3.
2. Claude can't change the installed guards, and can't start an
   administrator prompt. Only Ernie updates the installed guards.
   Drills 5 and 14.

## Only inside this folder
3. Manual mode only, and only Ernie picks the mode. In Accept edits, Auto
   or any other mode except Plan, the check script stops every command and
   file change and asks Ernie to pick Manual. In Plan mode, every command
   asks first. Drills 2, 4 and 15.
4. Claude asks before every file change and every command that changes
   something. Look-only commands, like checking status, run without a
   click. Helper agents follow the same rules. Drills 1, 11 and 12.
5. A thread working in another folder can't change this folder's files:
   the check blocks it, with no question. For commands, the check looks for
   this folder's path in the command text (plan section 6). Drill 20: a
   question alone didn't stop it, because questions were approved without
   being read (2026-09-29).
6. Blocked outright, even if Ernie clicks "allow":
   - pushing to main, force pushes, and deleting branches on GitHub
     (drills 6, 7 and 16)
   - merging pull requests, or switching on auto-merge (drill 8)
   - changing Git settings; reading them is fine (drill 17)
   - commits or pushes as anyone but the AI account (drill 9)
   - commands that wipe out work, like deleting a folder with everything
     in it, `git reset --hard` or `git clean` (drill 10)
7. Python asks first, however it is started, including from the project's
   venv (D-019, question 2). In other projects, python keeps its shortcut.
   Drill 18.

## The files
Kept here and changed only through pull requests:
- `README.md`: this guide.
- `managed-settings.json`: the protected settings file.
- `check-command.ps1`: the check script. It runs before every command and
  file change, and knows which folder a thread works in. If it hits an
  error, it stops the action instead of letting it through. Drill 19.
- `check-command-tests.csv`: the check script's test cases. Each line says
  what Claude tries and whether the script must block it, ask first, or
  leave it to the app's usual rules ("normal"). The script must pass every
  case before it is installed.
- `run-check-tests.ps1`: runs every test case against the check script and
  shows pass or fail. Look-only.
- `tamper-check.ps1`: compares the installed guards with these copies and
  says "same" or "different". It also reports any extra file in the guards
  folder, any Windows registry policy for Claude Code (one would outrank the
  protected file), and whether this project's Git name and email are the AI
  account's (guard 4). Look-only. Drill 13.
- `install-guards.ps1`: copies the reviewed guards into the protected
  folder, for build step 3 and any later update. Ernie runs it.
- `undo-guards.ps1`: takes the guards out again and keeps the files in a
  backup folder. Ernie runs it.

Installed in build step 3, with Ernie's administrator "Yes":
- `C:\Program Files\ClaudeCode\managed-settings.json`
- `C:\Program Files\ClaudeCode\hooks\check-command.ps1`

This project's Git name is set to the AI account before the install,
because rule 6 blocks that change afterwards.

## Answering the app's questions
Answer plain "Yes" or "No". Never choose "Always allow", "Allow for this
session" or "Don't ask again": the app then skips the question next time,
even when the guards ask for it (drills 1 and 18, 2026-09-27).

## Install, update or undo (Ernie only)
These need an administrator PowerShell. Once the guards are live, Claude
can't start one (rule 2), so Ernie runs them:
1. Click Start, type `PowerShell`, right-click "Windows PowerShell" and
   choose "Run as administrator". Windows asks "Yes or No": click Yes.
2. Copy one of these lines into that window and press Enter.
   - Install, or update after a change to the guards:
     `powershell -NoProfile -ExecutionPolicy Bypass -File "D:\python\projects\document-manager\vault\guards\install-guards.ps1"`
   - Undo, if the guards get in the way (nothing is deleted; the files
     move to a backup folder in your home folder):
     `powershell -NoProfile -ExecutionPolicy Bypass -File "D:\python\projects\document-manager\vault\guards\undo-guards.ps1"`
3. Close the window. Then run the tamper check, in any PowerShell (no
   administrator needed). After an install it must say ALL SAME:
   `powershell -NoProfile -ExecutionPolicy Bypass -File "D:\python\projects\document-manager\vault\guards\tamper-check.ps1"`

## Still to find out (build step 5)
- Answered 2026-09-27: the check script stops the app's own mode switch
  (drill 4). Auto-merge wasn't tried.
- Answered 2026-09-27: the check script sees which mode a thread is in
  (drills 2 and 15).
- What happens if the check script can't start at all?
- What happens if the check script runs past its 60 seconds?
- The desktop app can pass its own settings to Claude Code. Once the
  protected file exists, are any of them lost?
- Partly answered 2026-09-27: the app's settings report bypass mode as
  "disabled by the organization's managed settings", so the desktop app
  reads the protected file (drill 3).
