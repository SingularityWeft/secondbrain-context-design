#!/usr/bin/env python3
"""Verify a public repository's reachable history, object closure, and privacy terms."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

from privacy_denylist import load_private_denylist, matching_term


ROOT = Path(__file__).resolve().parents[1]
class HistoryError(RuntimeError):
    pass


def git(root: Path, *arguments: str, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        input=input_bytes,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise HistoryError(f"git {' '.join(arguments)} fehlgeschlagen: {detail}")
    return result.stdout


def object_inventory(root: Path) -> tuple[set[str], dict[str, str]]:
    reachable_lines = git(root, "rev-list", "--objects", "--all").decode("ascii").splitlines()
    reachable = {line.split(" ", 1)[0] for line in reachable_lines if line}
    all_lines = git(
        root,
        "cat-file",
        "--batch-all-objects",
        "--batch-check=%(objectname) %(objecttype)",
    ).decode("ascii").splitlines()
    all_objects: dict[str, str] = {}
    for line in all_lines:
        object_id, object_type = line.split(" ", 1)
        all_objects[object_id] = object_type
    if set(all_objects) != reachable:
        raise HistoryError("Nicht erreichbare oder fremde Git-Objekte im Public Repo erkannt")
    return reachable, all_objects


def scan_object(root: Path, object_id: str, private_terms: tuple[str, ...]) -> None:
    content = git(root, "cat-file", "-p", object_id)
    text = content.decode("utf-8", errors="ignore")
    if matching_term(text, private_terms):
        raise HistoryError(f"Eintrag aus privater Denylist in Git-Objekt {object_id[:12]} erkannt")


def check_branch_context(root: Path) -> None:
    branches = git(root, "for-each-ref", "--format=%(refname:short)", "refs/heads").decode("utf-8").splitlines()
    if branches == ["main"]:
        return
    expected_sha = os.environ.get("GITHUB_SHA", "")
    is_verified_github_checkout = (
        branches == []
        and os.environ.get("GITHUB_ACTIONS") == "true"
        and re.fullmatch(r"[0-9a-f]{40}", expected_sha) is not None
        and git(root, "rev-parse", "HEAD").decode("ascii").strip() == expected_sha
    )
    if not is_verified_github_checkout:
        raise HistoryError("Public Repo muss lokal main oder ein verifizierter GitHub-Actions-Checkout sein")


def check(root: Path, require_single_root_commit: bool, private_denylist: Path | None = None) -> tuple[int, int]:
    if not (root / ".git").is_dir():
        raise HistoryError("Public Repo besitzt kein lokales .git-Verzeichnis")
    check_branch_context(root)
    commit_count = int(git(root, "rev-list", "--count", "--all").decode("ascii").strip())
    if commit_count < 1:
        raise HistoryError("Public Repo besitzt noch keinen Commit")
    roots = git(root, "rev-list", "--max-parents=0", "--all").decode("ascii").splitlines()
    if len(roots) != 1:
        raise HistoryError(f"Public Repo muss genau eine Historienwurzel besitzen, gefunden {len(roots)}")
    if require_single_root_commit and commit_count != 1:
        raise HistoryError(f"Public Reset muss genau einen Root-Commit besitzen, gefunden {commit_count}")
    private_terms = load_private_denylist(private_denylist, root, HistoryError)
    reachable, all_objects = object_inventory(root)
    for object_id, object_type in all_objects.items():
        if object_type in {"blob", "commit", "tag"}:
            scan_object(root, object_id, private_terms)
    return commit_count, len(reachable)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--require-single-root", action="store_true")
    parser.add_argument("--private-denylist", type=Path)
    args = parser.parse_args()
    try:
        commits, objects = check(args.root.resolve(), args.require_single_root, args.private_denylist)
    except (HistoryError, OSError, UnicodeError, ValueError) as exc:
        print(f"PUBLIC_HISTORY_STOP: {exc}", file=sys.stderr)
        return 2
    print(f"PUBLIC_HISTORY_PASS commits={commits} objects={objects} identity_matches=0 unreachable=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
