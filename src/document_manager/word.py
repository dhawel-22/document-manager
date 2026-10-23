"""Word: one Word document's Stage A summary (spec/summaries.md, SM-3, SM-6).

Documents are opened for reading only. Nothing here can save, change, move
or delete a document (SM-5).
"""

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

import docx
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.table import Table
from docx.text.paragraph import Paragraph

FIRST_WORDS = 60  # SM-3
# Old .doc files and password-protected .docx files both start with these bytes.
OLD_FORMAT = bytes.fromhex("D0CF11E0A1B11AE1")
HEADING = re.compile(r"Heading ([1-9])")


@dataclass
class Summary:
    """A Stage A summary, taken straight from the document (SM-3)."""

    title: str  # "" when the document has no title
    headings: list[tuple[int, str]]  # (level, text), in order
    first_words: str
    word_count: int


class CouldNotRead(Exception):
    """A document that can't be summarized; the message is the reason (SM-6)."""


def summarize_document(path: Path | str) -> Summary:
    """Read one Word document and return its Stage A summary (SM-3).

    Raises CouldNotRead with the reason, instead of guessing (SM-6).
    """
    path = Path(path)
    if path.name.startswith("~$"):
        raise CouldNotRead("Word's temporary lock file, not a document")
    if path.suffix.lower() == ".doc":
        raise CouldNotRead("old Word file (.doc); save it as .docx in Word first")
    try:
        with open(path, "rb") as f:
            if f.read(len(OLD_FORMAT)) == OLD_FORMAT:
                raise CouldNotRead("protected with a password, or not a real .docx inside")
        document = docx.Document(str(path))
        title = _saved_title(document)
        headings = []
        words = []
        for paragraph in _paragraphs(document.iter_inner_content()):
            text = paragraph.text.strip()
            style = (paragraph.style.name if paragraph.style is not None else "") or ""
            if not title and style == "Title" and text:
                title = text
            heading = HEADING.fullmatch(style)
            if heading and text:
                headings.append((int(heading.group(1)), text))
            words.extend(paragraph.text.split())
    except CouldNotRead:
        raise
    except Exception as error:  # one unreadable document is listed, not fatal (SM-6)
        raise CouldNotRead(f"{type(error).__name__}: {error}") from error
    return Summary(title, headings, " ".join(words[:FIRST_WORDS]), len(words))


def _saved_title(document) -> str:
    """The title saved in the document itself, or "" if there is none (SM-3).

    Asked for directly, because for a document with no saved properties the
    library's usual way makes up the title "Word Document".
    """
    try:
        saved = document.part.package.part_related_by(RELATIONSHIP_TYPE.CORE_PROPERTIES)
    except KeyError:
        return ""
    return (saved.core_properties.title or "").strip()


def _paragraphs(blocks: Iterable[Paragraph | Table]) -> Iterator[Paragraph]:
    """Every paragraph in reading order, going into tables (SM-3).

    A merged table cell is read once, not once for each column it covers.
    """
    for block in blocks:
        if isinstance(block, Table):
            seen = set()  # each cell's own XML element; kept, so it stays the same object
            for row in block.rows:
                for cell in row.cells:
                    if cell._tc in seen:  # _tc: the library's name for the cell's XML
                        continue
                    seen.add(cell._tc)
                    yield from _paragraphs(cell.iter_inner_content())
        else:
            yield block
