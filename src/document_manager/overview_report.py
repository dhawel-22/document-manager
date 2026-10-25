"""Overview report: the overview in plain words (spec/overview.md)."""

from document_manager.overview import OTHER, Overview

# OV-10: Check saves nothing (CK-6), so only accepted changes are known.
NOTE = ("Only accepted changes are known. Check saves nothing, so a folder with\n"
        "no accepted changes may still have changed.")


def overview_report(register_file: str, result: Overview) -> str:
    """The overview, in the order and words of the example in the spec."""
    lines = [
        f"Overview of {register_file}",
        "From the register file only: the folders weren't read.",  # OV-2
        "",
        f"Folders: {len(result.folders):,}, files: {result.files:,}, "
        f"size: {size_words(result.size)}, empty files: {result.empty_files:,}.",  # OV-3, OV-8
        "",
    ]
    for folder in result.folders:  # OV-3, OV-5
        kinds = ", ".join(f"{kind.lower()} {count:,}" for kind, count in folder.kinds.items())
        lines += [
            folder.path,
            f"  Files: {folder.files:,}, size: {size_words(folder.size)}. "
            f"Newest list: {_when(folder.listed_at)}. Changes accepted: {folder.accepted:,}.",
            f"  {kinds[0].upper()}{kinds[1:]}.",
        ]
    lines += ["", "Kinds:", *_kinds(result), "", *_duplicates(result), "", *_changes(result),
              NOTE]
    return "\n".join(lines)


def size_words(size: int) -> str:
    """A size the way Windows counts it, 1 KB being 1,024 bytes, with one
    decimal, like 47.4 GB. Under 1 KB, in bytes."""
    if size < 1024:
        return "1 byte" if size == 1 else f"{size:,} bytes"
    for unit in ("KB", "MB", "GB", "TB"):
        size /= 1024
        if round(size, 1) < 1024 or unit == "TB":
            return f"{size:,.1f} {unit}"


def _kinds(result: Overview) -> list[str]:
    """Each kind's files and size in all folders, the numbers lined up on the
    right, and other's endings (OV-5)."""
    counts = {kind: f"{files:,}" for kind, (files, _) in result.kinds.items()}
    sizes = {kind: size_words(size) for kind, (_, size) in result.kinds.items()}
    count_width = max(len(count) for count in counts.values())
    size_width = max(len(size) for size in sizes.values())
    lines = []
    for kind, (files, _) in result.kinds.items():
        word = "file" if files == 1 else "files"
        line = f"  {kind:<28}{counts[kind]:>{count_width}} {word:<5}   {sizes[kind]:>{size_width}}"
        if kind == OTHER and result.other_endings:
            endings = ", ".join(f".{ending} {count:,}" if ending else f"(none) {count:,}"
                                for ending, count in result.other_endings)
            line += f"   endings: {endings}"
        lines.append(line)
    return lines


def _duplicates(result: Overview) -> list[str]:
    """The duplicates' totals, then each group with every place (OV-6, OV-7)."""
    if not result.duplicates:
        return ["Duplicates: none."]
    lines = [f"Duplicates: {_count(len(result.duplicates), 'group', 'groups')}, "
             f"{_count(result.extra_copies, 'extra copy', 'extra copies')}, "
             f"{size_words(result.extra_space)}."]
    for duplicate in result.duplicates:
        lines.append(f"  {len(duplicate.places):,} copies, {size_words(duplicate.size)} each")
        lines += [f"    {place}" for place in duplicate.places]
    return lines


def _changes(result: Overview) -> list[str]:
    """Each accepted list's changes, then the folders with none (OV-9)."""
    if not result.changes:
        return ["Changes accepted: none."]
    folders = len({change.folder for change in result.changes})
    none = sum(1 for folder in result.folders if folder.accepted == 0)
    lines = [f"Changes accepted: {_count(len(result.changes), 'list', 'lists')}, "
             f"in {_count(folders, 'folder', 'folders')}. Folders with none: {none:,}."]
    lines += [f"  {change.folder}  {_when(change.accepted_at)}: changed {change.changed:,}, "
              f"new {change.new:,}, missing {change.missing:,}." for change in result.changes]
    return lines


def _count(number: int, one: str, many: str) -> str:
    """1 group, 2 groups."""
    return f"{number:,} {one if number == 1 else many}"


def _when(saved_at: str) -> str:
    """2026-10-24T16:05:12+00:00 shown as 2026-10-24 16:05 UTC."""
    return f"{saved_at[:10]} {saved_at[11:16]} UTC"
