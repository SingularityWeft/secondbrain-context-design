from __future__ import annotations

import json
import platform
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "scripts" / "runtime_isolation_probe.py"
POLICY = ROOT / "_core" / "runtime-policy.json"
RECORDED_PROBE = ROOT / "_evidence" / "runtime" / "macos-codex-probe.json"


class Spec01RuntimeTests(unittest.TestCase):
    @unittest.skipUnless(platform.system() == "Darwin", "macOS isolation contract")
    def test_runtime_probe_enforces_boundaries(self) -> None:
        result = subprocess.run(
            [sys.executable, str(PROBE)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        evidence = json.loads(result.stdout)
        self.assertEqual(evidence["status"], "pass")
        self.assertFalse(evidence["logged_content"])
        self.assertEqual(evidence["failures"], [])
        for check in evidence["checks"].values():
            self.assertEqual(check["result"], "pass")

    def test_runtime_policy_remains_restricted(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertEqual(policy["primary_status"], "restricted-synthetic-only")
        self.assertEqual(policy["owner_decision"], "unsigned-technical-default")
        self.assertIn("claude-desktop", policy["unsupported_for_confidential_data"])
        self.assertIn("deny-network", policy["required_controls"])
        self.assertIn("deny-git-metadata-write", policy["required_controls"])

    def test_recorded_probe_is_content_free_and_pinned(self) -> None:
        evidence = json.loads(RECORDED_PROBE.read_text(encoding="utf-8"))
        self.assertEqual(evidence["status"], "pass")
        self.assertFalse(evidence["logged_content"])
        self.assertEqual(evidence["failures"], [])
        self.assertEqual(
            evidence["environment"]["workspace_sha"],
            "89bd45cd3aaa0f3339c738eb0039d3ed7dea8e22",
        )

    def test_runtime_matrix_has_exactly_one_primary_path(self) -> None:
        matrix = (ROOT / "docs" / "runtime" / "runtime-matrix.md").read_text(encoding="utf-8")
        self.assertEqual(matrix.count("**primärer technischer Default;"), 1)
        self.assertIn("isolation-unverified / synthetic-only", matrix)
        self.assertIn("Daemon und lokales Testimage nicht verfügbar", matrix)

    def test_claude_desktop_is_not_overclaimed(self) -> None:
        desktop = (ROOT / "docs" / "runtime" / "claude-desktop.md").read_text(encoding="utf-8")
        self.assertIn("Kein echter Datei-, Canary- oder Netztest", desktop)
        self.assertIn("kein primär unterstützter Pfad", desktop)
        self.assertIn("nicht für vertrauliche Nutzung freigegeben", desktop)


if __name__ == "__main__":
    unittest.main()
