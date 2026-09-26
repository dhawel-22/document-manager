# Document Manager: Claude Code guards plan

**Version:** 1.2 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "01 · Standing instructions and guards"
**Changes:** v1.1 (2026-09-25): question 1 answered: administrator. Made
through a pull request.
v1.2 (2026-09-25): section 8 (findings from build step 1) and question 2
added, in thread "02 · Guards build". Made through a pull request.

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

## 7. Open questions (Waiting)
1. Answered 2026-09-25: administrator (Windows asks only "Yes or No").
   When you install a program, does Windows ask only "Yes or No", or does it
   ask for a password? The answer tells us whether your account is an
   administrator.
2. Your personal settings file lets Claude run any `python` command in Bash
   without asking, in every project. How should this project close that gap?
   The choices come in build step 2 (section 8).

## 8. Findings from build step 1 (2026-09-25)
Sources: Anthropic's Claude Code help pages at code.claude.com/docs/en/
(managed-settings, permissions, permission-modes, hooks, desktop,
checkpointing, sub-agents, settings-reference, tools-reference), and
look-only checks on this computer. Nothing was installed or changed. Every
finding stays "On trust" until a fire drill proves it.

### This computer
- Claude Code 2.1.281 runs inside the Claude desktop app (a Windows app
  package, version 2.9939.2.0). The app keeps its copy of Claude Code in
  `C:\Users\Drew\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude-code`.
  Versions 2.1.280 and 2.1.281 are both there, so it updates itself.
  Recheck the version before the fire drills.
- Of the settings places checked, only the personal file exists:
  `C:\Users\Drew\.claude\settings.json`. No project settings, no protected
  file, no Windows registry policy.
- That personal file lets Claude run any `python` command in Bash without
  asking, in every project (question 2).
- Claude has two command tools here: Bash (Git Bash) and PowerShell.

### Guard by guard (section 3)
1. The protected file can set the starting mode and switch off bypass mode.
   It must also switch off "Auto" mode, where a second AI approves actions
   instead of Ernie (against D-016). No setting was found that switches off
   "Accept edits", and the desktop app remembers a mode picked for a folder
   over the default. But "ask" rules prompt in every mode, so ask rules for
   Claude's file tools and for the file commands Accept edits lets through
   (mkdir, touch, rm, rmdir, mv, cp, sed; Set-Content, Add-Content,
   Clear-Content, Remove-Item) should close that gap.
2. "Deny" rules block in every mode without a prompt, and no other settings
   file can loosen a rule in the protected file. Each command rule is needed
   twice, for Bash and for PowerShell. Rules match a command as written:
   `git -C . push` gets past `Bash(git push *)` (section 6).
3. Hooks work on Windows, in Git Bash by default or in PowerShell if the hook
   asks for it. A hook blocks with exit code 2 (or a JSON "deny"); exit code
   1 lets the action through. Hooks in the protected file can't be switched
   off elsewhere, and they also run for helper agents. A command check must
   watch Bash, PowerShell and Monitor.
4. A Git feature; nothing to check in Claude Code. Today this project's Git
   settings (`.git/config`) give the name "Ernie".
5. Nothing needed from Claude Code.
6. The protected file reaches every Claude Code thread on this computer,
   including this app's Code tab and helper agents. Hooks are told each
   thread's project folder, so project-only checks can stay in this folder.
7. Rewind undoes only edits made by Claude's file tools: not changes made by
   commands, and usually not edits by helper agents. Plan mode asks before
   commands only while Auto mode is off.
8. Not a Claude Code question (build step 4).

### Also found
- A helper agent can be set to run in "Accept edits" while the main thread
  is in Manual. Ask rules and hooks still apply to it.
- "Yes, and don't ask again" on a command or web prompt saves an allow rule
  that later threads use too. Until the guards are in, choose plain "Yes".
- The desktop app can pass its own settings to Claude Code. Once the
  protected file exists, Claude Code ignores them unless the file sets
  `parentSettingsBehavior`.
- The built-in block on deleting system folders with cmd's `rd` or `del`
  needs Claude Code 2.1.283; this computer has 2.1.281.

### Not known yet (step 2 or the fire drills)
- The help pages spell the Auto-mode setting two ways: `disableAutoMode` and
  `permissions.disableAutoMode`. Which works?
- Does a mode remembered for this folder also beat the protected file's
  starting mode?
- Does the desktop app have rewind? The help pages don't say.
- Can a rule block the app's own tools, like its mode switch?
- How do we see, from the desktop app, which settings are in force? The help
  pages use `/status`, a terminal command.
