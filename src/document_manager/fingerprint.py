"""Fingerprint: a short code made from a file's contents (spec/fingerprint.md)."""

import hashlib
from pathlib import Path
from typing import BinaryIO


def fingerprint(path: Path | str) -> str:
    """Return the SHA-256 of the file's exact bytes, as 64 hex characters (FP-1).

    The file is opened for reading only (FP-4). If it can't be read, the error
    is raised, never hidden behind a made-up value (FP-5).
    """
    with open(path, "rb") as f:
        return fingerprint_of(f)


def fingerprint_of(f: BinaryIO) -> str:
    """The same, for a file already open for reading (FP-1)."""
    return hashlib.file_digest(f, "sha256").hexdigest()
