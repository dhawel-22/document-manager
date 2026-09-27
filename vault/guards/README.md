# The guards: a plain-words guide

**Version:** 1.1 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "02 · Guards build"
**Changes:** v1.1 (2026-09-26): the check script's test cases added. Made
through a pull request.

This guide says what each guard does. The other files in this folder must
match it. The plan is `docs/01-guards-plan.md`. Every guard stays "On trust"
until its fire drill passes (plan section 4). New drills 14 to 20 are named
here and get added to the plan in a later change.

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
5. Changes to files in this folder ask first, whichever thread makes them,
   even one working in another folder. For commands, the check looks for
   this folder's path in the command text (plan section 6). Drill 20.
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
- `tamper-check.ps1`: compares the installed guards with these copies and
  says "same" or "different". It also checks that this project's Git name
  is the AI account (guard 4). Look-only. Drill 13.

Installed in build step 3, with Ernie's administrator "Yes":
- `C:\Program Files\ClaudeCode\managed-settings.json`
- `C:\Program Files\ClaudeCode\hooks\check-command.ps1`

This project's Git name is set to the AI account before the install,
because rule 6 blocks that change afterwards.

## Still to find out (build step 5)
- Can a rule stop the app's own tools, like its mode switch and auto-merge?
- Does the check script see which mode a thread is in?
- What happens if the check script can't start at all?
- The desktop app can pass its own settings to Claude Code. Once the
  protected file exists, are any of them lost?
- How can we see, from the desktop app, which settings are in force?
