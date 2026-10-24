-- Register file, version 3: adds accepted lists (spec/accept.md).
-- Runs after register-2.sql, on new and older register files. The first
-- list stays in the file table; each accepted list is saved beside it.
BEGIN;

CREATE TABLE accepted (
    id          INTEGER PRIMARY KEY,  -- the order the lists were accepted in
    folder_id   INTEGER NOT NULL REFERENCES folder (id),
    accepted_at TEXT NOT NULL         -- date and time, UTC (AC-2)
);

CREATE TABLE accepted_file (
    accepted_id INTEGER NOT NULL REFERENCES accepted (id),
    path        TEXT NOT NULL,     -- place in the folder, like letters/note.txt
    size        INTEGER NOT NULL,  -- in bytes
    fingerprint TEXT NOT NULL,     -- spec/fingerprint.md
    PRIMARY KEY (accepted_id, path)
);

PRAGMA user_version = 3;
COMMIT;
