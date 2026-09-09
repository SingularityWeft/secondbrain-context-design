#!/usr/bin/env python3
"""Comprehensive fail-closed repository contract for the Clief starter."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from privacy_denylist import load_private_denylist, matching_term


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {"", ".json", ".md", ".py", ".sh", ".txt", ".yaml", ".yml"}
IGNORED_PARTS = {".git", ".tmp", "__pycache__"}
REQUIRED_FILES = {
    ".github/ISSUE_TEMPLATE/praxistest.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/verify.yml",
    "CONTRIBUTING.md",
    "LICENSE",
    "NOTICE.md",
    "README.md",
    "RUN-STATE.md",
    "SECURITY.md",
    "START-HIER.md",
    "_core/data-policy.md",
    "_core/human-gates.md",
    "_core/license-inventory.json",
    "_core/policy.json",
    "_core/runtime-policy.json",
    "_core/workspace-contract.md",
    "_evidence/PUBLICATION-APPROVAL-2026-09-09.md",
    "_evidence/CHANGE-2026-09-09-private-practice-test.md",
    "docs/testing/anfaenger-walkthrough.md",
    "docs/testing/ergebnisformular.md",
    "docs/agent-interoperabilitaet.md",
    "examples/synthetische-beratung/README.md",
    "pilot/01-testeinladung.md",
    "pilot/02-technischer-testauftrag.md",
    "pilot/03-pilotvereinbarung.md",
    "pilot/04-einwilligung-und-datenschutz.md",
    "pilot/05-laufprotokoll.md",
    "pilot/07-retest-protokoll.md",
    "pilot/08-go-no-go.md",
    "pilot/README.md",
    "pilot/befundregister.json",
    "pilot/gate-status.json",
    "pilot/oeffentliche-evidenz.md",
    "scripts/check_pilot.py",
    "scripts/privacy_denylist.py",
    "scripts/check_public_history.py",
    "scripts/build_agent_context.py",
    "scripts/run_e2e.py",
    "scripts/verify-repo.sh",
    "skills/REGISTRY.json",
    "template/AGENT-INTERFACE.md",
    "template/01-ausrichtung/user-context.md",
    "workflows/evidence-to-artifact/rubric.json",
}
REQUIRED_DIRS = {
    "template/00-eingang",
    "template/01-ausrichtung",
    "template/02-projekte",
    "template/03-wissen",
    "template/04-entscheidungen",
    "template/05-reviews",
    "template/99-archiv",
}
PUBLIC_CLAIM_FILES = {
    "CONTRIBUTING.md",
    "README.md",
    "START-HIER.md",
    "docs/setup.md",
    "docs/skills.md",
    "examples/synthetische-beratung/README.md",
}
TEMPLATE_MARKERS = {
    "AUDIENCES",
    "BOUNDARIES",
    "BUSINESS_NAME",
    "CAPACITY_CONSTRAINTS",
    "COMMUNICATION_PREFERENCES",
    "HOW",
    "OFFERS",
    "OWNER_ROLE",
    "PRINCIPLES",
    "SETUP_DATE",
    "SUPPORT_PREFERENCES",
    "TEMPLATE_DIGEST",
    "USER_GOALS",
    "WHAT",
    "WHO",
    "WHY",
    "WORKING_STYLE",
    "WORKSPACE_ID",
}
CHECKOUT_COMMIT = "3d3c42e5aac5ba805825da76410c181273ba90b1"
class RepositoryError(RuntimeError):
    pass


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def iter_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and not any(part in IGNORED_PARTS for part in path.parts)
    )


def iter_text_files(root: Path) -> list[Path]:
    return [path for path in iter_files(root) if path.suffix.lower() in TEXT_SUFFIXES]


def load_json(path: Path, root: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RepositoryError(f"Ungültiges JSON: {relative(path, root)}: {exc}") from exc


def check_structure(root: Path) -> None:
    missing = sorted(item for item in REQUIRED_FILES if not (root / item).is_file())
    missing.extend(sorted(item for item in REQUIRED_DIRS if not (root / item).is_dir()))
    if missing:
        raise RepositoryError("Fehlender Pflichtpfad: " + ", ".join(missing))
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    if len(skills) != 4:
        raise RepositoryError(f"skills/REGISTRY.json: exakt vier Basisskills erwartet, gefunden {len(skills)}")
    stages = sorted((root / "workflows/evidence-to-artifact/stages").glob("*/CONTEXT.md"))
    if len(stages) != 6:
        raise RepositoryError(
            "workflows/evidence-to-artifact/stages: exakt sechs Stufen erwartet"
        )
    if (root / "template/AGENTS.md").read_bytes() != (root / "template/CLAUDE.md").read_bytes():
        raise RepositoryError("template/AGENTS.md: Runtime-Adapter sind semantisch nicht identisch")
    interface = (root / "template/AGENT-INTERFACE.md").read_text(encoding="utf-8")
    if (
        "providerneutrale" not in interface.lower()
        or "kanonische Logik" not in interface
        or "untrusted data" not in interface
    ):
        raise RepositoryError("template/AGENT-INTERFACE.md: providerneutraler kanonischer Vertrag fehlt")


def check_links(root: Path) -> int:
    pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    count = 0
    for path in iter_files(root):
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        for raw in pattern.findall(text):
            target = raw.strip().split()[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            destination = (path.parent / unquote(target.split("#", 1)[0])).resolve(strict=False)
            if not destination.is_relative_to(root.resolve()):
                raise RepositoryError(f"Link verlässt Repository: {relative(path, root)} -> {target}")
            if not destination.exists():
                raise RepositoryError(f"Gebrochener Link: {relative(path, root)} -> {target}")
            count += 1
    return count


def check_hygiene(root: Path, private_terms: tuple[str, ...] = ()) -> int:
    personal_path = re.compile(r"(?:/" + r"Users/|/home/[A-Za-z0-9._-]+/|[A-Za-z]:\\Users\\)")
    placeholders = (
        re.compile(r"\{\{" + r"[^}]+\}\}"),
        re.compile(r"\bT" + r"ODO\b", re.IGNORECASE),
        re.compile(r"\bT" + r"BD\b", re.IGNORECASE),
        re.compile(r"\bF" + r"IXME\b", re.IGNORECASE),
        re.compile(r"REPLACE_" + r"MARKER", re.IGNORECASE),
    )
    secrets = (
        re.compile(r"s" + r"k-[A-Za-z0-9_-]{20,}"),
        re.compile(r"A" + r"KIA[0-9A-Z]{16}"),
        re.compile(r"g" + r"hp_[A-Za-z0-9]{30,}"),
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    )
    marker_pattern = re.compile(r"@" + r"@([A-Z0-9_]+)@" + r"@")
    count = 0
    for path in iter_text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError as exc:
            raise RepositoryError(f"Nicht lesbarer Text: {relative(path, root)}") from exc
        name = relative(path, root)
        if personal_path.search(text):
            raise RepositoryError(f"Persönlicher absoluter Pfad: {name}")
        if any(pattern.search(text) for pattern in placeholders):
            raise RepositoryError(f"Offener Platzhalter: {name}")
        if any(pattern.search(text) for pattern in secrets):
            raise RepositoryError(f"Typisches Secret: {name}")
        if matching_term(text, private_terms):
            raise RepositoryError(f"Eintrag aus privater Denylist erkannt: {name}")
        markers = set(marker_pattern.findall(text))
        if markers:
            if not name.startswith("template/") or not markers.issubset(TEMPLATE_MARKERS):
                raise RepositoryError(f"Unerlaubter Template-Marker: {name}")
        count += 1
    for path in iter_files(root):
        if path.is_symlink():
            raise RepositoryError(f"Symlink im Starter nicht erlaubt: {relative(path, root)}")
        if path.suffix.lower() not in TEXT_SUFFIXES:
            raise RepositoryError(f"Unerwartete Binärdatei: {relative(path, root)}")
    return count


def check_json(root: Path) -> int:
    paths = [path for path in iter_files(root) if path.suffix.lower() == ".json"]
    for path in paths:
        load_json(path, root)
    return len(paths)


def check_policy_and_claims(root: Path) -> int:
    policy_path = root / "_core/policy.json"
    policy = load_json(policy_path, root)
    if not isinstance(policy, dict):
        raise RepositoryError("_core/policy.json: Objekt erwartet")
    project = policy.get("project_name", {})
    if project.get("status") != "public-alpha" or project.get("public_release") != "approved-alpha":
        raise RepositoryError("_core/policy.json: öffentlicher Alpha-Status ist nicht korrekt freigegeben")
    if policy.get("starter_mode") != "synthetic-only":
        raise RepositoryError("_core/policy.json: starter_mode muss synthetic-only sein")
    classes = {item.get("id"): item.get("starter_allowed") for item in policy.get("data_classes", [])}
    if classes != {"S0": True, "S1": False, "S2": False, "S3": False}:
        raise RepositoryError("_core/policy.json: Datenklassen weichen vom Vertrag ab")
    private_classes = {
        item.get("id"): item.get("private_instance_allowed")
        for item in policy.get("data_classes", [])
        if item.get("id") in {"S1", "S2", "S3"}
    }
    if private_classes != {"S1": True, "S2": True, "S3": False}:
        raise RepositoryError("_core/policy.json: Private Datenklassen weichen vom Vertrag ab")
    patterns = policy.get("forbidden_public_claims", [])
    if not patterns:
        raise RepositoryError("_core/policy.json: Claim-Policy fehlt")
    for name in PUBLIC_CLAIM_FILES:
        text = (root / name).read_text(encoding="utf-8")
        matches = [item["id"] for item in patterns if re.search(item["pattern"], text, re.IGNORECASE)]
        if matches:
            raise RepositoryError(f"Verbotener öffentlicher Claim: {name}: {', '.join(matches)}")
    human_actions = set(policy.get("human_gate_actions", []))
    required_actions = {
        "publish",
        "release",
        "push",
        "deploy",
        "activate-connector",
        "share-private-context-with-agent",
        "publish-sanitized-issue-or-pull-request",
    }
    if not required_actions.issubset(human_actions):
        raise RepositoryError("_core/policy.json: Human-Gate-Aktionen fehlen")
    return len(patterns)


def check_private_practice_and_contribution(root: Path) -> int:
    contracts = {
        "README.md": (
            "Zwei Phasen",
            "getrennte private Instanz",
            "echten, überschaubaren Anwendungsfall",
            "öffentliche Issues und Pull Requests",
            "CONTRIBUTING.md",
        ),
        "START-HIER.md": (
            "außerhalb des öffentlichen Clones",
            "weder in Git noch in öffentliche Issues oder Pull Requests",
        ),
        "SECURITY.md": (
            "echter Praxistest",
            "Agentenzugriff",
            "bereinigte Reproduktionen",
        ),
        "CONTRIBUTING.md": (
            "Erst lokal lösen",
            "synthetischen oder vollständig bereinigten Angaben",
            "Fork unter deiner eigenen GitHub-Identität",
            "keine private Praxisevidenz imitieren",
        ),
        "docs/testing/anfaenger-walkthrough.md": (
            "Phase 1",
            "Phase 2",
            "praktischen Nutzen",
            "Unterstützung benötigt",
        ),
        ".github/ISSUE_TEMPLATE/praxistest.yml": (
            "Keine Kundeninformationen",
            "keine Secrets",
            "SECURITY.md",
        ),
        ".github/PULL_REQUEST_TEMPLATE.md": (
            "Base-SHA",
            "bash scripts/verify-repo.sh",
            "Private Instanzdateien wurden nicht",
            "Kein Auto-Merge",
        ),
    }
    for name, fragments in contracts.items():
        text = (root / name).read_text(encoding="utf-8")
        missing = [fragment for fragment in fragments if fragment.lower() not in text.lower()]
        if missing:
            raise RepositoryError(f"{name}: Zwei-Phasen- oder Contribution-Vertrag fehlt: {missing[0]}")
    contribution = (root / "CONTRIBUTING.md").read_text(encoding="utf-8").lower()
    forbidden = ("git push origin", "auto-merge aktivieren", "maintainer-token anfordern")
    if any(item in contribution for item in forbidden):
        raise RepositoryError("CONTRIBUTING.md: unsicherer öffentlicher Beitragsweg")
    return len(contracts)


def check_license(root: Path) -> int:
    license_path = root / "LICENSE"
    notice_path = root / "NOTICE.md"
    inventory_path = root / "_core/license-inventory.json"
    license_text = license_path.read_text(encoding="utf-8")
    if "MIT License" not in license_text or "MoselMinds" not in license_text:
        raise RepositoryError("LICENSE: MIT- oder MoselMinds-Hinweis fehlt")
    inventory = load_json(inventory_path, root)
    if not isinstance(inventory, dict) or not inventory.get("entries"):
        raise RepositoryError("_core/license-inventory.json: Einträge fehlen")
    notice = notice_path.read_text(encoding="utf-8")
    registered: set[str] = set()
    for entry in inventory["entries"]:
        item_id = entry.get("id", "unbekannt")
        required = {
            "id", "source_url", "source_commit", "license", "copyright_notice",
            "usage", "bundled_paths", "notice_file",
        }
        if not required.issubset(entry):
            raise RepositoryError(f"_core/license-inventory.json: Eintrag unvollständig: {item_id}")
        if not re.fullmatch(r"[0-9a-f]{40}", entry["source_commit"]):
            raise RepositoryError(f"_core/license-inventory.json: Quellcommit nicht unveränderlich: {item_id}")
        if entry["license"] != "MIT" or entry["copyright_notice"] not in notice:
            raise RepositoryError(f"NOTICE.md: Lizenzhinweis fehlt für {item_id}")
        if entry["source_commit"] not in notice:
            raise RepositoryError(f"NOTICE.md: Quellcommit fehlt für {item_id}")
        for name in entry["bundled_paths"]:
            registered.add(name)
            if not (root / name).exists():
                raise RepositoryError(f"_core/license-inventory.json: Fremdpfad fehlt: {name}")
    for root_name in inventory.get("foreign_roots", []):
        foreign_root = root / root_name
        if foreign_root.exists():
            for path in foreign_root.rglob("*"):
                if path.is_file() and relative(path, root) not in registered:
                    raise RepositoryError(f"_core/license-inventory.json: Fremdpfad nicht inventarisiert: {relative(path, root)}")
    return len(inventory["entries"])


def check_ci(root: Path) -> None:
    path = root / ".github/workflows/verify.yml"
    text = path.read_text(encoding="utf-8")
    required = (
        "permissions:\n  contents: read",
        "runs-on: ubuntu-24.04",
        f"uses: actions/checkout@{CHECKOUT_COMMIT}",
        "run: bash scripts/verify-repo.sh",
    )
    if any(item not in text for item in required):
        raise RepositoryError(f"{relative(path, root)}: CI-Vertrag ist unvollständig oder nicht gepinnt")
    forbidden = ("secrets" + ".", "curl ", "wget ", "pip install", "npm install", "model-api")
    if any(item.lower() in text.lower() for item in forbidden):
        raise RepositoryError(f"{relative(path, root)}: CI enthält verbotene Abhängigkeit")


def run(root: Path, private_denylist: Path | None = None) -> dict[str, int]:
    resolved = root.expanduser().resolve()
    if not resolved.is_dir():
        raise RepositoryError(f"Repository nicht gefunden: {root}")
    private_terms = load_private_denylist(private_denylist, resolved, RepositoryError)
    check_structure(resolved)
    result = {
        "links": check_links(resolved),
        "text_files": check_hygiene(resolved, private_terms),
        "json_files": check_json(resolved),
        "claim_rules": check_policy_and_claims(resolved),
        "practice_contracts": check_private_practice_and_contribution(resolved),
        "license_entries": check_license(resolved),
    }
    check_ci(resolved)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--private-denylist", type=Path)
    args = parser.parse_args()
    try:
        result = run(args.root, args.private_denylist)
        print("REPOSITORY_CONTRACT_PASS " + " ".join(f"{key}={value}" for key, value in result.items()))
        return 0
    except (RepositoryError, OSError, UnicodeError, TypeError) as exc:
        print(f"REPOSITORY_CONTRACT_STOP {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
