# Fingerprint

**Version:** 1.0 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "03 · Lighter routine"

A file's fingerprint is a short code made from its contents. The program
uses it to tell whether a file has changed.

| ID | Rule |
|---|---|
| FP-1 | The fingerprint is the SHA-256 of the file's exact bytes: 64 characters, digits 0–9 and letters a–f. |
| FP-2 | Files with the same contents get the same fingerprint, whatever their names or folders. |
| FP-3 | Changing the contents, even by one letter, changes the fingerprint. |
| FP-4 | Making a fingerprint only reads the file. It never changes it. |
| FP-5 | If the file can't be read, the program says so. It never makes up a fingerprint. |
