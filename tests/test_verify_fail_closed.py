from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VerifyFailClosedTests(unittest.TestCase):
    def mutation_result(self, mutate, private_term: str | None = None) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory(prefix="clief-negative-") as directory:
            parent = Path(directory)
            copy = parent / "repo"
            shutil.copytree(
                ROOT,
                copy,
                ignore=shutil.ignore_patterns(".git", ".tmp", "__pycache__", "*.pyc"),
            )
            expected_path = mutate(copy)
            arguments = [sys.executable, str(copy / "scripts/check_repository.py"), "--root", str(copy)]
            if private_term is not None:
                denylist = parent / "private-release-denylist.txt"
                denylist.write_text(private_term + "\n", encoding="utf-8")
                denylist.chmod(0o600)
                arguments.extend(["--private-denylist", str(denylist)])
            result = subprocess.run(
                arguments,
                cwd=copy,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, expected_path)
            self.assertIn(expected_path, result.stderr)
            return result

    def test_broken_link_stops_with_path(self) -> None:
        def mutate(root: Path) -> str:
            path = root / "README.md"
            path.write_text(path.read_text(encoding="utf-8") + "\n[Kaputter Testlink](fehlt.md)\n", encoding="utf-8")
            return "README.md"

        self.assertIn("Gebrochener Link", self.mutation_result(mutate).stderr)

    def test_open_marker_stops_with_path(self) -> None:
        def mutate(root: Path) -> str:
            path = root / "README.md"
            marker = "@" + "@OPEN_MARKER@" + "@"
            path.write_text(path.read_text(encoding="utf-8") + f"\n{marker}\n", encoding="utf-8")
            return "README.md"

        self.assertIn("Template-Marker", self.mutation_result(mutate).stderr)

    def test_typical_secret_stops_with_path(self) -> None:
        def mutate(root: Path) -> str:
            path = root / "README.md"
            secret = "s" + "k-" + ("x" * 30)
            path.write_text(path.read_text(encoding="utf-8") + f"\n{secret}\n", encoding="utf-8")
            return "README.md"

        self.assertIn("Typisches Secret", self.mutation_result(mutate).stderr)

    def test_personal_path_stops_with_path(self) -> None:
        def mutate(root: Path) -> str:
            path = root / "README.md"
            personal = "/" + "Users/beispiel/privat"
            path.write_text(path.read_text(encoding="utf-8") + f"\n{personal}\n", encoding="utf-8")
            return "README.md"

        self.assertIn("Persönlicher absoluter Pfad", self.mutation_result(mutate).stderr)

    def test_forbidden_claim_stops_with_path(self) -> None:
        def mutate(root: Path) -> str:
            path = root / "README.md"
            claim = "DSGVO-" + "konform"
            path.write_text(path.read_text(encoding="utf-8") + f"\n{claim}\n", encoding="utf-8")
            return "README.md"

        self.assertIn("Verbotener öffentlicher Claim", self.mutation_result(mutate).stderr)

    def test_missing_license_notice_stops_with_path(self) -> None:
        def mutate(root: Path) -> str:
            (root / "NOTICE.md").unlink()
            return "NOTICE.md"

        self.assertIn("Fehlender Pflichtpfad", self.mutation_result(mutate).stderr)

    def test_private_denylist_identity_stops_with_path(self) -> None:
        identity = "Beispielperson Geheim"

        def mutate(root: Path) -> str:
            path = root / "README.md"
            path.write_text(path.read_text(encoding="utf-8") + f"\n{identity}\n", encoding="utf-8")
            return "README.md"

        self.assertIn("privater Denylist", self.mutation_result(mutate, identity).stderr)


if __name__ == "__main__":
    unittest.main()
