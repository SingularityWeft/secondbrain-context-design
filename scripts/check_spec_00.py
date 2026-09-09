#!/usr/bin/env python3
"""Fail-closed policy and repository checks for SPEC-00."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "_core" / "policy.json"
INVENTORY_PATH = ROOT / "_core" / "license-inventory.json"
REQUIRED_PATHS = (
    "README.md",
    "START-HIER.md",
    "LICENSE",
    "NOTICE.md",
    "SECURITY.md",
    "RUN-STATE.md",
    "_core/data-policy.md",
    "_core/human-gates.md",
    "_core/policy.json",
    "_core/license-inventory.json",
    "_evidence/SPEC-00.md",
    "_evidence/PUBLICATION-APPROVAL-2026-09-09.md",
)
PUBLIC_CLAIM_PATHS = ("README.md", "START-HIER.md")
TEXT_SUFFIXES = {"", ".md", ".json", ".py", ".sh", ".txt", ".yml", ".yaml"}


class CheckError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CheckError(f"Ungültige JSON-Datei {path.relative_to(ROOT)}: {exc}") from exc


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
    return sorted(files)


def check_required_paths() -> None:
    missing = [item for item in REQUIRED_PATHS if not (ROOT / item).is_file()]
    if missing:
        raise CheckError("Fehlende Pflichtpfade: " + ", ".join(missing))


def check_markdown_links() -> int:
    link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    checked = 0
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        for raw_target in link_pattern.findall(path.read_text(encoding="utf-8")):
            target = raw_target.strip().split()[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            relative = unquote(target.split("#", 1)[0])
            resolved = (path.parent / relative).resolve()
            if not resolved.is_relative_to(ROOT.resolve()):
                raise CheckError(f"Link verlässt das Repository: {path.relative_to(ROOT)} -> {target}")
            if not resolved.exists():
                raise CheckError(f"Gebrochener Link: {path.relative_to(ROOT)} -> {target}")
            checked += 1
    return checked


def check_repository_hygiene() -> int:
    home_pattern = re.compile(r"(?:/" + r"Users/|/home/[A-Za-z0-9._-]+/|[A-Za-z]:\\Users\\)")
    placeholder_patterns = (
        re.compile(r"\{\{" + r"[^}]+\}\}"),
        re.compile(r"\bT" + r"ODO\b", re.IGNORECASE),
        re.compile(r"\bT" + r"BD\b", re.IGNORECASE),
        re.compile(r"\bF" + r"IXME\b", re.IGNORECASE),
        re.compile(r"REPLACE_" + r"MARKER", re.IGNORECASE),
    )
    secret_patterns = (
        re.compile(r"s" + r"k-[A-Za-z0-9_-]{20,}"),
        re.compile(r"A" + r"KIA[0-9A-Z]{16}"),
        re.compile(r"g" + r"hp_[A-Za-z0-9]{30,}"),
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    )
    scanned = 0
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        if home_pattern.search(text):
            raise CheckError(f"Absoluter Nutzerpfad erkannt: {relative}")
        if any(pattern.search(text) for pattern in placeholder_patterns):
            raise CheckError(f"Platzhalter erkannt: {relative}")
        if any(pattern.search(text) for pattern in secret_patterns):
            raise CheckError(f"Typisches Secret erkannt: {relative}")
        scanned += 1
    return scanned


def check_policy_contract() -> dict:
    policy = load_json(POLICY_PATH)
    project = policy.get("project_name", {})
    if project.get("status") != "public-alpha" or project.get("public_release") != "approved-alpha":
        raise CheckError("Öffentlicher Alpha-Status ist nicht korrekt freigegeben")
    if policy.get("starter_mode") != "synthetic-only":
        raise CheckError("Starter-Modus muss synthetic-only sein")
    classes = {item.get("id"): item.get("starter_allowed") for item in policy.get("data_classes", [])}
    if classes != {"S0": True, "S1": False, "S2": False, "S3": False}:
        raise CheckError("Datenklassen weichen vom Alpha-Vertrag ab")
    if not policy.get("human_gate_actions") or not policy.get("allowed_actions"):
        raise CheckError("Human-Gate- oder Allowlist-Aktionen fehlen")
    if not policy.get("forbidden_public_claims"):
        raise CheckError("Claim-Policy fehlt")
    return policy


def forbidden_claims(text: str, policy: dict) -> list[str]:
    return [
        item["id"]
        for item in policy["forbidden_public_claims"]
        if re.search(item["pattern"], text, flags=re.IGNORECASE)
    ]


def check_public_claims(policy: dict) -> None:
    for relative in PUBLIC_CLAIM_PATHS:
        matches = forbidden_claims((ROOT / relative).read_text(encoding="utf-8"), policy)
        if matches:
            raise CheckError(f"Verbotener öffentlicher Claim in {relative}: {', '.join(matches)}")


def check_license_inventory() -> int:
    inventory = load_json(INVENTORY_PATH)
    required = {
        "id",
        "source_url",
        "source_commit",
        "license",
        "copyright_notice",
        "usage",
        "bundled_paths",
        "notice_file",
    }
    entries = inventory.get("entries", [])
    if not entries:
        raise CheckError("Lizenzinventar ist leer")
    for entry in entries:
        missing = sorted(required - set(entry))
        if missing:
            raise CheckError(f"Lizenzinventar {entry.get('id', 'unbekannt')} unvollständig: {', '.join(missing)}")
        if not re.fullmatch(r"[0-9a-f]{40}", entry["source_commit"]):
            raise CheckError(f"Quellcommit ist nicht unveränderlich: {entry['id']}")
        if not (ROOT / entry["notice_file"]).is_file():
            raise CheckError(f"Notice fehlt für {entry['id']}")
        for bundled in entry["bundled_paths"]:
            if not (ROOT / bundled).exists():
                raise CheckError(f"Inventarisierter Fremdpfad fehlt: {bundled}")

    registered = {item for entry in entries for item in entry["bundled_paths"]}
    unregistered: list[str] = []
    for root_name in inventory.get("foreign_roots", []):
        foreign_root = ROOT / root_name
        if foreign_root.exists():
            for path in foreign_root.rglob("*"):
                if path.is_file() and str(path.relative_to(ROOT)) not in registered:
                    unregistered.append(str(path.relative_to(ROOT)))
    if unregistered:
        raise CheckError("Nicht inventarisierte Fremdpfade: " + ", ".join(sorted(unregistered)))
    return len(entries)


def check_input(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if not re.search(r"(?m)^data_class:\s*synthetic\s*$", text):
        raise CheckError("STOP_DATA_POLICY: Datenklasse fehlt oder ist nicht synthetic")
    if not re.search(r"(?m)^synthetic:\s*true\s*$", text):
        raise CheckError("STOP_DATA_POLICY: synthetische Herkunft ist nicht bestätigt")
    sensitive_patterns = (
        re.compile(r"\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30}\b"),
        re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
        re.compile(r"(?:passwort|password|api[_ -]?key|zugangsdaten)\s*[:=]", re.IGNORECASE),
        re.compile(r"(?:kundennummer|personalnummer|steuer-id)\s*[:=]", re.IGNORECASE),
    )
    if any(pattern.search(text) for pattern in sensitive_patterns):
        raise CheckError("STOP_DATA_POLICY: geschütztes oder reales Merkmal erkannt")


def run_repo_check() -> None:
    check_required_paths()
    policy = check_policy_contract()
    check_public_claims(policy)
    links = check_markdown_links()
    files = check_repository_hygiene()
    licenses = check_license_inventory()
    print(f"REPO_POLICY_PASS links={links} files={files} licenses={licenses}")


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("repo")
    claim_parser = subparsers.add_parser("claim")
    claim_parser.add_argument("text")
    action_parser = subparsers.add_parser("action")
    action_parser.add_argument("name")
    input_parser = subparsers.add_parser("input")
    input_parser.add_argument("path", type=Path)
    args = parser.parse_args()

    try:
        policy = check_policy_contract()
        if args.command == "repo":
            run_repo_check()
        elif args.command == "claim":
            matches = forbidden_claims(args.text, policy)
            if matches:
                raise CheckError("CLAIM_BLOCKED: " + ", ".join(matches))
            print("CLAIM_ALLOWED")
        elif args.command == "action":
            if args.name in policy["human_gate_actions"]:
                raise CheckError("HUMAN_GATE_REQUIRED: " + args.name)
            if args.name not in policy["allowed_actions"]:
                raise CheckError("UNKNOWN_ACTION_STOP: " + args.name)
            print("ACTION_ALLOWED: " + args.name)
        elif args.command == "input":
            check_input(args.path)
            print("SAFE_SYNTHETIC_INPUT")
    except (CheckError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
