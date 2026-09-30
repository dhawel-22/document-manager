-- Register file, version 1 (spec/register.md).
PRAGMA user_version = 1;

CREATE TABLE folder (
    id            INTEGER PRIMARY KEY,
    path          TEXT NOT NULL UNIQUE,  -- the registered folder, full path
    registered_at TEXT NOT NULL          -- date and time, UTC (RG-2)
);

CREATE TABLE file (
    folder_id   INTEGER NOT NULL REFERENCES folder (id),
    path        TEXT NOT NULL,     -- place in the folder, like letters/note.txt
    size        INTEGER NOT NULL,  -- in bytes
    fingerprint TEXT NOT NULL,     -- spec/fingerprint.md
    PRIMARY KEY (folder_id, path)
);
