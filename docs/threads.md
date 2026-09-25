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
Decided: D-016 and D-017 (see 01-guards-plan.md).
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
Open: build the guards (plan section 5, step 1 next); open questions 2–6;
old branches on GitHub can be deleted.
