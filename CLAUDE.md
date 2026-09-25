# Document Manager: standing instructions for Claude

Claude reads this file automatically at the start of every thread in
this folder.

## Start of every thread
- Read docs/00-opening-document.md and docs/threads.md, then tell Ernie
  in a few short lines where we are.
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
- Claude works only as the GitHub account dhawel-22-claude. Never use
  Ernie's account (dhawel-22).
- Before pushing, check that `gh auth status` shows dhawel-22-claude as the
  active account.
- Commit as the AI account:
  `git -c user.name="dhawel-22-claude" -c user.email="333494763+dhawel-22-claude@users.noreply.github.com" commit ...`
- Push as the AI account:
  `git -c credential.helper= -c "credential.helper=!gh auth git-credential" push ...`

## Threads
- Each thread has a numbered title, like "01 · Standing instructions and
  guards", and sits in the "Document Manager" sidebar group.
- At the end of a thread, its entry in docs/threads.md is added or updated
  through a pull request.
