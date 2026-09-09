from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts/check_pilot.py"
HUMAN_GATES = {
    "primary-run",
    "independent-beginner-walkthroughs",
    "claude-desktop-isolation",
    "privacy-and-public-claims",
    "strategic-priority",
    "public-freebie-push-release",
}


def run_checker(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/check_pilot.py"), "--root", str(root), *arguments],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


class Spec06PilotTests(unittest.TestCase):
    def copied_repo(self, directory: str) -> Path:
        target = Path(directory) / "repo"
        shutil.copytree(
            ROOT,
            target,
            ignore=shutil.ignore_patterns(".git", ".tmp", "__pycache__", "*.pyc"),
        )
        return target

    def test_complete_pilot_package_passes_technical_contract(self) -> None:
        result = run_checker(ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PILOT_CONTRACT_PASS gates=7 findings=0 fixture_findings=1", result.stdout)

    def test_public_alpha_approval_is_separate_from_open_pilot_gates(self) -> None:
        payload = json.loads((ROOT / "pilot/gate-status.json").read_text(encoding="utf-8"))
        gates = {gate["id"]: gate for gate in payload["gates"]}
        self.assertEqual(payload["decision"], "NO-GO")
        self.assertTrue(payload["generated_from_real_human_evidence"])
        approved = {"strategic-priority", "public-freebie-push-release"}
        blocked = HUMAN_GATES - approved
        self.assertEqual({gate_id for gate_id in HUMAN_GATES if gates[gate_id]["status"] == "blocked"}, blocked)
        for gate_id in blocked:
            self.assertEqual(gates[gate_id]["evidence"], [])
            self.assertTrue(gates[gate_id]["reason"])
        for gate_id in approved:
            self.assertEqual(gates[gate_id]["status"], "passed")
            self.assertTrue(gates[gate_id]["evidence"])

    def test_missing_fairness_term_stops_with_invitation_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="clief-pilot-contract-") as directory:
            copy = self.copied_repo(directory)
            path = copy / "pilot/01-testeinladung.md"
            path.write_text(path.read_text(encoding="utf-8").replace("unbezahlt", "ohne Angabe"), encoding="utf-8")
            result = run_checker(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("pilot/01-testeinladung.md", result.stderr)

    def test_green_gate_without_evidence_stops_with_state_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="clief-pilot-gate-") as directory:
            copy = self.copied_repo(directory)
            path = copy / "pilot/gate-status.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["gates"][0]["evidence"] = []
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            result = run_checker(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("pilot/gate-status.json", result.stderr)
            self.assertIn("grünes Gate ohne Evidenz", result.stderr)

    def test_forced_go_with_blocked_gates_stops(self) -> None:
        with tempfile.TemporaryDirectory(prefix="clief-pilot-go-") as directory:
            copy = self.copied_repo(directory)
            path = copy / "pilot/gate-status.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["decision"] = "GO"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            result = run_checker(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("GO ohne vollständige reale Evidenz", result.stderr)

    def test_incomplete_release_blocker_finding_stops(self) -> None:
        with tempfile.TemporaryDirectory(prefix="clief-pilot-finding-") as directory:
            copy = self.copied_repo(directory)
            path = copy / "pilot/examples/synthetic-befundregister.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            del payload["findings"][0]["reproduction_steps"]
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            result = run_checker(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("pilot/examples/synthetic-befundregister.json", result.stderr)
            self.assertIn("Reproduktionsschritt", result.stderr)

    def test_mislabeled_protected_finding_stops(self) -> None:
        with tempfile.TemporaryDirectory(prefix="clief-pilot-protected-") as directory:
            copy = self.copied_repo(directory)
            path = copy / "pilot/examples/synthetic-befundregister.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["findings"][0]["summary"] = "Kontakt: real.person@firma.example"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            result = run_checker(copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("pilot/examples/synthetic-befundregister.json", result.stderr)
            self.assertIn("geschütztes oder reales Merkmal", result.stderr)

    def test_public_evidence_protected_mutations_stop_with_path(self) -> None:
        mutations = {
            "name": "\nTestperson: Erika Musterfrau\n",
            "contact": "\nKontakt: person@example.invalid\n",
            "phone": "\nKontakt: +49 170 12345678\n",
            "path": "\n/" + "Users/beispiel/private/datei.md\n",
            "secret": "\ns" + "k-" + ("z" * 30) + "\n",
            "private": "contains_private_business_content: true",
            "environment": "\nDarwin 25.6 lokale Umgebung\n",
            "claim": "\nDSGVO-" + "konform\n",
        }
        for name, mutation in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory(prefix="clief-public-evidence-") as directory:
                copy = self.copied_repo(directory)
                path = copy / "pilot/oeffentliche-evidenz.md"
                text = path.read_text(encoding="utf-8")
                if name == "private":
                    text = text.replace("contains_private_business_content: false", mutation)
                else:
                    text += mutation
                path.write_text(text, encoding="utf-8")
                result = run_checker(copy, "public-evidence", str(path))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("pilot/oeffentliche-evidenz.md", result.stderr)

    def test_release_blocker_retest_requires_full_independent_restart(self) -> None:
        text = (ROOT / "pilot/07-retest-protokoll.md").read_text(encoding="utf-8")
        self.assertIn("unbeteiligte Testperson", text)
        self.assertIn("frischer Clone des neuen SHA", text)
        self.assertIn("gesamter betroffener Testauftrag", text)
        self.assertIn("Teil-Retest", text)
        self.assertIn("schließt den Release-Blocker nicht", text)


if __name__ == "__main__":
    unittest.main()
