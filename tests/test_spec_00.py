from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_spec_00.py"


def run_checker(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


class Spec00ContractTests(unittest.TestCase):
    def test_repository_contract_is_complete(self) -> None:
        result = run_checker("repo")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("REPO_POLICY_PASS", result.stdout)

    def test_bounded_claim_is_allowed(self) -> None:
        result = run_checker("claim", "Lokaler technischer Alpha mit synthetischen Daten")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_forbidden_claim_classes_are_blocked(self) -> None:
        claims = (
            "DSGVO-konform",
            "State of the Art",
            "autonome Unternehmensführung",
            "garantierter Umsatz",
        )
        for claim in claims:
            with self.subTest(claim=claim):
                result = run_checker("claim", claim)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("CLAIM_BLOCKED", result.stderr)

    def test_local_action_is_allowed(self) -> None:
        result = run_checker("action", "verify-local")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_external_and_unknown_actions_stop(self) -> None:
        for action, marker in (
            ("send-external", "HUMAN_GATE_REQUIRED"),
            ("reputation-claim", "HUMAN_GATE_REQUIRED"),
            ("invented-action", "UNKNOWN_ACTION_STOP"),
        ):
            with self.subTest(action=action):
                result = run_checker("action", action)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(marker, result.stderr)

    def test_synthetic_input_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.md"
            path.write_text(
                "---\ndata_class: synthetic\nsynthetic: true\n---\nFantasie GmbH plant einen erfundenen Workshop.\n",
                encoding="utf-8",
            )
            result = run_checker("input", str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SAFE_SYNTHETIC_INPUT", result.stdout)

    def test_unclassified_or_sensitive_input_stops(self) -> None:
        samples = (
            "---\ndata_class: confidential\nsynthetic: false\n---\nInterne Notiz\n",
            "---\ndata_class: synthetic\nsynthetic: true\n---\nKontakt: anna@firma.example\n",
        )
        for sample in samples:
            with self.subTest(sample=sample.splitlines()[1]):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "input.md"
                    path.write_text(sample, encoding="utf-8")
                    result = run_checker("input", str(path))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("STOP_DATA_POLICY", result.stderr)


if __name__ == "__main__":
    unittest.main()
