# Document Manager: Phase 2 scorecard

**Version:** 1.0 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "10 · Phase 2, continued"

Phase 2 (opening document, section 5): one real network folder and one
Google Drive folder, read-only. Each phase must pass a clean scorecard
before the next one starts.

The folders hold Ernie's own files, so this file gives only counts,
never what the documents say (D-009).

## 1. Steps

| Step | Result |
|---|---|
| 1. Before Phase 2: a way to accept a change | spec/accept.md, AC-1 to AC-9 (#61 to #64), thread 08 |
| 2. A Google Drive test folder | G:\My Drive\Document manager test, picked by Ernie, thread 09 |
| 3. Try-out on its 6 PDFs | Done, thread 09 |
| 4. Try-out with Word documents added | Done, thread 10 |
| 5. A Google Doc | Not tried: Ernie has no Google Docs (thread 10) |
| 6. One real network folder | Done, thread 10 |
| 7. Scorecard | This file |

## 2. Evidence
Ernie ran each try-out in the window, with the register file at
D:\python\document-manager-register.db. Before and after each one,
Claude worked out every file's fingerprint, size and last-changed time
separately.

- Google Drive, 6 PDFs (2026-10-23): Accept said "Nothing has changed.
  Files checked: 6." Every file was the same before and after, and the
  folder still held only its 6 files.
- Google Drive, with 13 Word documents added (2026-10-24), 19 files in
  all: afterwards, the register file held 13 summaries, none "couldn't
  read", and a new list of 19 files that matches the folder. Ernie's
  picture of the window shows "Documents: 13, couldn't read: 0." Every
  file was the same before and after, and nothing new appeared.
- Network folder (2026-10-24), on drive T:, which Windows reports as a
  network drive: 83 files in 11 subfolders, 20.9 MB, including 72 Word
  documents and 8 PDFs. Register listed all 83, and every entry matches
  the folder. Summarize saved 72 summaries, none "couldn't read"; Ernie's
  picture shows "Documents: 72, couldn't read: 0." Accept saved nothing,
  because nothing had changed (AC-6). Every file was the same before and
  after, and nothing new appeared.
- After the 2026-10-24 try-outs, the project folder had no changes (git
  status), the register file was still version 3, and docs and spec had
  no new lists or summaries.

The thread log entry for thread 10 records what happened.

## 3. Limits
- Summaries of these documents say little. Of the 85 Word documents
  tried, 84 have no title and 83 have no headings. SM-3 finds those only
  through Word's Title and Heading styles, or the title in File, Info,
  and 81 of the documents use only the plain "Normal" style. Most
  summaries are just the first 60 words and a word count. Ernie to
  decide: leave it, change the rule, or AI summaries (Stage B, which
  sends each document's text to Anthropic).
- Only Word documents are summarized (SM-1). The 14 PDFs and 3 other
  files were registered and checked, but not summarized.
- Google Docs weren't tried, because Ernie has none. Online-only Drive
  files, which download when read (thread 08), weren't looked at.
- The register saved the network folder under its network address
  (`\\server\share\...`), not under T:, because the program works out
  the full path. Typing T:\ still finds it.
- Big folders: Summarize took about 9 seconds for 72 documents over the
  network, and the window can't be used while it works (spec/window.md,
  "Left for later"). Phase 3, all network files, would need this first.
- Only two small folders were tried: 19 files and 83 files.

## 4. Result
Phase 2 passes (2026-10-24, Ernie). Steps 1 to 7 are done or settled,
and nothing in either folder was changed. Phase 3 starts only when Ernie
says so.
