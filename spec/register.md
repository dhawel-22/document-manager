# Register

**Version:** 1.0 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "03 · Lighter routine"

The register is the program's list of files. For each folder registered, it
keeps every file's place, size and fingerprint (spec/fingerprint.md). Later,
the check will compare the folder with this list.

| ID | Rule |
|---|---|
| RG-1 | Registering a folder lists every file in it and in its subfolders: the file's place in the folder (like `letters/note.txt`), its size and its fingerprint. |
| RG-2 | The list is saved in a register file (an SQLite database), with the folder's full path and the date and time (UTC) it was registered. |
| RG-3 | Registering only reads the files. It never changes, moves or deletes them. |
| RG-4 | The register file can't be inside the folder it lists. |
| RG-5 | A folder that is already in the register file is refused. Its list is never silently replaced. |
| RG-6 | If the folder or any file in it can't be read, nothing is saved, and the program says which one. |
