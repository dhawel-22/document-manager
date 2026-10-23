# Summaries

**Version:** 1.0 (draft) · **Owner:** Ernie
**Drafted by:** Claude, in thread "04 · Finish Phase 0"

The summaries feature finds the Word documents in a registered folder,
reads them, and saves each one's location and summary in the register file
(spec/register.md).

Stage A (these rules): find, read and store, all on this computer. Nothing
leaves the computer.
Stage B (later, only with Ernie's yes): real summaries written by Claude.
Each document's text would be sent to Anthropic.

| ID | Rule |
|---|---|
| SM-1 | Summarizing a registered folder finds every Word document (`.docx`) in it and in its subfolders. |
| SM-2 | For each document, it saves the document's place in the folder, its fingerprint, the summary, how the summary was made, and the date and time (UTC). |
| SM-3 | Stage A summary: the document's title, its headings in order, its first 60 words, and its word count, all taken straight from the document. Nothing is made up or reworded. |
| SM-4 | A document whose fingerprint hasn't changed since its last summary is skipped. A changed document gets a new summary, and the old one is kept with its date. |
| SM-5 | Summarizing only reads the documents. It never changes, moves or deletes them. |
| SM-6 | Old Word files (`.doc`), protected files, and files that can't be opened are listed as "couldn't read", with the reason. Nothing is guessed for them. |
| SM-7 | A folder that isn't in the register file is refused. |
| SM-8 | A command shows the results: each document's place and summary, plus the "couldn't read" list. |
| SM-9 | Stage B, AI summaries, is off until Ernie decides to turn it on. Until then, no document text leaves this computer. |

How it's proven:
- A test for every rule, on fake Word documents made for the tests. That
  includes one with headings, one with no title, an empty one, a protected
  one, and an old `.doc` file.
- A demo run the way Ernie would type it, like the one in thread 03.

On trust (technical):
- Word documents are read with `python-docx`, a widely used free library,
  pinned to one exact version in `requirements-dev.txt`.
- The summaries go in a new table in the same register file.
