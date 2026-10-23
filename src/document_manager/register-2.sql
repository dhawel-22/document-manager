-- Register file, version 2: adds the summaries (spec/summaries.md).
-- Runs after register.sql (version 1), on new and older register files.
BEGIN;

CREATE TABLE summary (
    id          INTEGER PRIMARY KEY,  -- the order the summaries were saved in
    folder_id   INTEGER NOT NULL REFERENCES folder (id),
    path        TEXT NOT NULL,  -- place in the folder, like letters/report.docx
    fingerprint TEXT,           -- the document's, when summarized; NULL if it couldn't be read at all
    made_at     TEXT NOT NULL,  -- date and time, UTC (SM-2)
    method      TEXT NOT NULL,  -- how the summary was made: 'stage-a' (SM-3)
    title       TEXT,           -- '' when the document has no title
    headings    TEXT,           -- a JSON list of [level, text], in order
    first_words TEXT,
    word_count  INTEGER,
    problem     TEXT            -- why it couldn't be read (SM-6); NULL when summarized
);

CREATE INDEX summary_place ON summary (folder_id, path);

PRAGMA user_version = 2;
COMMIT;
