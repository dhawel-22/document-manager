"""Report: what the check found, in plain words (spec/report.md)."""

from document_manager.check import CheckResult


def report(result: CheckResult) -> str:
    """One line with the counts, then every finding (RP-2), or one line if
    nothing has changed (RP-3)."""
    if not (result.changed or result.new or result.missing):
        return f"Nothing has changed. Files checked: {result.unchanged}."
    lines = [
        f"Changed: {len(result.changed)}, new: {len(result.new)}, "
        f"missing: {len(result.missing)}, unchanged: {result.unchanged}."
    ]
    for label, places in (
        ("changed", result.changed),
        ("new", result.new),
        ("missing", result.missing),
    ):
        lines += [f"  {label:<7}  {place}" for place in places]
    return "\n".join(lines)
