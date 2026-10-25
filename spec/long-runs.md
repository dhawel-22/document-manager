# Long runs

**Version:** 1.0 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "14 · Discovery: runs that don't fail"

On a big folder, Register and Check take hours: all of T: would take about
10 hours each (thread 12). Until now, a run that stopped for any reason
started again from the first file: after Stop, a closed window, a network
drive that dropped (BF-4), or the computer turning off. With these rules,
the next run picks up where the last one stopped
(docs/05-discovery-plan.md, section 4).

| ID | Rule |
|---|---|
| LR-1 | While Register or Check reads a folder, it keeps what it has read so far in a progress file next to the register file: each file's place, size, last-changed time, and fingerprint, or why it couldn't be read. |
| LR-2 | The progress is kept at least once a minute between files, and when the run stops: by Stop, by closing the window, or by a problem (BF-4, BF-5). A power cut loses at most the last minute of reading, and the file being read. |
| LR-3 | The next Register or Check of the same folder, with the same register file, picks up from the progress. A file read before isn't read again if its size and last-changed time are still the same; any other file is read, including one that couldn't be read before. |
| LR-4 | A run that picks up says so, in one line before its usual words: when the run it picks up from stopped, how many files it kept, and how many it read again. |
| LR-5 | When a run finishes, it saves its list (RG-2) or shows its report (RP-2), as before, and its progress is removed. When no unfinished run is left, the progress file is deleted. |
| LR-6 | The progress file is the program's own working file, never part of the register file. The register file is still written only when a run finishes, so where the other rules say nothing is saved (WN-14, BF-4), the register file is left as it was. |
| LR-7 | Register refuses a folder that's already registered before it reads any file (RG-5), instead of after. |
| LR-8 | Accept and Summarize don't pick up: a stopped Accept or Summarize starts again from the first file, as before. |
| LR-9 | Runs still only read the documents. Besides the register file, the progress file is the only file written. |

How it's proven:
- A test for every rule, on fake folders: a run stopped partway by a
  counter, as Stop does, and a typed command ended partway by force, as a
  power cut would; then the next run. Each test checks what it kept, what
  it read again, and that the list or report is the same as from a run
  that never stopped.
- A file changed while the run was stopped is read again; one whose size
  and last-changed time are the same is kept.
- A try-out by Ernie in the window, on a big fake folder: Register, Stop
  partway, close the window, open it again, and Register again; then the
  same with Check. Every file's fingerprint must be the same before and
  after.

On trust (technical):
- The progress file is an SQLite file, like the register file, so a power
  cut while it's being written leaves it as it was when it was last kept.
- The size and last-changed time a run compares come from the folder's
  listing, so files kept from before aren't opened at all. Checked on this
  computer's own disk (thread 14): the listing gives the same size and
  time as the file itself, even for a file held open, and it shows a
  change, even one that keeps the size. Not yet tested on a network drive,
  where Windows can keep a copy of a listing for a few seconds.

Details:
- The progress file is next to the register file, with ".progress" added
  to its name, like document-manager-register.db.progress.
- A run picks up only from its own kind: a Check doesn't pick up a stopped
  Register's progress, or the other way round.
- A file whose size and last-changed time stay the same while its bytes
  change is missed by a run that picks up. The next Check that doesn't
  pick up reads every file again.
- Words (LR-4), like: "Picked up the run that stopped at 2026-10-26 03:12
  UTC: 115000 files kept, 12 read again." The time is in UTC, as the
  register file's times are.
- Stop (WN-14), for Register and Check: the status line says "<Button>
  stopped at <time> (this computer's time). The register file wasn't
  changed; the next <Button> on this folder picks up from here." For
  Summarize and Accept it stays "Nothing was saved."
- A typed register or check command stopped with Ctrl+C says, in one plain
  line, that the register file wasn't changed and the next run picks up.
- A Register refused because the folder is already registered (LR-7)
  removes that folder's Register progress, which could never finish.
- The count (WN-13): a file kept from before counts as read.

Left for later:
- Accept and Summarize picking up (LR-8). Accept's second reading could
  use its first the same way (LR-3), which would make it much faster.
- Starting over on purpose: deleting the progress file does it, by hand.
- Two runs of the same folder at the same time.
