-- Register file, version 5: adds the AI summaries (spec/ai-summaries.md).
-- Runs after register-4.sql, on new and older register files. It only adds
-- a table, so the lists and Stage A summaries already saved stay as they
-- are (AI-7).
BEGIN;

CREATE TABLE ai_summary (
    id           INTEGER PRIMARY KEY,  -- the order the summaries were saved in
    folder_id    INTEGER NOT NULL REFERENCES folder (id),
    path         TEXT NOT NULL,     -- place in the folder, like letters/report.docx
    fingerprint  TEXT NOT NULL,     -- the document's, when it was summarized (AI-8)
    made_at      TEXT NOT NULL,     -- date and time, UTC
    method       TEXT NOT NULL,     -- how the summary was made: 'ai' (AI-7)
    model        TEXT NOT NULL,     -- the model's name in LM Studio (AI-2, AI-7)
    instructions INTEGER NOT NULL,  -- the instructions' version (AI-4, AI-7)
    summary      TEXT NOT NULL      -- the model's final answer, without its thinking
);

CREATE INDEX ai_summary_place ON ai_summary (folder_id, path);

PRAGMA user_version = 5;
COMMIT;
