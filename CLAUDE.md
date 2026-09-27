# Document Manager: standing instructions for Claude

Claude reads this file automatically at the start of every thread in
this folder.

## Start of every thread
- Read docs/00-opening-document.md and docs/threads.md, then tell Ernie
  in a few short lines where we are.
- Also read this thread's permission mode (a look-only check of the app).
  If it isn't Manual ("default"), tell Ernie and ask him to pick Manual in
  the mode selector next to the send button.
- This reading is the only action allowed before "go".

## Working with Ernie
- The user is Ernie. "Drew" is only the computer account name.
- Ernie is new to this: short messages, one step at a time, plain language.
- Claude proposes; Ernie decides. Technical choices are recorded
  "On trust" (D-015).
- The working rules in section 3 of the opening document always apply.

## "go" and "continue"
- Documentation first. Nothing happens until Ernie says "go".
- "continue" means keep talking. Only "go" means act.
- Talking needs no permission: show drafts and answers right away.
- Show the text of each change in chat before making it.
- A "go" covers only the step just shown. Then stop and report, with evidence.

## How changes happen
- main on GitHub (dhawel-22/document-manager) is locked. Every change goes
  through a pull request that Ernie approves and merges on the website.
  One pull request per change.
- Each change follows the four steps in docs/teaching/how-a-change-happens.md.
- Claude works only as the GitHub account dhawel-22-claude. Never use
  Ernie's account (dhawel-22).
- Before each change, check that this thread is still in Manual mode. The
  app can switch it back after a break (thread 02).
- Before pushing, check the account by asking GitHub directly:
  `gh api user --jq .login` must print dhawel-22-claude. Don't rely on
  `gh auth status` alone; the desktop app's copy of the GitHub tool's
  settings still shows an old name (thread 02).
- Commit as the AI account:
  `git -c user.name="dhawel-22-claude" -c user.email="333494763+dhawel-22-claude@users.noreply.github.com" commit ...`
- Push as the AI account:
  `git -c credential.helper= -c "credential.helper=!gh auth git-credential" push ...`
- End every commit message and pull request description with a plain note
  naming the AI model, like "Made with Claude Opus 5.5." No "Co-Authored-By"
  or "Generated with Claude Code" lines (D-018).

## Threads
- Each thread has a numbered title, like "01 · Standing instructions and
  guards", and sits in the "Document Manager" sidebar group.
- At the end of a thread, its entry in docs/threads.md is added or updated
  through a pull request.
