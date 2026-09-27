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

## 02 · Guards build (from 2026-09-25)
Purpose: build the Claude Code guards (guards plan, section 5).
Decided: nothing new yet.
Done:
- This thread switched from "Accept edits" to Manual, so the app asks
  before file changes.
- Build step 1: the guards plan v1.2 records what Claude Code 2.1.281
  supports on Windows, and adds question 2 (pull request #10, entry
  94d12ba). Nothing is installed yet.
Lessons:
- The desktop app remembers the mode picked for a folder, and that beats
  the default. This thread came back in "Accept edits" after a break.
  Check the mode at the start of each thread and after each break.
- The desktop app keeps its own copy of the GitHub tool's settings, and it
  still names Ernie's account. So `gh auth status` can show "dhawel-22"
  while GitHub actually sees the AI account. No sign-in for Ernie's account
  was found on this computer. The reliable check asks GitHub: `gh api user`.
- Too much at once loses Ernie. One short step at a time, in plain words,
  and say what each click is for before asking for it.
- Ernie's review is the real check, so each change must be small and plain
  enough to read. "I don't understand this" is always a fine answer.
Open: question 2 (the python rule), then build step 2; a proposal for
checking code Ernie can't judge (tests first, code can't change its own
tests, a scope check, a second reviewer, approving results); CLAUDE.md: add
the mode check and use `gh api user`; tidy the leftover name in the app's
copy; old branches on GitHub can be deleted; open questions 2–6.
