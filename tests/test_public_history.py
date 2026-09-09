from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts/check_public_history.py"


def command(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(arguments, cwd=root, capture_output=True, text=True, check=False)


def create_repo(parent: Path, content: str = "Öffentlicher synthetischer Starter.\n") -> Path:
    repo = parent / "repo"
    repo.mkdir()
    command(repo, "git", "init", "-b", "main").check_returncode()
    command(repo, "git", "config", "user.name", "Public Starter Maintainer").check_returncode()
    command(repo, "git", "config", "user.email", "maintainer@example.invalid").check_returncode()
    (repo / "README.md").write_text(content, encoding="utf-8")
    command(repo, "git", "add", "README.md").check_returncode()
    command(repo, "git", "commit", "-m", "Initial public release candidate").check_returncode()
    return repo


def check(repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return command(repo, sys.executable, str(CHECKER), "--root", str(repo), *extra)


def private_denylist(parent: Path, value: str, mode: int = 0o600) -> Path:
    path = parent / "private-release-denylist.txt"
    path.write_text(value + "\n", encoding="utf-8")
    path.chmod(mode)
    return path


class PublicHistoryTests(unittest.TestCase):
    def test_single_clean_root_commit_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = create_repo(Path(directory))
            result = check(repo)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("commits=1", result.stdout)
            self.assertIn("unreachable=0", result.stdout)

    def test_private_identity_in_root_commit_stops_with_external_denylist(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            identity = "Beispielperson Geheim"
            repo = create_repo(parent, f"Private Pilotperson: {identity}\n")
            denylist = private_denylist(parent, identity)
            result = check(repo, "--private-denylist", str(denylist))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("privater Denylist in Git-Objekt", result.stderr)

    def test_private_denylist_inside_repo_or_broadly_readable_stops(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            repo = create_repo(parent)
            inside = repo / "denylist.txt"
            inside.write_text("Beispielperson Geheim\n", encoding="utf-8")
            inside.chmod(0o600)
            self.assertNotEqual(check(repo, "--private-denylist", str(inside)).returncode, 0)
            outside = private_denylist(parent, "Beispielperson Geheim", mode=0o644)
            result = check(repo, "--private-denylist", str(outside))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("nur für den Owner", result.stderr)

    def test_public_checker_contains_no_fixed_identity_fingerprint_table(self) -> None:
        source = CHECKER.read_text(encoding="utf-8")
        self.assertNotIn("FORBIDDEN_IDENTITY_DIGESTS", source)

    def test_clean_followup_commit_passes_normal_policy_but_not_reset_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = create_repo(Path(directory))
            (repo / "README.md").write_text("Zweiter Stand.\n", encoding="utf-8")
            command(repo, "git", "add", "README.md").check_returncode()
            command(repo, "git", "commit", "-m", "Second commit").check_returncode()
            result = check(repo)
            self.assertEqual(result.returncode, 0, result.stderr)
            reset_gate = check(repo, "--require-single-root")
            self.assertNotEqual(reset_gate.returncode, 0)
            self.assertIn("genau einen Root-Commit", reset_gate.stderr)


if __name__ == "__main__":
    unittest.main()
