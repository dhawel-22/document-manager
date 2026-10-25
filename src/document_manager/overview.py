"""Overview: where the files are, worked out from the register file alone
(spec/overview.md, OV-1 to OV-9, OV-11).

Only the register file is read, and it is opened read-only (OV-1). The
folders and their files are never opened.
"""

import sqlite3
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

from document_manager.check import compare
from document_manager.register import VERSION

# The five kinds, in the order the overview shows them (OV-4).
DOCUMENTS = "Documents"
MEDIA = "Pictures, sound and video"
PROGRAMS = "Program files"
BACKUPS = "Backups and archives"
OTHER = "Other"
KINDS = (DOCUMENTS, MEDIA, PROGRAMS, BACKUPS, OTHER)

# Each kind's endings (spec/overview.md, Details). Any other ending is other.
ENDINGS = {
    DOCUMENTS: "doc docx docm dot dotx rtf odt txt md pdf xls xlsx xlsm xlsb xltx csv ods"
               " ppt pptx odp msg eml htm html mhtml ics vsd vsdx pub one mdb accdb",
    MEDIA: "jpg jpeg png gif bmp tif tiff heic webp svg ico mp3 wav wma m4a flac aac ogg"
           " mp4 mov avi wmv mkv m4v mpg mpeg webm",
    BACKUPS: "zip 7z rar tar gz tgz bz2 xz zst cab iso img vhd vhdx bak bkf old",
    PROGRAMS: "exe dll msi ocx ax sys bat cmd ps1 vbs js ts py pyc pyd pyi ipynb jar class"
              " json yaml yml toml ini cfg config inf xml sql sqlite db winmd pkg"
              " appinstaller typed",
}
KIND_OF_ENDING = {ending: kind for kind, endings in ENDINGS.items() for ending in endings.split()}

# A file inside a folder with one of these names is a program file, whatever
# its ending (OV-4).
PROGRAM_FOLDERS = {".git", "node_modules", "__pycache__", ".venv", "venv", "site-packages"}

Listing = list[tuple[str, int, str]]  # each file's place, size and fingerprint


@dataclass
class FolderOverview:
    """One registered folder, by its newest list (OV-2, OV-3, OV-5)."""

    path: str  # the folder's full path, as the register file saves it
    files: int
    size: int  # in bytes
    listed_at: str  # when its newest list was saved: date and time, UTC
    accepted: int  # how many times its changes were accepted
    kinds: dict[str, int]  # its files of each kind, in the order of KINDS


@dataclass
class Duplicate:
    """Files with the same fingerprint in more than one place (OV-6)."""

    size: int  # of each copy, in bytes
    places: list[str]  # full paths, folder by folder, ignoring capitals

    @property
    def extra_space(self) -> int:
        """The space taken by every copy but one (OV-7)."""
        return self.size * (len(self.places) - 1)


@dataclass
class Change:
    """An accepted list, compared with the list before it (OV-9)."""

    folder: str
    accepted_at: str  # date and time, UTC
    changed: int
    new: int
    missing: int


@dataclass
class Overview:
    """What the overview shows, worked out from the register file alone."""

    folders: list[FolderOverview]  # by path, ignoring capitals (OV-3)
    kinds: dict[str, tuple[int, int]]  # each kind's files and size, in all folders (OV-5)
    other_endings: list[tuple[str, int]]  # other's ten most common; "" for none (OV-5)
    duplicates: list[Duplicate]  # the most extra space first (OV-6)
    empty_files: int  # counted on their own, not as duplicates (OV-8)
    changes: list[Change]  # folder by folder, oldest first (OV-9)

    @property
    def files(self) -> int:
        return sum(folder.files for folder in self.folders)

    @property
    def size(self) -> int:
        return sum(folder.size for folder in self.folders)

    @property
    def extra_copies(self) -> int:
        """Every copy but one, in all the duplicates (OV-7)."""
        return sum(len(duplicate.places) - 1 for duplicate in self.duplicates)

    @property
    def extra_space(self) -> int:
        """The space the extra copies take (OV-7)."""
        return sum(duplicate.extra_space for duplicate in self.duplicates)


