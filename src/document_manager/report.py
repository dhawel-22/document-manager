"""Report: what the check found, in plain words (spec/report.md)."""

from document_manager.check import CheckResult


def report(result: CheckResult) -> str:
    """One line with the counts, then every finding (RP-2), or one line if
    nothing has changed and every file could be read (RP-3, BF-8)."""
    if not (result.changed or result.new or result.missing or result.could_not_read):
        return f"Nothing has changed. Files checked: {result.unchanged}."
    counts = (f"Changed: {len(result.changed)}, new: {len(result.new)}, "
              f"missing: {len(result.missing)}, unchanged: {result.unchanged}")
    if result.could_not_read:
        counts += f", couldn't read: {len(result.could_not_read)}"
    lines = [f"{counts}."]
    for label, places in (
        ("changed", result.changed),
        ("new", result.new),
        ("missing", result.missing),
    ):
        lines += [f"  {label:<7}  {place}" for place in places]
    lines += [f"  couldn't read  {place}  {why}" for place, why in result.could_not_read]
    return "\n".join(lines)
