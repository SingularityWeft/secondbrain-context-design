from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts/check_repository.py"
E2E = ROOT / "scripts/run_e2e.py"
CI = ROOT / ".github/workflows/verify.yml"
CHECKOUT_COMMIT = "3d3c42e5aac5ba805825da76410c181273ba90b1"


def command(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(arguments, cwd=ROOT, capture_output=True, text=True, check=False)


class Spec05VerifyTests(unittest.TestCase):
    def test_repository_contract_passes(self) -> None:
        result = command([sys.executable, str(CHECKER)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("REPOSITORY_CONTRACT_PASS", result.stdout)

    def test_complete_synthetic_e2e_preserves_outputs_and_index(self) -> None:
        result = command([sys.executable, str(E2E)])
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "E2E_PASS")
        self.assertEqual(payload["data_class"], "synthetic")
        self.assertTrue(payload["technical_fixture_not_human"])
        self.assertTrue(payload["artifact_hashes_preserved"])
        self.assertTrue(payload["manual_hash_preserved"])
        self.assertTrue(payload["foreign_hash_preserved"])
        self.assertTrue(payload["git_index_unchanged"])
        self.assertFalse(payload["external_writes"])
        self.assertEqual(len(payload["artifact_sequence"]), 15)
        self.assertEqual(payload["hash_evidence"]["before_rerun"], payload["hash_evidence"]["after_rerun"])
        self.assertTrue(all(len(value) == 64 for value in payload["artifact_sha256"].values()))
        self.assertEqual(
            set(payload["expected_worktree_status"]),
            {
                " M 01-ausrichtung/business-context.md",
                "?? 00-eingang/fremde-synthetische-notiz.md",
            },
        )

    def test_ci_is_read_only_pinned_and_calls_only_canonical_verify(self) -> None:
        text = CI.read_text(encoding="utf-8")
        self.assertIn("permissions:\n  contents: read", text)
        self.assertIn(f"actions/checkout@{CHECKOUT_COMMIT}", text)
        self.assertEqual(text.count("run:"), 1)
        self.assertIn("run: bash scripts/verify-repo.sh", text)
        self.assertNotIn("secrets" + ".", text)
        self.assertNotIn("pip install", text)
        self.assertNotIn("npm install", text)

    def test_beginner_walkthrough_remains_blocked_without_person(self) -> None:
        walkthrough = (ROOT / "docs/testing/anfaenger-walkthrough.md").read_text(encoding="utf-8")
        form = (ROOT / "docs/testing/ergebnisformular.md").read_text(encoding="utf-8")
        self.assertIn("blocked – reale unabhängige Testperson fehlt", walkthrough)
        self.assertIn("mit Hilfe", form)
        self.assertIn("Anlass und Umfang der Hilfe", form)
        self.assertIn("nicht ausgeführt", form)


if __name__ == "__main__":
    unittest.main()
