# How a change happens

**Version:** 1.3 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "01 · Standing instructions and guards"
**Changes:** v1.1 (2026-09-25): step 3 now checks the pull request number.
Made through a pull request.
v1.2 (2026-09-29): one "go" per change; "merged" starts step 4; looking
needs no "go" (D-020). Made through a pull request.
v1.3 (2026-09-30): step 3 adds the "bypass rules" tick, needed since the
rule set only-ernie-merges. Made through a pull request.

A teaching aid (D-007). Every change follows the same four steps, with one
"go". Looking at files, GitHub or the app never needs a "go".

## 1. Talk (no "go" needed)
Claude shows the exact text in chat. Ernie reads it, asks questions, or asks
for changes.

## 2. "go": make the change
- Claude checks that it is signed in as the AI account and that this
  computer matches GitHub.
- Claude makes a temporary branch and saves the change there.
- Claude sends it to GitHub and opens a pull request.
- Claude stops and gives Ernie the address.

## 3. Ernie's turn on GitHub (no "go")
- Type the address yourself.
- Check that the number next to the title matches the one Claude gave.
- Read "Files changed".
- Click "Submit review", choose "Approve", then submit.
- Tick "Merge without waiting for requirements to be met (bypass rules)".
  Only Ernie has this box. It lifts only the rule set only-ernie-merges;
  the approval is still required.
- Click "Merge pull request", then "Confirm merge".
- Tell Claude "merged".

## 4. After "merged": update this computer (no "go")
- Claude checks on GitHub that the right pull request merged. If it didn't,
  Claude stops.
- Claude brings the merge onto this computer.
- Claude checks that every file here matches GitHub exactly.
- Claude removes the temporary branch and stops.

Then the next change starts again at step 1.

## Start and end of a thread
- Start: Claude reads the opening document and the thread log and says where
  we are. No "go" needed.
- End: the wrap-up is just another change and goes through the same four
  steps.
