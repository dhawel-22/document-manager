# Register

**Version:** 1.2 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "03 · Lighter routine"
**Changes:** v1.1 (2026-10-23): RG-5, a refused folder leaves the register
file exactly as it was (thread 08). Made through a pull request.
v1.2 (2026-10-25): RG-1 and RG-6, files that can't be read
(spec/busy-folders.md). Made through a pull request.

The register is the program's list of files. For each folder registered, it
keeps every file's place, size and fingerprint (spec/fingerprint.md). Later,
the check will compare the folder with this list.

| ID | Rule |
|---|---|
| RG-1 | Registering a folder lists every file in it and in its subfolders: the file's place in the folder (like `letters/note.txt`), its size and its fingerprint. A file that can't be read is listed with the reason instead of a fingerprint (spec/busy-folders.md). |
| RG-2 | The list is saved in a register file (an SQLite database), with the folder's full path and the date and time (UTC) it was registered. |
| RG-3 | Registering only reads the files. It never changes, moves or deletes them. |
| RG-4 | The register file can't be inside the folder it lists. |
| RG-5 | A folder that is already in the register file is refused, and the register file is left exactly as it was. Its list is never silently replaced. |
| RG-6 | If the folder or a subfolder can't be read, nothing is saved, and the program says which one. A file that can't be read doesn't stop it (spec/busy-folders.md). |
