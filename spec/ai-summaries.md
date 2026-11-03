# AI summaries

**Version:** 1.1 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "16 · AI summaries on this computer"
**Changes:** v1.1 (2026-11-03): AI-6 lowered to 3,000 words, and AI-11,
after a measurement (thread 16); the commands. Made through a pull request.

AI summaries are Stage B of summaries (spec/summaries.md). A model running
in LM Studio on this computer reads each Word document's text and writes a
short summary, which is saved in the register file next to the Stage A
summary (D-024).

| ID | Rule |
|---|---|
| AI-1 | AI summaries are made only on this computer, by LM Studio. The program talks only to 127.0.0.1 (this computer). Any other address is refused, so no document text leaves this computer. |
| AI-2 | The model is Qwen3.8 27B (Ernie, thread 16). Changing it needs a new version of these rules. |
| AI-3 | AI summaries cover the Word documents (`.docx`) in a registered folder, read the same way as Stage A (SM-1, SM-6). A folder that isn't in the register file is refused (SM-7). |
| AI-4 | The model gets the fixed instructions below and the document's text, nothing else. |
| AI-5 | A summary says only what the document states. What it doesn't state is written "unavailable". |
| AI-6 | A document over 3,000 words is listed as "too long", with its word count. Nothing is summarized from part of it. |
| AI-7 | Each summary is saved as a new row as soon as it's made, with how it was made: "AI", the model's name and the instructions' version. A stop keeps the summaries already saved. The Stage A summary and older rows are never changed. |
| AI-8 | A document whose fingerprint hasn't changed since its last AI summary, by the same model and instructions, is skipped (like SM-4). |
| AI-9 | If LM Studio isn't running, or the model isn't loaded, the run stops before reading any document, with one plain line, and nothing is saved. |
| AI-10 | AI summaries only read the documents. They never change, move or delete them (SM-5). |
| AI-11 | If LM Studio refuses a document as too big for the model's reading space, or the model's answer is cut off, nothing is saved for it. It's listed as "not made", with the reason, and the run carries on. |

The instructions (version 1), sent to the model word for word:

    You write summaries for a document register. Summarize the document
    below in 3 to 5 plain sentences.
    Say what kind of document it is, who it is from and to, its date, and
    its main points.
    Use only facts stated in the document. If something is not stated,
    write "unavailable". Do not guess.

How it's proven:
- A test for every rule. The tests use a stand-in for LM Studio, so they
  run on GitHub too, where there's no model.
- A try-out by Ernie on a few registered Word documents, with every
  file's fingerprint checked before and after.

On trust (technical):
- The program talks to LM Studio's local server (port 1234) in the
  standard way, using Python's own tools; no new library.
- Only the model's final answer is saved, not its thinking.
- The 3,000-word limit leaves room in the model's reading space as LM
  Studio loads it now (8,192 tokens). Measured in thread 16: a fake
  4,096-word report took 7,267 tokens, and the model's thinking filled
  the rest, so its answer was cut off; LM Studio refused a fake
  6,000-word one as too big. Version 1.0 said 4,000 words would fit; it
  didn't.
- The model is asked for the same words each time (temperature 0), as in
  the try-out in thread 16.
- The AI summaries are saved in a new table in the register file, which
  becomes version 5 the first time one is saved.

Commands (v1.1), from PowerShell in the project folder:

    .venv\Scripts\python -m document_manager ai-summarize <folder> <register file>
    .venv\Scripts\python -m document_manager ai-summaries <folder> <register file>

- ai-summarize: makes the AI summaries (AI-1 to AI-11), then says in one
  line how many were made, unchanged, too long, couldn't be read and not
  made, followed by each one that's too long, couldn't be read or wasn't
  made, with its word count or the reason. Ctrl+C stops it, and the
  summaries already made stay saved (AI-7).
- ai-summaries: shows each document's place and latest AI summary, with
  when and by which model it was made. It only reads the register file.
- Both list documents in the same order as summarize. A problem is said
  in one plain line (like RP-4).
- There's no button for them in the window yet.
