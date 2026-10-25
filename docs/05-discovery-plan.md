# Document Manager: Discovery plan

**Version:** 1.0 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "12 · Phase 3: all network files"

The program has two parts (Ernie, thread 12): discovery first, then a
vault.

- Discovery: files stay where they are. The program looks at them,
  read-only, and finds out what Ernie has. Phases 1 to 3 of the opening
  document are discovery.
- Vault, later: the documents that matter are kept inside the system.
  Every change goes through check-out and check-in, so the vault knows
  at once who changed what, and keeps each version. It works like the
  vault that protects this project's own files, where every change goes
  through a pull request.

The folders hold Ernie's own files, so this file gives only counts,
never folder or file names (D-009).

## 1. Why two parts
In thread 12, the program was measured on a whole network drive (T:):
- Reading all of it would take about 10 hours: about 3 hours to read its
  315 GB, and about 7 hours to open its 695,000 files one at a time.
- A run fails if one file is deleted, renamed or locked while it runs,
  and on a busy drive files come and go all day.
- 99% of its files are in one backup folder.

A program that only looks from outside can't know about changes in
seconds. A vault can, because every change goes through it. So discovery
doesn't need to be fast: it's a survey that runs in the background, and
a long run at night is fine.

## 2. What discovery finds out
1. What's there: every file, where it is, its size and its fingerprint.
2. What kind: documents, program files, backups or media.
3. Duplicates: the same fingerprint in more than one place.
4. What changes, and how often: which folders are busy and which quiet.
5. What's inside: summaries of Word documents now, a word index later.

Together, the answers make a map of Ernie's files: what belongs in the
vault, and how to bring it in.

## 3. Where
T: first, then Google Drive and this computer's own folders. Whether
the second network drive (Y:, system backups) is included is Ernie's
decision.

## 4. How it works
- Read-only, always: discovery never changes, moves or deletes a file.
- It uses what's built: Register, Check, Accept and Summarize, in the
  window.
- It runs at quiet times: on a busy drive, nights and weekends.

What it still needs before all of T:, each written up in spec/ first,
for Ernie's approval:
- A run carries on past a file that's deleted, renamed or locked, and
  says which one, instead of failing.
- A long run that's stopped picks up where it left off.
- A report that answers questions 2 to 4.

## 5. After discovery
The vault belongs to the phase that moves files (opening document,
section 5, "Later"), after backups and its own fire drills. Discovery's
map decides what goes in. Check-out and check-in, versions, activity and
answers in seconds belong there.

## 6. Done when
Discovery is done for a place when questions 1 to 5 have answers in a
report Ernie can read, and nothing there was changed, proven the way
the try-outs were.
