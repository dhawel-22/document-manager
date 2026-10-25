# Overview

**Version:** 1.1 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "13 · Discovery: where is my stuff"
**Changes:** v1.1 (2026-10-25): details for program folders and other's
endings. Made through a pull request.

The overview answers where Ernie's files are, from what the register file
already knows (docs/05-discovery-plan.md, questions 2 to 4): what kind of
files each folder holds, which files are duplicates, and which folders
have changed. It reads only the register file, never the folders, so it
takes seconds even for folders that take hours to check.

| ID | Rule |
|---|---|
| OV-1 | The overview only reads the register file. It never opens the folders or their files, and never changes anything. |
| OV-2 | It covers every folder in the register file, each by its newest list, the one Check uses (CK-1). Its first lines say that it comes from the register file, not from the folders as they are now. |
| OV-3 | Folders: for each folder, its files, their total size, the date of its newest list, and how many times its changes were accepted. Then the totals for all folders. |
| OV-4 | Kinds: each file is one of five kinds, by the ending of its name (like `.docx`): documents; pictures, sound and video; program files; backups and archives; or other (the table below). A file inside a program folder, like `.git` or `node_modules`, is a program file whatever its ending. |
| OV-5 | For each kind, the number of files and their size in all folders, and the number of files in each folder. For "other", also its ten most common endings, so what isn't sorted is still seen. |
| OV-6 | Duplicates: files with the same fingerprint (FP-2) in more than one place, in one folder or in several. Each group shows its size and every place where it is. The groups whose extra copies take the most space come first. |
| OV-7 | The duplicates' totals: the groups, the extra copies (every copy but one), and the space the extra copies take. |
| OV-8 | Empty files all have the same fingerprint, so they aren't counted as duplicates. They are counted on their own. |
| OV-9 | Changes: for each accepted list, its folder, its date, and how many files were changed, new and missing compared with the list before it. Folders with no accepted list are counted in one line. |
| OV-10 | The overview says plainly that it knows only accepted changes. Check saves nothing (CK-6), so a folder with no accepted changes may still have changed. |
| OV-11 | A register file that doesn't exist, can't be read or holds no folders gives one plain line (RP-4). Nothing is reported as fine. |
| OV-12 | The command below shows the overview. A test runs it exactly as written (like RP-5). |
| OV-13 | In the window, an Overview button does what the command does, using only the register file box (spec/window.md). |

The command, from PowerShell in the project folder:

    .venv\Scripts\python -m document_manager overview <register file>

Example overview, on fake folders:

    Overview of D:\registers\example.db
    From the register file only: the folders weren't read.

    Folders: 2, files: 9, size: 4.2 MB, empty files: 1.

    C:\Example\Letters
      Files: 6, size: 3.0 MB. Newest list: 2026-10-24 16:05 UTC. Changes accepted: 1.
      Documents 4, pictures, sound and video 1, program files 0, backups and archives 0, other 1.
    C:\Example\Photos
      Files: 3, size: 1.3 MB. Newest list: 2026-10-24 15:22 UTC. Changes accepted: 0.
      Documents 0, pictures, sound and video 3, program files 0, backups and archives 0, other 0.

    Kinds:
      Documents                   4 files    2.6 MB
      Pictures, sound and video   4 files    1.7 MB
      Program files               0 files    0 bytes
      Backups and archives        0 files    0 bytes
      Other                       1 file    12.0 KB   endings: (none) 1

    Duplicates: 1 group, 1 extra copy, 400.0 KB.
      2 copies, 400.0 KB each
        C:\Example\Letters\holiday.jpg
        C:\Example\Photos\holiday.jpg

    Changes accepted: 1 list, in 1 folder. Folders with none: 1.
      C:\Example\Letters  2026-10-24 16:05 UTC: changed 1, new 1, missing 0.
    Only accepted changes are known. Check saves nothing, so a folder with
    no accepted changes may still have changed.

How it's proven:
- A test for every rule, on fake register files made for the tests,
  including an older register file (version 1) and one with accepted
  lists. Each test also checks that the register file's fingerprint is
  the same afterwards (OV-1).
- A try-out by Ernie on the real register file, in the window: the
  register file's fingerprint must be the same before and after, and the
  counts must match counts worked out separately.

On trust (technical):
- The kinds table below. Endings are compared ignoring capitals.
- No new library: the overview is worked out in Python from the register
  file, opened read-only, like the check (CK-6).

Details:
- Kinds (OV-4), by ending:
  - Documents: doc, docx, docm, dot, dotx, rtf, odt, txt, md, pdf, xls,
    xlsx, xlsm, xlsb, xltx, csv, ods, ppt, pptx, odp, msg, eml, htm,
    html, mhtml, ics, vsd, vsdx, pub, one, mdb, accdb.
  - Pictures, sound and video: jpg, jpeg, png, gif, bmp, tif, tiff, heic,
    webp, svg, ico, mp3, wav, wma, m4a, flac, aac, ogg, mp4, mov, avi,
    wmv, mkv, m4v, mpg, mpeg, webm.
  - Backups and archives: zip, 7z, rar, tar, gz, tgz, bz2, xz, zst, cab,
    iso, img, vhd, vhdx, bak, bkf, old.
  - Program files: exe, dll, msi, ocx, ax, sys, bat, cmd, ps1, vbs, js,
    ts, py, pyc, pyd, pyi, ipynb, jar, class, json, yaml, yml, toml, ini,
    cfg, config, inf, xml, sql, sqlite, db, winmd, pkg, appinstaller,
    typed; and every file inside a folder named .git, node_modules,
    __pycache__, .venv, venv or site-packages.
  - Other: everything else, including names with no ending.
- The ending is the part of the name after its last dot. A name with no
  dot, or whose only dot comes first (like `.gitignore`), has no ending;
  "other" shows it as "(none)".
- Program folders' names are compared ignoring capitals too, like endings.
- Other's ten endings (OV-5): the ones with the most files; endings with
  the same number go in alphabetical order, "(none)" first.
- Sizes: 1 KB is 1,024 bytes, as Windows counts; shown with one decimal,
  like 47.4 GB. Under 1 KB, in bytes.
- Order: folders by their path, ignoring capitals (like summaries); the
  places in a duplicate group the same way; groups taking the same space
  by their first place.
- Places in duplicates are shown in full, with the folder, so they can be
  found in Windows' Explorer.
- Dates are in UTC, as they are saved (RG-2, AC-2).
- A folder's first list is the one saved when it was registered; its
  first accepted list is compared with that one.
- Older register files (versions 1 and 2) are read as they are, never
  changed.
- A network folder shows under its network address, as the register
  saves it (thread 10).

Left for later:
- How often folders change: the register knows only accepted changes.
  Each file's last-changed date, from the sweep by dates (thread 12),
  could answer it; that needs its own rules.
- What's inside documents (question 5): a word index.
- Saving the overview as a file.
