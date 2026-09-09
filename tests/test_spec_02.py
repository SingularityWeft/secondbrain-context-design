from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / "scripts" / "setup_workspace.py"
ANSWERS = ROOT / "setup" / "synthetic-answers.json"


def run_setup(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SETUP), *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plan_for(target: Path) -> dict:
    result = run_setup("plan", "--answers", str(ANSWERS), "--target", str(target))
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


def apply_for(target: Path, token: str) -> subprocess.CompletedProcess[str]:
    return run_setup(
        "apply",
        "--answers",
        str(ANSWERS),
        "--target",
        str(target),
        "--confirm-token",
        token,
    )


class Spec02SetupTests(unittest.TestCase):
    def test_plan_is_read_only_and_wrong_token_stops(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "private-instance"
            plan = plan_for(target)
            self.assertFalse(target.exists())
            self.assertFalse(plan["write_performed"])
            self.assertGreater(len(plan["planned_paths"]), 10)
            result = apply_for(target, "0" * 64)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(target.exists())

    def test_fresh_setup_routing_placeholders_and_restart(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "private-instance"
            plan = plan_for(target)
            result = apply_for(target, plan["confirmation_token"])
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "applied")
            self.assertFalse(payload["git_commands_executed"])
            self.assertFalse((target / ".git").exists())
            files = sorted(str(path.relative_to(target)) for path in target.rglob("*") if path.is_file())
            self.assertEqual(files, sorted(plan["planned_paths"]))
            for path in target.rglob("*"):
                if path.is_file():
                    self.assertIsNone(re.search(r"@@[A-Z0-9_]+@@", path.read_text(encoding="utf-8")), path)

            routing = (target / "CONTEXT.md").read_text(encoding="utf-8")
            for area in (
                "00-eingang/",
                "01-ausrichtung/",
                "02-projekte/",
                "03-wissen/",
                "04-entscheidungen/",
                "05-reviews/",
                "99-archiv/",
            ):
                self.assertEqual(routing.count(f"`{area}`"), 1, area)

            status = run_setup("status", "--target", str(target))
            self.assertEqual(status.returncode, 0, status.stderr)
            restart = json.loads(status.stdout)
            self.assertTrue(restart["last_completed"])
            self.assertEqual(len(restart["blockers"]), 3)
            self.assertIsInstance(restart["next_safe_action"], str)

    def test_rerun_preserves_manual_foreign_and_index_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "private-instance"
            plan = plan_for(target)
            first = apply_for(target, plan["confirmation_token"])
            self.assertEqual(first.returncode, 0, first.stderr)

            subprocess.run(["git", "init", "-b", "main"], cwd=target, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Synthetic Test"], cwd=target, check=True)
            subprocess.run(["git", "config", "user.email", "synthetic@example.invalid"], cwd=target, check=True)
            subprocess.run(["git", "add", "--", *plan["planned_paths"]], cwd=target, check=True)
            subprocess.run(["git", "commit", "-m", "Synthetic baseline"], cwd=target, check=True, capture_output=True)

            manual = target / "01-ausrichtung" / "business-context.md"
            manual.write_text(manual.read_text(encoding="utf-8") + "\nManuelle synthetische Ergänzung.\n", encoding="utf-8")
            foreign = target / "fremde-notiz.md"
            foreign.write_text("Unabhängige synthetische Notiz.\n", encoding="utf-8")
            missing = target / "03-wissen" / "README.md"
            missing.unlink()
            manual_before = sha256(manual)
            foreign_before = sha256(foreign)
            index_before = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=target,
                check=True,
                capture_output=True,
                text=True,
            ).stdout

            rerun = apply_for(target, plan["confirmation_token"])
            self.assertEqual(rerun.returncode, 3, rerun.stderr)
            payload = json.loads(rerun.stdout)
            self.assertIn("01-ausrichtung/business-context.md", payload["conflicts"])
            self.assertIn("03-wissen/README.md", payload["created"])
            self.assertEqual(sha256(manual), manual_before)
            self.assertEqual(sha256(foreign), foreign_before)
            self.assertTrue(missing.is_file())
            index_after = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=target,
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertEqual(index_after, index_before)
            status = subprocess.run(
                ["git", "status", "--short"], cwd=target, check=True, capture_output=True, text=True
            ).stdout
            self.assertIn("business-context.md", status)
            self.assertIn("fremde-notiz.md", status)

    def test_broad_and_starter_internal_targets_stop(self) -> None:
        for target in (str(Path.home()), str(ROOT / "private-instance"), str(ROOT.parent)):
            with self.subTest(target=target):
                result = run_setup("plan", "--answers", str(ANSWERS), "--target", target)
                self.assertNotEqual(result.returncode, 0)

    def test_manipulated_marker_stops_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "private-instance"
            target.mkdir(mode=0o700)
            marker = target / ".clief-instance.json"
            marker.write_text('{"schema_version":"1.0","workspace_id":"fremd"}\n', encoding="utf-8")
            plan = plan_for(target)
            result = apply_for(target, plan["confirmation_token"])
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(sorted(path.name for path in target.iterdir()), [marker.name])

    def test_existing_target_with_broad_permissions_stops(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "private-instance"
            target.mkdir(mode=0o755)
            target.chmod(0o755)
            plan = plan_for(target)
            result = apply_for(target, plan["confirmation_token"])
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(target.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
