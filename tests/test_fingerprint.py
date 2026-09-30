"""Tests for the fingerprint rules in spec/fingerprint.md (FP-1 to FP-5)."""

import hashlib

import pytest

from document_manager.fingerprint import fingerprint

# Answer keys, worked out with Windows' own SHA-256, not with Python.
HELLO = "5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03"
EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_fp1_matches_the_answer_key(tmp_path):
    hello = tmp_path / "hello.txt"
    hello.write_bytes(b"hello\n")
    empty = tmp_path / "empty.txt"
    empty.write_bytes(b"")
    assert fingerprint(hello) == HELLO
    assert fingerprint(empty) == EMPTY


def test_fp1_big_file(tmp_path):
    data = bytes(range(256)) * 20_000  # about 5 MB
    big = tmp_path / "big.bin"
    big.write_bytes(data)
    assert fingerprint(big) == hashlib.sha256(data).hexdigest()


def test_fp2_same_contents_same_fingerprint(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    one = tmp_path / "a" / "letter.txt"
    two = tmp_path / "b" / "copy of letter.docx"
    one.write_bytes(b"Dear Ernie\n")
    two.write_bytes(b"Dear Ernie\n")
    assert fingerprint(one) == fingerprint(two)


def test_fp3_one_letter_changes_it(tmp_path):
    f = tmp_path / "note.txt"
    f.write_bytes(b"hello\n")
    before = fingerprint(f)
    f.write_bytes(b"hallo\n")
    assert fingerprint(f) != before


def test_fp4_only_reads(tmp_path):
    f = tmp_path / "note.txt"
    f.write_bytes(b"hello\n")
    stamp = f.stat().st_mtime_ns
    fingerprint(f)
    assert f.read_bytes() == b"hello\n"
    assert f.stat().st_mtime_ns == stamp


def test_fp5_missing_file_is_an_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        fingerprint(tmp_path / "not-there.txt")
