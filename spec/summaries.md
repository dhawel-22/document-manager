# Summaries

**Version:** 1.6 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "04 · Finish Phase 0"
**Changes:** v1.1 (2026-10-23): details for SM-3 and SM-6, below. Made
through a pull request.
v1.2 (2026-10-23): details for saving, and for older register files. Made
through a pull request.
v1.3 (2026-10-23): the two commands. Made through a pull request.
v1.4 (2026-10-23): summaries lists documents in the same order as
summarize. Made through a pull request.
v1.5 (2026-10-24): an older register file is brought up to date only
when summaries are saved. Made through a pull request.
v1.6 (2026-10-25): busy folders (spec/busy-folders.md). Made through a
pull request.

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

Details (v1.1):
- Title (SM-3): the title saved in the document itself (in Word: File,
  Info, Title). If there's none, the first paragraph styled "Title". If
  there's neither, the summary says "no title". The library on its own
  would make up the title "Word Document" in that case, so the title is
  read directly.
- Headings (SM-3): the paragraphs styled "Heading 1" to "Heading 9", in
  order, with their level.
- Words (SM-3): counted in the main text, tables included, in the order
  they appear; a merged table cell counts once. Headers, footers,
  footnotes, comments and text boxes aren't read.
- "Couldn't read" reasons (SM-6): an old Word file (.doc); protected with a
  password, or not a real .docx inside; Word's temporary lock file (a name
  starting with "~$"); or the error, word for word.
- Saving (SM-2, SM-4): each summary is a new row; old rows are never
  changed or deleted. A document that still can't be read, for the same
  reason, isn't saved again.
- Register files made before summaries (version 1) get the summaries table
  the first time a folder in them is summarized. The check reads them as
  they are, and never changes them (CK-6).
- Saving (v1.5): an older register file is brought up to the current
  version only when the summaries are saved, after every document has
  been read. A run that is stopped (spec/window.md, WN-14), or fails
  while reading, leaves the register file exactly as it was.
- Busy folders (v1.6): a document or subfolder that's gone when its turn
  comes is left out, not listed as couldn't read. If the folder itself
  can't be reached any more, the run stops and nothing is saved
  (spec/busy-folders.md, BF-3, BF-4).

Commands (v1.3), from PowerShell in the project folder:

    .venv\Scripts\python -m document_manager summarize <folder> <register file>
    .venv\Scripts\python -m document_manager summaries <folder> <register file>

- summarize: summarizes the folder (SM-1 to SM-7), then says in one line
  how many documents were summarized, unchanged, and couldn't be read,
  followed by each one that couldn't be read, with the reason.
- summaries: shows the results (SM-8): each document's place and latest
  summary, then the "couldn't read" list. It only reads the register file.
- Both work exactly as written; a test runs them that way (like RP-5). A
  problem is said in one plain line (like RP-4).
- Characters the window can't show appear as "?"; the summary in the
  register file is unchanged.
- Both list documents in the same order: folder by folder, ignoring
  capitals.