def overview(register_file: Path | str) -> Overview:
    """Work out the overview of every folder in the register file (OV-2)."""
    register_file = Path(register_file).resolve(strict=True)  # never made here (OV-11)
    con = sqlite3.connect(f"{register_file.as_uri()}?mode=ro", uri=True)  # OV-1
    try:
        lists_of = _lists(con, register_file)
    finally:
        con.close()

    folders, changes = [], []
    files_of, size_of, endings = Counter(), Counter(), Counter()
    copies = {}  # each fingerprint's size and places (OV-6)
    empty = 0
    for path in sorted(lists_of, key=_order):
        lists = lists_of[path]
        listed_at, newest = lists[-1]  # the newest list, the one Check uses (OV-2)
        kinds = dict.fromkeys(KINDS, 0)
        for place, size, fp in newest:
            full = str(PureWindowsPath(path, *place.split("/")))
            kind = kind_of(full)
            kinds[kind] += 1
            files_of[kind] += 1
            size_of[kind] += size
            if kind == OTHER:
                endings[ending(place.rsplit("/", 1)[-1])] += 1
            if size == 0:  # empty files all have the same fingerprint (OV-8)
                empty += 1
            else:
                copies.setdefault(fp, (size, []))[1].append(full)
        folders.append(FolderOverview(path, len(newest), sum(row[1] for row in newest),
                                      listed_at, len(lists) - 1, kinds))
        for (_, before), (accepted_at, after) in zip(lists, lists[1:]):  # OV-9
            found = compare(_fingerprints(before), _fingerprints(after))
            changes.append(Change(path, accepted_at, len(found.changed), len(found.new),
                                  len(found.missing)))
    duplicates = [Duplicate(size, sorted(places, key=_order))
                  for size, places in copies.values() if len(places) > 1]
    return Overview(
        folders=folders,
        kinds={kind: (files_of[kind], size_of[kind]) for kind in KINDS},
        # the most files first; the same number in alphabetical order
        other_endings=sorted(endings.items(), key=lambda item: (-item[1], item[0]))[:10],
        duplicates=sorted(duplicates, key=lambda d: (-d.extra_space, _order(d.places[0]))),
        empty_files=empty,
        changes=changes,
    )


def kind_of(path: str) -> str:
    """A file's kind, from its full path (OV-4)."""
    parts = PureWindowsPath(path).parts
    if any(part.lower() in PROGRAM_FOLDERS for part in parts[:-1]):
        return PROGRAMS
    return KIND_OF_ENDING.get(ending(parts[-1]), OTHER)


def ending(name: str) -> str:
    """The part of a name after its last dot, ignoring capitals. A name with
    no dot, or whose only dot comes first, like .gitignore, has none: ""."""
    dot = name.rfind(".")
    return name[dot + 1:].lower() if dot > 0 else ""


def _lists(con: sqlite3.Connection, register_file: Path) -> dict[str, list[tuple[str, Listing]]]:
    """Each folder's lists with their dates, oldest first: the list saved when
    it was registered, then each accepted list (OV-2, OV-9). Older register
    files are read as they are."""
    version = con.execute("PRAGMA user_version").fetchone()[0]
    if version == 0:
        raise ValueError(f"{register_file} isn't a register file (OV-11)")
    if version > VERSION:
        raise ValueError(f"Unknown register file version: {version}")
    lists_of = {}
    for folder_id, path, registered_at in con.execute(
            "SELECT id, path, registered_at FROM folder").fetchall():
        lists = [(registered_at, con.execute(
            "SELECT path, size, fingerprint FROM file WHERE folder_id = ?", (folder_id,)
        ).fetchall())]
        if version >= 3:  # accepted lists came in version 3
            for accepted_id, accepted_at in con.execute(
                    "SELECT id, accepted_at FROM accepted WHERE folder_id = ? ORDER BY id",
                    (folder_id,)).fetchall():
                lists.append((accepted_at, con.execute(
                    "SELECT path, size, fingerprint FROM accepted_file WHERE accepted_id = ?",
                    (accepted_id,)).fetchall()))
        lists_of[path] = lists
    if not lists_of:
        raise ValueError(f"There are no folders in {register_file} yet (OV-11)")
    return lists_of


def _order(path: str) -> list[str]:
    """Folder by folder, ignoring capitals (like spec/summaries.md)."""
    return [part.lower() for part in PureWindowsPath(path).parts]


def _fingerprints(listing: Listing) -> dict[str, str]:
    """Each place's fingerprint, the way the check compares them."""
    return {place: fp for place, _, fp in listing}
