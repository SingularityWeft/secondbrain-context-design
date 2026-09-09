from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / "scripts" / "setup_workspace.py"
RUNNER = ROOT / "scripts" / "run_skill.py"
CHECKER = ROOT / "scripts" / "check_skills.py"
ANSWERS = ROOT / "setup" / "synthetic-answers.json"
FIXTURES = ROOT / "tests" / "fixtures" / "skills"
GOLDENS = ROOT / "_evidence" / "skills" / "outputs"
SKILLS = {
    "capture-und-routing": (
        FIXTURES / "capture-und-routing.json",
        "00-eingang/capture-demo.md",
        GOLDENS / "capture-demo.md",
        "source_summary",
    ),
    "projekt-start": (
        FIXTURES / "projekt-start.json",
        "02-projekte/prozessklarheit-demo/PROJEKT.md",
        GOLDENS / "prozessklarheit-demo.md",
        "why",
    ),
    "entscheidung-dokumentieren": (
        FIXTURES / "entscheidung-dokumentieren.json",
        "04-entscheidungen/toolwahl-demo.md",
        GOLDENS / "toolwahl-demo.md",
        "question",
    ),
    "wochenreview": (
        FIXTURES / "wochenreview.json",
        "05-reviews/2026-w37-demo.md",
        GOLDENS / "2026-w37-demo.md",
        "projects",
    ),
}


def run(command: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)


def create_workspace(parent: Path) -> Path:
    target = parent / "private-instance"
    planned = run(
        [sys.executable, str(SETUP), "plan", "--answers", str(ANSWERS), "--target", str(target)]
    )
    if planned.returncode != 0:
        raise AssertionError(planned.stderr)
    token = json.loads(planned.stdout)["confirmation_token"]
    applied = run(
        [
            sys.executable,
            str(SETUP),
            "apply",
            "--answers",
            str(ANSWERS),
            "--target",
            str(target),
            "--confirm-token",
            token,
        ]
    )
    if applied.returncode != 0:
        raise AssertionError(applied.stderr)
    return target


def run_skill(workspace: Path, skill: str, input_path: Path) -> subprocess.CompletedProcess[str]:
    return run(
        [
            sys.executable,
            str(RUNNER),
            "--workspace",
            str(workspace),
            "--skill",
            skill,
            "--input",
            str(input_path),
        ]
    )


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Spec03SkillTests(unittest.TestCase):
    def test_contracts_and_registry(self) -> None:
        result = run([sys.executable, str(CHECKER)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("skills=4", result.stdout)

    def test_four_normal_cases_match_golden_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            for skill, (fixture, relative, golden, _) in SKILLS.items():
                with self.subTest(skill=skill):
                    before = digest(fixture)
                    result = run_skill(workspace, skill, fixture)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(digest(fixture), before)
                    self.assertEqual((workspace / relative).read_bytes(), golden.read_bytes())

    def test_four_empty_cases_stop_without_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = create_workspace(root)
            for skill, (fixture, relative, _, empty_field) in SKILLS.items():
                with self.subTest(skill=skill):
                    payload = json.loads(fixture.read_text(encoding="utf-8"))
                    payload[empty_field] = [] if empty_field == "projects" else ""
                    input_path = root / f"empty-{skill}.json"
                    input_path.write_text(json.dumps(payload), encoding="utf-8")
                    result = run_skill(workspace, skill, input_path)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("EMPTY_INPUT", result.stderr)
                    self.assertFalse((workspace / relative).exists())

    def test_four_protected_data_cases_stop_with_safe_alternative(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = create_workspace(root)
            for skill, (fixture, relative, _, _) in SKILLS.items():
                with self.subTest(skill=skill):
                    payload = json.loads(fixture.read_text(encoding="utf-8"))
                    payload["data_class"] = "confidential"
                    payload["synthetic"] = False
                    input_path = root / f"protected-{skill}.json"
                    input_path.write_text(json.dumps(payload), encoding="utf-8")
                    result = run_skill(workspace, skill, input_path)
                    self.assertNotEqual(result.returncode, 0)
                    error = json.loads(result.stderr)
                    self.assertEqual(error["reason"], "STOP_DATA_POLICY")
                    self.assertIn("vollständig erfundene", error["safe_alternative"])
                    self.assertFalse((workspace / relative).exists())

    def test_four_conflicts_preserve_manual_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = create_workspace(root)
            for skill, (fixture, relative, _, _) in SKILLS.items():
                with self.subTest(skill=skill):
                    created = run_skill(workspace, skill, fixture)
                    self.assertEqual(created.returncode, 0, created.stderr)
                    output = workspace / relative
                    output.write_text(output.read_text(encoding="utf-8") + "\nManuelle synthetische Änderung.\n", encoding="utf-8")
                    before = digest(output)
                    repeated = run_skill(workspace, skill, fixture)
                    self.assertEqual(repeated.returncode, 3)
                    self.assertIn("OUTPUT_CONFLICT", repeated.stderr)
                    self.assertEqual(digest(output), before)

    def test_review_has_at_most_one_action_per_project(self) -> None:
        golden = (GOLDENS / "2026-w37-demo.md").read_text(encoding="utf-8")
        sections = golden.split("### ")[1:]
        self.assertEqual(len(sections), 2)
        for section in sections:
            marker = "Nächste Aktion, maximal eine:\n\n"
            self.assertEqual(section.count(marker), 1)
            action_block = section.split(marker, 1)[1].split("\n\n", 1)[0]
            self.assertEqual(action_block.count("\n- ") + action_block.startswith("- "), 1)

    def test_public_starter_cannot_be_used_as_private_workspace(self) -> None:
        fixture = FIXTURES / "capture-und-routing.json"
        result = run_skill(ROOT, "capture-und-routing", fixture)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("INVALID_WORKSPACE", result.stderr)


if __name__ == "__main__":
    unittest.main()
