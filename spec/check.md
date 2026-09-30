# Check

**Version:** 1.0 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "03 · Lighter routine"

The check compares a registered folder with its list in the register file
(spec/register.md), to find what has changed since it was registered.

| ID | Rule |
|---|---|
| CK-1 | Checking a registered folder compares every file in it now with its list. Files that match the list are unchanged. |
| CK-2 | A file whose fingerprint is different from the list is changed. |
| CK-3 | A file on the list that is no longer in the folder is missing. |
| CK-4 | A file in the folder that isn't on the list is new. |
| CK-5 | A moved or renamed file shows as missing at its old place and new at its new place. |
| CK-6 | Checking only reads. It never changes the files or the register file. |
| CK-7 | A folder that isn't in the register file is refused. |
| CK-8 | If the folder, the register file or any file in the folder can't be read, the check stops and says which one. It never guesses. |
