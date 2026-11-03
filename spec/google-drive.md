# Google Drive

**Version:** 1.0 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "15 · Discovery: Google Drive (G:)"

Google Drive shows on this computer as drive G:, with 103,923 files, 626 GB
(thread 15). A file there can be kept only at Google, and reading it
downloads it to this computer (thread 08). There isn't room for that, and
copying Drive's files to this computer is ruled out (Ernie, thread 15).

Google already keeps each file's name, place, size and SHA-256
fingerprint, the same kind of fingerprint the program makes (FP-1). With
these rules, Register on a Google Drive folder asks Google for that list
instead of reading the files, so nothing is downloaded.

| ID | Rule |
|---|---|
| GD-1 | The program never reads a file's contents on Google Drive. A folder or file is on Google Drive when Windows names its drive "Google Drive". |
| GD-2 | Register on a Google Drive folder asks Google for every file in it and in its subfolders: each file's place, size and fingerprint, as in RG-1. The fingerprint is Google's SHA-256 of the file (FP-1). |
| GD-3 | The program only asks Google about the files. It never asks for their contents, and never changes anything at Google or on G:. |
| GD-4 | A file Google gives no fingerprint for, like a Google Docs file, is listed as couldn't read: its place, its size if Google gives it, and the reason (BF-6). Nothing is made up (FP-5). |
| GD-5 | Shortcuts and files in Google's trash are left out. Register says how many shortcuts it left out. |
| GD-6 | Check, Accept and Summarize refuse a Google Drive folder before anything is read, and say why: they read the files' contents. |
| GD-7 | Only folders in My Drive. The program finds the folder at Google by its place on G:. A folder Google can't find, or has more than one of, is refused, and nothing is saved. |
| GD-8 | Signing in to Google is Ernie's step, with its own command: once, and again whenever Google asks. The sign-in lets the program see the files' details, never their contents. It's kept outside the project, never in Git, and Claude never opens it. |
| GD-9 | Only the sign-in and the questions about the files go to Google. No file, list or summary leaves this computer. |
| GD-10 | If Google can't be reached, or the sign-in is missing or refused, nothing is saved, and the program says so in one plain line (RP-4). |
| GD-11 | A list from Google is saved like any other (RG-2), in the same register file, so the overview counts it with the rest. |
| GD-12 | In the window, Register on a Google Drive folder counts the files found (WN-13), and Stop works as for any run (WN-14). A stopped list from Google keeps no progress file: the next Register starts again from the start. |

The order of the work, each step its own pull request or website step:
1. These rules.
2. Google's libraries, at exact versions, and the sign-in command.
3. Ernie's set-up on Google's website, one screen at a time, then one
   sign-in. Google calls this permission "restricted", and its pages
   don't say clearly whether an app only its owner uses needs Google's
   review. If Google won't allow it, the work stops here, and these rules
   are looked at again.
4. Register from Google's list, with its tests.
5. The try-out.

How it's proven:
- A test for every rule, against a stand-in for Google that answers the
  way Google's documentation shows. The stand-in keeps every question,
  and a test checks that each one only asked about files (GD-3).
- A test that Register, Check, Accept and Summarize open no file in a
  Google Drive folder: the tests watch every file the program opens
  (GD-1, GD-6).
- The try-out, after Ernie signs in: Register the test folder
  G:\My Drive\Document manager test into a new register file made for the
  try-out. Google's list must give the same 19 places, sizes and
  fingerprints as the real register file's newest list of that folder,
  made by reading the files (thread 10). That shows that Google's
  fingerprint is the program's (FP-1), and that the sign-in's permission
  gives it.
- Then a bigger folder Ernie picks: its files and sizes must match G:'s
  own listing, which reads no file (thread 15).

On trust (technical):
- A drive is Google Drive when its name in Windows (its volume label) is
  "Google Drive", as G:'s is. Windows shows its file system as FAT32
  (read in thread 15).
- The permission is Google's drive.metadata.readonly: the narrowest one
  that covers a whole Drive. Google lists it as restricted (Google's guide
  to Drive's permissions, read in thread 15).
- Google gives a SHA-256 only for files whose contents are stored at
  Google: not for Google Docs, Sheets and the like, or for shortcuts
  (Google's Drive reference, read in thread 15).
- The program asks Google for all of My Drive at once, in parts, then
  keeps the files inside the chosen folder. That takes fewer questions
  than asking folder by folder. How long it takes isn't measured yet.
- The sign-in uses two files in C:\Users\Drew\.document-manager, outside
  the project: google-client.json, which Ernie saves from Google's
  website, and google-sign-in.json, which the sign-in command writes.
  Every thread's copy of the project finds them there.
- No test talks to Google, and GitHub's computer never signs in.

Details:
- Places (RG-1) are made from the names Google gives, joined with /, like
  letters/note.txt. A / inside a name becomes _. Google allows two files
  with the same name in one folder, and Windows doesn't: each is listed,
  with Google's ID for it added in brackets, like letters/note.txt [1a2B3c].
- Register says "Registered <folder>, from Google's list. Files listed:
  <count>." When any file has no fingerprint, as in BF-8: "Files listed:
  <count>, couldn't read: <count>." and each one, with the reason. Then
  "Shortcuts left out: <count>." when there are any.
- Reasons (GD-4): "a Google file, with no fingerprint at Google" for
  Google Docs, Sheets, Slides and the like; "Google gave no fingerprint"
  for any other.
- GD-6: "<folder> is on Google Drive. Check would download every file it
  reads, so it's refused (GD-6)." The same for Accept and Summarize, with
  their names.
- GD-7: "<folder> isn't in My Drive (GD-7).", "<folder> wasn't found at
  Google (GD-7).", or "Google has more than one folder named <name> there,
  so <folder> can't be told apart (GD-7)."
- GD-10: "Not signed in to Google. Sign in with
  .venv\Scripts\python -m document_manager google-sign-in (GD-8).",
  "Google couldn't be reached. Nothing was saved (GD-10).", or "Google
  refused the sign-in. Nothing was saved (GD-10)."
- The sign-in command, typed by Ernie in PowerShell in the project folder:

      .venv\Scripts\python -m document_manager google-sign-in

  It opens Google's sign-in page in the browser, then says "Signed in to
  Google as <account>." Ernie checks that it's his account, as on GitHub
  (thread 05).
- A register file on Google Drive is refused too (GD-1): "<file> is on
  Google Drive, where a register file can't be (GD-1)."
- The test folder G:\My Drive\Document manager test was registered in
  thread 09 by reading its files. Its lists stay; Check, Accept and
  Summarize on it are refused from now on (GD-6).
- Stop (GD-12): "Register stopped at <time> (this computer's time).
  Nothing was saved."

Left for later:
- Check and Accept from Google's list, with each file's last-changed time
  at Google, for question 4: what changes, and how often.
- Other computers on G: (97 files in thread 15).
- Summaries of documents on Google Drive: they need the text (GD-6).
- A folder inside another registered folder is counted twice by the
  overview, each of its files as a duplicate of itself (read in the code,
  thread 15). The test folder is inside My Drive.
- A guard that stops Claude from opening the sign-in files (GD-8).
- Finding duplicates among files Google gives no fingerprint for, if
  there are many.
