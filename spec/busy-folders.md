# Busy folders

**Version:** 1.0 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "14 · Discovery: runs that don't fail"

On a busy drive, files are deleted, renamed, locked and changed all day.
Until now, a file deleted, renamed or locked while a run ran stopped the
whole run, and nothing was saved (docs/05-discovery-plan.md, section 4).
A file that changed while it was read could get a fingerprint that
matches no version of it. With these rules, Register, Check, Accept and
Summarize carry on past such a file and say which one it was and why,
and the register file keeps the files that couldn't be read.

| ID | Rule |
|---|---|
| BF-1 | A file that can't be read when its turn comes is listed as "couldn't read", with the reason, and the run carries on. |
| BF-2 | A file whose size or last-changed time is different just after it was read than just before is listed as couldn't read too, with the reason "changed while it was read". Its fingerprint isn't used. |
| BF-3 | A file or subfolder that's gone when its turn comes (deleted or renamed while the run runs) is treated as not there: Check shows a file that's on the list as missing, and Register, Accept and Summarize leave it out. |
| BF-4 | A file or subfolder counts as gone only if the folder itself can still be reached. If the folder can't be reached any more, like a network drive that drops, the run stops and nothing is saved. |
| BF-5 | A subfolder that can't be read, and isn't gone, still stops the run, and nothing is saved, as before. |
| BF-6 | Register and Accept keep a file that couldn't be read on the list: its place, its size if Windows gives it, and the reason, but no fingerprint. Nothing is made up (FP-5). |
| BF-7 | Check never calls a file it can't read changed, unchanged or new: it shows it only as couldn't read, with the reason. A file on the list without a fingerprint shows as new once it can be read, so accepting gives it one. |
| BF-8 | When any file couldn't be read, the words never say "Nothing has changed". The count line says how many couldn't be read, and each one follows, with the reason. |
| BF-9 | Files that couldn't be read aren't changes. If they're all that Check found, Accept doesn't ask, and says "Nothing was saved." |
| BF-10 | The overview counts the files that couldn't be read, and never counts them as duplicates (spec/overview.md v1.3). |
| BF-11 | Runs still only read the files. The register file is the only file written, and the lists and summaries already in it stay as they are. |

Example report, on fake files:

    Changed: 1, new: 0, missing: 1, unchanged: 3, couldn't read: 1.
      changed  letters/note.txt
      missing  letters/old.txt
      couldn't read  mail/archive.pst  in use by another program, or no permission

How it's proven:
- A test for every rule, on fake folders made for the tests: a file held
  open the way Outlook holds its mail files, a file with a locked part, a
  file deleted after it was found, a subfolder deleted while the files are
  being found, a file that grows while it's read, and a folder that can't
  be reached any more.
- An older register file (versions 1 to 3) gets the new table only when a
  list is saved, and a test checks that the lists and summaries already in
  it are the same afterwards (BF-11).
- A try-out by Ernie in the window on fake documents, with one held open
  by another program while Register and Check run. Every other file's
  fingerprint must be the same before and after.

On trust (technical):
- Register file version 4 adds one table for the files that couldn't be
  read, each with its list. Older register files are read as they are, and
  are brought up to version 4 only when a list is saved.
- A file's size and last-changed time are read from the open file, just
  before and just after its contents are read (BF-2).
- A file or subfolder is gone only if the folder can still be reached and
  its name isn't there any more (BF-4). A network folder that can't be
  reached gives Python the same "not found" as a deleted file (seen in a
  test in thread 14), so the folder is checked first.

Details:
- Reasons (BF-1): "in use by another program, or no permission" when
  Windows won't let the file be opened or read. Python gets the same
  answer for both (seen in a test in thread 14), so the reason names both.
  "changed while it was read" (BF-2). Any other reason, word for word,
  without the file's path.
- Check's words (BF-8): the count line ends with "couldn't read: <count>."
  when any file couldn't be read, and those files come last, one line
  each, as in the example. The window shows the tag in its colour (WN-4).
- Register and Accept say "Registered <folder>. Files listed: <count>,
  couldn't read: <count>." (or "Accepted <folder>. …"), followed by each
  file that couldn't be read. "Files listed" counts every file on the
  list, those that couldn't be read included. When every file could be
  read, the words are as before.
- A file that couldn't be read when it was listed has no fingerprint on
  the list. Once it can be read, Check can't tell whether it changed, so
  it shows it as new: new to the list (BF-7).
- Accept (AC-1): a file that couldn't be read when the changes were shown,
  and can be read after the yes, or the other way round, is a change since
  they were shown, so nothing is saved.
- Accept (AC-2): a file on the list that can't be read now is saved
  without a fingerprint. Its fingerprint stays in the older list (AC-3).
- Summarize already carries on past a document it can't read (SM-6).
  BF-3 and BF-4 now apply to it too (spec/summaries.md v1.6).
- The window counts a file that couldn't be read as read (WN-13), and Stop
  works as before (WN-14).

Left for later:
- A long run that picks up where it left off after a stop.
- While the program reads a file, other programs can't rename or delete
  it (seen in a test in thread 14), and a big file takes minutes. Runs at
  quiet times avoid it; opening files so others can still rename and
  delete them needs its own rules.
- A subfolder that can't be read (BF-5). None on T: couldn't be read;
  this computer's own folders may have some.
- Trying a file that couldn't be read again, later in the same run.
- Accept reads the folder twice. Saving what it showed would halve its
  time, and it wouldn't fail when the folder changes in between.
- Telling "in use" and "no permission" apart.
