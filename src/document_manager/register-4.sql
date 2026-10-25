-- Register file, version 4: adds the files that couldn't be read
-- (spec/busy-folders.md, BF-6). Runs after register-3.sql, on new and older
-- register files. It only adds a table, so the lists and summaries already
-- saved stay as they are (BF-11).
BEGIN;

CREATE TABLE unread (
    folder_id   INTEGER NOT NULL REFERENCES folder (id),
    accepted_id INTEGER REFERENCES accepted (id),  -- its accepted list; NULL for the first list
    path        TEXT NOT NULL,  -- place in the folder, like mail/archive.pst
    size        INTEGER,        -- in bytes; NULL if Windows didn't give it
    reason      TEXT NOT NULL   -- why it couldn't be read (BF-1, BF-2)
);

CREATE INDEX unread_list ON unread (folder_id, accepted_id);

PRAGMA user_version = 4;
COMMIT;
