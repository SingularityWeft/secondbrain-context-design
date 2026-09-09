from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_evidence_workflow.py"
WORKFLOW = ROOT / "workflows" / "evidence-to-artifact"
CASE = WORKFLOW / "fixtures" / "synthetic-workshop" / "manifest.json"
ACCEPT = WORKFLOW / "fixtures" / "synthetic-workshop" / "decision-accept-test.json"
REJECT = WORKFLOW / "fixtures" / "synthetic-workshop" / "decision-reject-test.json"


def run_workflow(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RUNNER), *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def prepare(run_dir: Path) -> subprocess.CompletedProcess[str]:
    return run_workflow("prepare", "--case", str(CASE), "--run-dir", str(run_dir))


def finalize(run_dir: Path, decision: Path) -> subprocess.CompletedProcess[str]:
    return run_workflow("finalize", "--run-dir", str(run_dir), "--decision", str(decision))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Spec04WorkflowTests(unittest.TestCase):
    def test_committed_example_chain_is_complete_and_hash_consistent(self) -> None:
        run_dir = ROOT / "_evidence" / "workflow" / "run-001"
        record = json.loads((run_dir / "run-record.final.json").read_text(encoding="utf-8"))
        self.assertEqual(record["case_id"], "nordstern-workshop-demo")
        self.assertEqual(record["status"], "technical-fixture-complete-awaiting-real-human")
        self.assertTrue(record["not_human_evidence"])
        self.assertTrue(record["changes"]["manual_change_detected"])
        self.assertFalse(record["external_writes"])
        for name, expected_hash in record["artifacts"].items():
            self.assertEqual(sha256(run_dir / name), expected_hash, name)
        working = (run_dir / "05-working-state.md").read_text(encoding="utf-8")
        self.assertIn("Technische Review-Änderung, keine menschliche Freigabe", working)
        review = (run_dir / "rubric-review.md").read_text(encoding="utf-8")
        self.assertIn("agent-review-not-human-approval", review)

    def test_stage_contracts_and_rubric_are_complete(self) -> None:
        stages = sorted((WORKFLOW / "stages").glob("*/CONTEXT.md"))
        self.assertEqual(len(stages), 6)
        for stage in stages:
            text = stage.read_text(encoding="utf-8")
            self.assertIn("## Inputs", text)
            self.assertIn("## Process", text)
            self.assertIn("## Outputs", text)
        rubric = json.loads((WORKFLOW / "rubric.json").read_text(encoding="utf-8"))
        self.assertEqual(
            {item["id"] for item in rubric["dimensions"]},
            {"source-quality", "claim-grounding", "relevance", "control"},
        )
        self.assertIn("critical-claim-without-decision", rubric["stop_conditions"])

    def test_happy_technical_path_preserves_manual_structure_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory) / "run"
            prepared = prepare(run_dir)
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            self.assertIn("awaiting-human-review", prepared.stdout)
            draft = run_dir / "03-structure-draft.md"
            original_hash = sha256(draft)
            manual_line = "Menschliche Änderung wäre hier separat zu bestätigen; dies ist nur synthetischer Testtext."
            draft.write_text(draft.read_text(encoding="utf-8") + f"\n{manual_line}\n", encoding="utf-8")

            completed = finalize(run_dir, ACCEPT)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            working = (run_dir / "05-working-state.md").read_text(encoding="utf-8")
            self.assertIn("not-human-approved", working)
            self.assertIn(manual_line, working)
            final_record = json.loads((run_dir / "run-record.final.json").read_text(encoding="utf-8"))
            self.assertTrue(final_record["not_human_evidence"])
            self.assertTrue(final_record["changes"]["manual_change_detected"])
            self.assertEqual(final_record["changes"]["structure_original_sha256"], original_hash)
            self.assertEqual(final_record["changes"]["structure_current_sha256"], sha256(draft))
            self.assertEqual(final_record["artifacts"]["03-structure-draft.md"], sha256(draft))
            self.assertEqual(final_record["decision_record_sha256"], sha256(ACCEPT))
            self.assertFalse(final_record["external_writes"])
            for stage in range(1, 7):
                self.assertTrue(any(run_dir.glob(f"{stage:02d}-*")), stage)

    def test_contradiction_and_insufficient_claim_remain_visible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory) / "run"
            prepared = prepare(run_dir)
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            ledger = (run_dir / "02-evidence-ledger.md").read_text(encoding="utf-8")
            structure = (run_dir / "03-structure-draft.md").read_text(encoding="utf-8")
            review = (run_dir / "04-human-review.md").read_text(encoding="utf-8")
            for claim in ("claim-duration-60", "claim-duration-90", "claim-guarantee"):
                self.assertIn(claim, ledger)
            self.assertIn("workshop-duration", ledger)
            self.assertIn("workshop-duration", structure)
            self.assertIn("claim-guarantee", structure)
            self.assertIn("claim-guarantee", review)
            self.assertIn("insufficient", review)

    def test_incomplete_gate_stops_before_working_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir = root / "run"
            prepared = prepare(run_dir)
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            decision = json.loads(ACCEPT.read_text(encoding="utf-8"))
            decision["claim_decisions"].pop("claim-guarantee")
            incomplete = root / "incomplete-decision.json"
            incomplete.write_text(json.dumps(decision), encoding="utf-8")
            result = finalize(run_dir, incomplete)
            self.assertEqual(result.returncode, 4)
            self.assertIn("INVALID_GATE", result.stderr)
            self.assertFalse((run_dir / "05-working-state.md").exists())
            self.assertFalse((run_dir / "run-record.final.json").exists())

    def test_rejected_gate_creates_debrief_but_no_working_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory) / "run"
            prepared = prepare(run_dir)
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            result = finalize(run_dir, REJECT)
            self.assertEqual(result.returncode, 4)
            self.assertFalse((run_dir / "05-working-state.md").exists())
            debrief = (run_dir / "06-debrief.md").read_text(encoding="utf-8")
            self.assertIn("rejected-no-working-state", debrief)
            self.assertIn("claim-guarantee", debrief)
            record = json.loads((run_dir / "run-record.final.json").read_text(encoding="utf-8"))
            self.assertEqual(record["status"], "rejected-no-working-state")
            self.assertTrue(record["not_human_evidence"])

    def test_prepare_conflict_preserves_manual_intermediate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory) / "run"
            first = prepare(run_dir)
            self.assertEqual(first.returncode, 0, first.stderr)
            ledger = run_dir / "02-evidence-ledger.md"
            ledger.write_text(ledger.read_text(encoding="utf-8") + "\nManuelle synthetische Notiz.\n", encoding="utf-8")
            before = sha256(ledger)
            repeated = prepare(run_dir)
            self.assertEqual(repeated.returncode, 3)
            self.assertIn("OUTPUT_CONFLICT", repeated.stderr)
            self.assertEqual(sha256(ledger), before)

    def test_mislabeled_protected_case_stops_before_run_creation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            copied_case = root / "case"
            shutil.copytree(CASE.parent, copied_case)
            manifest_path = copied_case / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["briefing"]["audience"] = "Kontakt: real.person@firma.example"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            run_dir = root / "run"
            result = run_workflow("prepare", "--case", str(manifest_path), "--run-dir", str(run_dir))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("STOP_DATA_POLICY", result.stderr)
            self.assertFalse(run_dir.exists())

    def test_protected_manual_edit_stops_before_final_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory) / "run"
            prepared = prepare(run_dir)
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            draft = run_dir / "03-structure-draft.md"
            draft.write_text(draft.read_text(encoding="utf-8") + "\nKontakt: real.person@firma.example\n", encoding="utf-8")
            result = finalize(run_dir, ACCEPT)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("STOP_DATA_POLICY", result.stderr)
            self.assertFalse((run_dir / "05-working-state.md").exists())
            self.assertFalse((run_dir / "run-record.final.json").exists())


if __name__ == "__main__":
    unittest.main()
