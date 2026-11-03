"""Summary report: summaries in plain words (spec/summaries.md, SM-8, and
spec/ai-summaries.md, Commands)."""

from document_manager.ai_summaries import AiSummarizeResult, SavedAiSummary
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


def ai_summarize_report(result: AiSummarizeResult) -> str:
    """One line with the counts, then each document with no AI summary, and
    why (AI-6, AI-11, SM-6)."""
    lines = [
        f"AI summaries made: {len(result.made)}, unchanged: {result.unchanged}, "
        f"too long: {len(result.too_long)}, couldn't read: {len(result.could_not_read)}, "
        f"not made: {len(result.not_made)}."
    ]
    lines += [f"  too long  {place}  {words} words" for place, words in result.too_long]
    lines += [f"  couldn't read  {place}  {reason}" for place, reason in result.could_not_read]
    lines += [f"  not made  {place}  {reason}" for place, reason in result.not_made]
    return "\n".join(lines)


def ai_summaries_report(folder: str, summaries: list[SavedAiSummary]) -> str:
    """Each document's place and latest AI summary, with when and by which
    model it was made."""
    if not summaries:
        return f"No AI summaries yet for {folder}. Run ai-summarize first."
    lines = [f"AI summaries for {folder}. Documents: {len(summaries)}."]
    for s in summaries:
        lines += ["", f"{s.place}  (made {_when(s.made_at)} by {s.model})"]
        lines += [f"  {line}" for line in s.summary.splitlines() if line.strip()]
    return "\n".join(lines)


def _when(made_at: str) -> str:
    """2026-10-23T16:40:12+00:00 shown as 2026-10-23 16:40 UTC."""
    return f"{made_at[:10]} {made_at[11:16]} UTC"
