"""Summary report: summaries in plain words (spec/summaries.md, SM-8)."""

from document_manager.summaries import SavedSummary, SummarizeResult


def summarize_report(result: SummarizeResult) -> str:
    """One line with the counts, then each document that couldn't be read."""
    lines = [
        f"Summarized: {len(result.summarized)}, unchanged: {result.unchanged}, "
        f"couldn't read: {len(result.could_not_read)}."
    ]
    lines += [f"  couldn't read  {place}  {reason}" for place, reason in result.could_not_read]
    return "\n".join(lines)


def summaries_report(folder: str, summaries: list[SavedSummary]) -> str:
    """Each document's place and latest summary, then the "couldn't read"
    list (SM-8)."""
    if not summaries:
        return f"No summaries yet for {folder}. Run summarize first."
    read = [s for s in summaries if s.problem is None]
    unread = [s for s in summaries if s.problem is not None]
    lines = [f"Summaries for {folder}. Documents: {len(read)}, couldn't read: {len(unread)}."]
    for s in read:
        lines += ["", f"{s.place}  (summarized {_when(s.made_at)})"]
        lines.append(f"  Title:    {s.title or 'no title'}")
        if s.headings:
            lines.append("  Headings:")
            lines += [f"    {'  ' * (level - 1)}{text}" for level, text in s.headings]
        else:
            lines.append("  Headings: none")
        lines.append(f"  Starts:   {s.first_words or '(no text)'}")
        lines.append(f"  Words:    {s.word_count}")
    if unread:
        lines += ["", "Couldn't read:"]
        lines += [f"  {s.place}  {s.problem}" for s in unread]
    return "\n".join(lines)


def _when(made_at: str) -> str:
    """2026-10-23T16:40:12+00:00 shown as 2026-10-23 16:40 UTC."""
    return f"{made_at[:10]} {made_at[11:16]} UTC"
