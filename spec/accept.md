# Accept

**Version:** 1.0 · **Owner:** Ernie · **Approved by:** Ernie, by merging the
pull request that added this file
**Drafted by:** Claude, in thread "08 · Before Phase 2"

Accepting tells the register that a registered folder's changes are
wanted. After that, the check compares the folder with the new list.

| ID | Rule |
|---|---|
| AC-1 | Accepting a registered folder first shows what has changed, exactly as Check would, and saves nothing until the person says yes. |
| AC-2 | On yes, a new list of the folder is saved, made the same way as registering (RG-1), with the date and time (UTC). |
| AC-3 | Old lists are kept. They are never changed or deleted. |
| AC-4 | The check always uses the newest list. |
| AC-5 | Accepting takes the whole folder: every changed, new and missing file. |
| AC-6 | If nothing has changed, nothing is saved, and the program says so. |
| AC-7 | Accepting only reads the files. The register file is the only thing it writes. |
| AC-8 | A folder that isn't in the register file is refused. |
| AC-9 | If the folder or any file in it can't be read, nothing is saved, and the program says which one. |
