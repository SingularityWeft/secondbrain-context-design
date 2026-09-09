#!/usr/bin/env python3
"""Load release-specific privacy terms without storing them in the public repo."""

from __future__ import annotations

import stat
import unicodedata
from pathlib import Path


def normalized(text: str) -> str:
    return unicodedata.normalize("NFKC", text).casefold()


def load_private_denylist(path: Path | None, public_root: Path, error_type: type[Exception]) -> tuple[str, ...]:
    if path is None:
        return ()
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise error_type("Private Denylist darf kein Symlink sein")
    resolved = candidate.resolve()
    root = public_root.resolve()
    if resolved.is_relative_to(root):
        raise error_type("Private Denylist muss außerhalb des öffentlichen Repositories liegen")
    try:
        metadata = resolved.stat()
    except OSError as exc:
        raise error_type("Private Denylist ist nicht lesbar") from exc
    if not stat.S_ISREG(metadata.st_mode):
        raise error_type("Private Denylist muss eine reguläre Datei sein")
    if metadata.st_mode & 0o077:
        raise error_type("Private Denylist muss nur für den Owner lesbar sein (0600)")
    try:
        lines = resolved.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise error_type("Private Denylist ist keine lesbare UTF-8-Datei") from exc
    terms = tuple(normalized(line.strip()) for line in lines if line.strip() and not line.lstrip().startswith("#"))
    if not terms or any(len(term) < 4 for term in terms):
        raise error_type("Private Denylist benötigt mindestens einen Eintrag mit vier Zeichen")
    return terms


def matching_term(text: str, terms: tuple[str, ...]) -> bool:
    value = normalized(text)
    return any(term in value for term in terms)
