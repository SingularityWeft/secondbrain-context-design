from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def check(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/check_repository.py"), "--root", str(root)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


class PrivatePracticeContractTests(unittest.TestCase):
    def copied_repo(self, directory: str) -> Path:
        target = Path(directory) / "repo"
        shutil.copytree(
            ROOT,
            target,
            ignore=shutil.ignore_patterns(".git", ".tmp", "__pycache__", "*.pyc"),
        )
        return target

    def test_two_phase_private_practice_and_public_feedback_contract_passes(self) -> None:
        result = check(ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("practice_contracts=7", result.stdout)

    def test_missing_two_phase_boundary_stops(self) -> None:
        with tempfile.TemporaryDirectory(prefix="context-practice-contract-") as directory:
            copy = self.copied_repo(directory)
            readme = copy / "README.md"
            text = readme.read_text(encoding="utf-8")
            text = text.replace("Zwei Phasen", "Ablauf").replace("zwei Phasen", "Ablauf")
            readme.write_text(text, encoding="utf-8")
            result = check(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("README.md", result.stderr)
            self.assertIn("Zwei-Phasen", result.stderr)

    def test_missing_public_redaction_boundary_stops(self) -> None:
        with tempfile.TemporaryDirectory(prefix="context-contribution-contract-") as directory:
            copy = self.copied_repo(directory)
            contribution = copy / "CONTRIBUTING.md"
            contribution.write_text(
                contribution.read_text(encoding="utf-8").replace(
                    "synthetischen oder vollständig bereinigten Angaben",
                    "passenden Angaben",
                ),
                encoding="utf-8",
            )
            result = check(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CONTRIBUTING.md", result.stderr)

    def test_templates_keep_private_instance_content_out_of_github(self) -> None:
        issue = (ROOT / ".github/ISSUE_TEMPLATE/praxistest.yml").read_text(encoding="utf-8")
        pull_request = (ROOT / ".github/PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
        self.assertIn("keine echten Unternehmens-, Kunden- oder Personendaten", issue)
        self.assertIn("Private Instanzdateien wurden nicht", pull_request)
        self.assertIn("keine Secrets", issue)
        self.assertIn("keine Secrets", pull_request)


if __name__ == "__main__":
    unittest.main()
