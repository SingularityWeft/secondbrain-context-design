#!/usr/bin/env python3
"""Run the complete synthetic Clief case in a disposable local workspace."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
SETUP = ROOT / "scripts/setup_workspace.py"
SKILL_RUNNER = ROOT / "scripts/run_skill.py"
WORKFLOW_RUNNER = ROOT / "scripts/run_evidence_workflow.py"
CONTEXT_BUILDER = ROOT / "scripts/build_agent_context.py"
ANSWERS = ROOT / "setup/synthetic-answers.json"
SKILL_FIXTURES = ROOT / "tests/fixtures/skills"
CASE_ROOT = ROOT / "workflows/evidence-to-artifact/fixtures/synthetic-workshop"
ARTIFACT_SEQUENCE = [
    ".clief-instance.json",
    "AGENT-INTERFACE.md",
    "01-ausrichtung/user-context.md",
    "00-eingang/capture-demo.md",
    "02-projekte/prozessklarheit-demo/PROJEKT.md",
    "04-entscheidungen/toolwahl-demo.md",
    "05-reviews/2026-w37-demo.md",
    "05-reviews/agent-context/e2e.md",
    "02-projekte/prozessklarheit-demo/evidence-run/01-briefing.md",
    "02-projekte/prozessklarheit-demo/evidence-run/02-evidence-ledger.md",
    "02-projekte/prozessklarheit-demo/evidence-run/03-structure-draft.md",
    "02-projekte/prozessklarheit-demo/evidence-run/04-human-review.md",
    "02-projekte/prozessklarheit-demo/evidence-run/05-working-state.md",
    "02-projekte/prozessklarheit-demo/evidence-run/06-debrief.md",
    "02-projekte/prozessklarheit-demo/evidence-run/run-record.final.json",
]
SKILLS = [
    "capture-und-routing",
    "projekt-start",
    "entscheidung-dokumentieren",
    "wochenreview",
]


class E2EError(RuntimeError):
    pass


def command(arguments: list[str], *, cwd: Path = ROOT, allowed: set[int] | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(arguments, cwd=cwd, capture_output=True, text=True, check=False)
    accepted = {0} if allowed is None else allowed
    if result.returncode not in accepted:
        detail = result.stderr.strip() or result.stdout.strip()
        raise E2EError(f"Befehl endete mit {result.returncode}: {arguments[0]}: {detail[:400]}")
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def setup(workspace: Path, expected_apply_codes: set[int]) -> dict:
    planned = command(
        [PYTHON, str(SETUP), "plan", "--answers", str(ANSWERS), "--target", str(workspace)]
    )
    token = json.loads(planned.stdout)["confirmation_token"]
    applied = command(
        [
            PYTHON,
            str(SETUP),
            "apply",
            "--answers",
            str(ANSWERS),
            "--target",
            str(workspace),
            "--confirm-token",
            token,
        ],
        allowed=expected_apply_codes,
    )
    return json.loads(applied.stdout)


def run_skills(workspace: Path) -> None:
    for skill in SKILLS:
        result = command(
            [
                PYTHON,
                str(SKILL_RUNNER),
                "--workspace",
                str(workspace),
                "--skill",
                skill,
                "--input",
                str(SKILL_FIXTURES / f"{skill}.json"),
            ]
        )
        payload = json.loads(result.stdout)
        if payload.get("status") != "created":
            raise E2EError(f"Skill erzeugte kein neues Artefakt: {skill}")


def build_agent_context(workspace: Path) -> None:
    result = command(
        [
            PYTHON,
            str(CONTEXT_BUILDER),
            "--workspace",
            str(workspace),
            "--task",
            "Ordne die synthetische Anfrage und nenne genau eine nächste sichere Aktion.",
            "--as-of",
            "2026-09-09T12:00:00+02:00",
            "--include",
            "00-eingang/capture-demo.md",
            "--output",
            "05-reviews/agent-context/e2e.md",
        ]
    )
    payload = json.loads(result.stdout)
    if payload.get("provider_invoked") is not False or payload.get("external_transfer") is not False:
        raise E2EError("Kontext-Bundle verletzte die lokale providerneutrale Grenze")


def run_workflow(workspace: Path) -> None:
    run_dir = workspace / "02-projekte/prozessklarheit-demo/evidence-run"
    command(
        [
            PYTHON,
            str(WORKFLOW_RUNNER),
            "prepare",
            "--case",
            str(CASE_ROOT / "manifest.json"),
            "--run-dir",
            str(run_dir),
        ]
    )
    draft = run_dir / "03-structure-draft.md"
    draft.write_text(
        draft.read_text(encoding="utf-8")
        + "\nTechnische Review-Änderung im E2E-Test; keine menschliche Freigabe.\n",
        encoding="utf-8",
    )
    completed = command(
        [
            PYTHON,
            str(WORKFLOW_RUNNER),
            "finalize",
            "--run-dir",
            str(run_dir),
            "--decision",
            str(CASE_ROOT / "decision-accept-test.json"),
        ]
    )
    payload = json.loads(completed.stdout)
    if payload.get("status") != "technical-fixture-complete-awaiting-real-human":
        raise E2EError("Workflow-Fixture wurde fälschlich als menschlich freigegeben")


def assert_artifacts(workspace: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for name in ARTIFACT_SEQUENCE:
        path = workspace / name
        if not path.is_file():
            raise E2EError(f"Erwartetes Artefakt fehlt: {name}")
        hashes[name] = sha256(path)
    return hashes


def initialize_git(workspace: Path) -> None:
    command(["git", "init", "-b", "main"], cwd=workspace)
    command(["git", "add", "--all"], cwd=workspace)
    command(
        [
            "git",
            "-c",
            "user.name=Clief Technical Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-m",
            "Record synthetic baseline",
        ],
        cwd=workspace,
    )


def verify_rerun(
    workspace: Path, artifact_hashes: dict[str, str]
) -> tuple[dict[str, str], dict[str, str], list[str]]:
    manual = workspace / "01-ausrichtung/business-context.md"
    foreign = workspace / "00-eingang/fremde-synthetische-notiz.md"
    missing = workspace / "03-wissen/README.md"
    manual.write_text(manual.read_text(encoding="utf-8") + "\nManuelle synthetische E2E-Notiz.\n", encoding="utf-8")
    foreign.write_text("# Fremde synthetische Notiz\n\nNicht vom Starter verwaltet.\n", encoding="utf-8")
    missing.unlink()
    preserved_before = {
        "manual": sha256(manual),
        "foreign": sha256(foreign),
        **{f"artifact:{name}": value for name, value in artifact_hashes.items()},
    }
    index_before = command(["git", "diff", "--cached", "--binary"], cwd=workspace).stdout

    applied = setup(workspace, {3})
    if applied.get("conflicts") != ["01-ausrichtung/business-context.md"]:
        raise E2EError("Setup-Zweitlauf meldete nicht exakt die erwartete manuelle Änderung")
    if "03-wissen/README.md" not in applied.get("created", []):
        raise E2EError("Setup-Zweitlauf stellte die fehlende Template-Datei nicht wieder her")

    preserved_after = {
        "manual": sha256(manual),
        "foreign": sha256(foreign),
        **{f"artifact:{name}": sha256(workspace / name) for name in artifact_hashes},
    }
    if preserved_before != preserved_after:
        raise E2EError("Setup-Zweitlauf veränderte manuelle, fremde oder erzeugte Artefakte")
    index_after = command(["git", "diff", "--cached", "--binary"], cwd=workspace).stdout
    if index_before != index_after or index_after:
        raise E2EError("Setup-Zweitlauf veränderte unerwartet den Git-Index")
    status = command(["git", "status", "--short"], cwd=workspace).stdout.splitlines()
    expected = {
        " M 01-ausrichtung/business-context.md",
        "?? 00-eingang/fremde-synthetische-notiz.md",
    }
    if set(status) != expected:
        raise E2EError(f"Unerwarteter Git-Status nach Zweitlauf: {status}")
    return preserved_before, preserved_after, sorted(status)


def run() -> dict:
    if not shutil.which("git"):
        raise E2EError("git ist für den lokalen E2E-Nachweis erforderlich")
    with tempfile.TemporaryDirectory(prefix="clief-e2e-") as directory:
        workspace = Path(directory) / "synthetic-private-workspace"
        first = setup(workspace, {0})
        if first.get("status") != "applied" or first.get("git_commands_executed") is not False:
            raise E2EError("Erstsetup verletzte den Setup-Vertrag")
        run_skills(workspace)
        build_agent_context(workspace)
        run_workflow(workspace)
        hashes = assert_artifacts(workspace)
        initialize_git(workspace)
        before, after, status = verify_rerun(workspace, hashes)
        return {
            "status": "E2E_PASS",
            "data_class": "synthetic",
            "technical_fixture_not_human": True,
            "artifact_sequence": ARTIFACT_SEQUENCE,
            "artifact_sha256": hashes,
            "hash_evidence": {"before_rerun": before, "after_rerun": after},
            "artifact_hashes_preserved": all(after[f"artifact:{name}"] == digest for name, digest in hashes.items()),
            "manual_hash_preserved": before["manual"] == after["manual"],
            "foreign_hash_preserved": before["foreign"] == after["foreign"],
            "git_index_unchanged": True,
            "expected_worktree_status": status,
            "external_writes": False,
        }


def main() -> int:
    try:
        print(json.dumps(run(), indent=2, ensure_ascii=False))
        return 0
    except (E2EError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "E2E_STOP", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
