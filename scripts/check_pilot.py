#!/usr/bin/env python3
"""Validate the technical pilot package without simulating human evidence."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ALLOWED_FINDING_CLASSES = {"release-blocker", "friction", "question"}
REQUIRED_GATE_IDS = {
    "technical-verify",
    "primary-run",
    "independent-beginner-walkthroughs",
    "claude-desktop-isolation",
    "privacy-and-public-claims",
    "strategic-priority",
    "public-freebie-push-release",
}
BLOCKED_HUMAN_GATES = REQUIRED_GATE_IDS - {"technical-verify"}


class PilotError(RuntimeError):
    pass


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def load_json(path: Path, root: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PilotError(f"{rel(path, root)}: ungültiges JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise PilotError(f"{rel(path, root)}: JSON-Objekt erwartet")
    return payload


def require_fragments(path: Path, fragments: list[str], root: Path) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [fragment for fragment in fragments if fragment.lower() not in text.lower()]
    if missing:
        raise PilotError(f"{rel(path, root)}: Pflichtaussage fehlt: {missing[0]}")


def validate_contract_documents(root: Path) -> None:
    pilot = root / "pilot"
    contracts = {
        "01-testeinladung.md": [
            "unbezahlt", "höchstens 60 Minuten", "Konkreter Dank", "unabhängig",
            "ablehnen", "jederzeit abbrechen", "awaiting-real-decision",
            "synthetischen Beispiel", "getrennten privaten lokalen Instanz", "praktischem Nutzen",
            "Wenn das nicht weiterhilft", "bereinigtes Issue oder Pull Request",
        ],
        "02-technischer-testauftrag.md": [
            "keine Werbeaussage", "nicht ungefragt", "mit Hilfe", "kein Push",
            "Phase 1", "Phase 2", "Reale ausgewählte Arbeitsinformationen",
            "öffentliche Rückmeldung",
        ],
        "03-pilotvereinbarung.md": [
            "Getrennte Phasen", "unabhängig davon", "keine Pflicht zu Lob",
            "nicht automatisch", "auf Wunsch lokal archiviert", "Partnerschaft", "Beauftragung",
        ],
        "04-einwilligung-und-datenschutz.md": [
            "unsigned-and-blocked", "einzeln getroffen", "Wörtliche Nutzung",
            "Öffentliche Namens", "Widerruf", "Leere Felder", "privater Praxistest",
            "Agenten beziehungsweise Anbieters", "Öffentliche Rückgabe",
        ],
        "05-laufprotokoll.md": [
            "Repository-SHA", "Startzeit", "Endzeit", "Hilfe nötig", "Artefakte",
            "Blocker", "Frictions", "Fragen", "keine Evidenz", "praktischer Nutzen",
            "Unterstützungsbedarf", "keine privaten Inhalte",
        ],
        "07-retest-protokoll.md": [
            "release-blocker", "neuem vollständigem SHA", "unbeteiligte Testperson",
            "gesamter betroffener Testauftrag", "Teil-Retest", "schließt den Release-Blocker nicht",
        ],
        "08-go-no-go.md": [
            "NO-GO", "zwei getrennte Entscheidungen", "Claude-Desktop-Isolation",
            "Claims und Danksagungen", "strategische Priorität", "Evidenzreferenz",
        ],
    }
    for name, fragments in contracts.items():
        path = pilot / name
        if not path.is_file():
            raise PilotError(f"pilot/{name}: Pflichtdokument fehlt")
        require_fragments(path, fragments, root)


def validate_findings(path: Path, root: Path) -> int:
    payload = load_json(path, root)
    if payload.get("data_class") != "synthetic":
        raise PilotError(f"{rel(path, root)}: nur synthetische Befunde sind im Starter erlaubt")
    if set(payload.get("allowed_classes", [])) != ALLOWED_FINDING_CLASSES:
        raise PilotError(f"{rel(path, root)}: Befundklassen weichen vom Vertrag ab")
    findings = payload.get("findings")
    if not isinstance(findings, list):
        raise PilotError(f"{rel(path, root)}: findings muss eine Liste sein")
    serialized = json.dumps(payload, ensure_ascii=False)
    protected = (
        re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
        re.compile(r"\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30}\b"),
        re.compile(r"(?:passwort|password|api[_ -]?key|zugangsdaten)\s*[:=]", re.IGNORECASE),
        re.compile(r"(?:kundennummer|personalnummer|steuer-id)\s*[:=]", re.IGNORECASE),
    )
    if any(pattern.search(serialized) for pattern in protected):
        raise PilotError(f"{rel(path, root)}: geschütztes oder reales Merkmal in synthetischem Register")
    required = {
        "id", "class", "summary", "reproduction_steps", "evidence",
        "affected_task", "found_on_sha", "status",
    }
    identifiers: set[str] = set()
    for index, finding in enumerate(findings):
        label = f"{rel(path, root)}: findings[{index}]"
        if not isinstance(finding, dict) or not required.issubset(finding):
            raise PilotError(f"{label}: Reproduktionsschritt, Evidenz oder Pflichtfeld fehlt")
        if finding["id"] in identifiers:
            raise PilotError(f"{label}: doppelte Befund-ID")
        identifiers.add(finding["id"])
        if finding["class"] not in ALLOWED_FINDING_CLASSES:
            raise PilotError(f"{label}: unbekannte Befundklasse")
        if not isinstance(finding["reproduction_steps"], list) or not finding["reproduction_steps"]:
            raise PilotError(f"{label}: Reproduktionsschritt fehlt")
        if not isinstance(finding["evidence"], list) or not finding["evidence"]:
            raise PilotError(f"{label}: Evidenz fehlt")
        if not all(isinstance(value, str) and value.strip() for value in finding["reproduction_steps"] + finding["evidence"]):
            raise PilotError(f"{label}: Reproduktionsschritt oder Evidenz ist leer")
        if not re.fullmatch(r"[0-9a-f]{40}", str(finding["found_on_sha"])):
            raise PilotError(f"{label}: vollständiger Fund-SHA fehlt")
    return len(findings)


def validate_public_evidence(path: Path, root: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise PilotError(f"{rel(path, root)}: öffentliche Evidenz ist nicht lesbar") from exc
    required = (
        "data_class: synthetic-aggregate",
        "contains_private_business_content: false",
        "release_status: blocked",
    )
    if any(item not in text for item in required):
        raise PilotError(f"{rel(path, root)}: Anonymisierungs- oder Release-Metadaten fehlen")
    protected = (
        ("Name", re.compile(r"(?:participant|tester|testperson|vollständiger name|full name)[_ :]+[A-ZÄÖÜ][\wÄÖÜäöüß-]+(?:\s+[A-ZÄÖÜ][\wÄÖÜäöüß-]+)+", re.IGNORECASE)),
        ("Kontakt", re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")),
        ("Telefonkontakt", re.compile(r"(?:\+|00)\d{2}[ /-]?(?:\d[ /-]?){7,}")),
        ("persönlicher Pfad", re.compile(r"(?:/" + r"Users/|/home/[A-Za-z0-9._-]+/|[A-Za-z]:\\Users\\)")),
        ("Secret", re.compile(r"s" + r"k-[A-Za-z0-9_-]{20,}")),
        ("Secret", re.compile(r"A" + r"KIA[0-9A-Z]{16}")),
        ("Secret", re.compile(r"g" + r"hp_[A-Za-z0-9]{30,}")),
        ("Secret", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
        ("private Inhalte", re.compile(r"contains_private_business_content:\s*true", re.IGNORECASE)),
        ("unnötiges Umgebungsdetail", re.compile(r"(?:Darwin|Windows|Linux)\s+\d+[.]\d+", re.IGNORECASE)),
    )
    for label, pattern in protected:
        if pattern.search(text):
            raise PilotError(f"{rel(path, root)}: geschützte öffentliche Evidenz erkannt: {label}")
    policy = load_json(root / "_core/policy.json", root)
    matches = [
        item["id"]
        for item in policy.get("forbidden_public_claims", [])
        if re.search(item["pattern"], text, re.IGNORECASE)
    ]
    if matches:
        raise PilotError(f"{rel(path, root)}: verbotener öffentlicher Claim: {', '.join(matches)}")


def validate_gates(path: Path, root: Path) -> dict:
    payload = load_json(path, root)
    gates = payload.get("gates")
    if not isinstance(gates, list):
        raise PilotError(f"{rel(path, root)}: Gate-Liste fehlt")
    by_id: dict[str, dict] = {}
    for gate in gates:
        if not isinstance(gate, dict) or not isinstance(gate.get("id"), str):
            raise PilotError(f"{rel(path, root)}: ungültiger Gate-Eintrag")
        by_id[gate["id"]] = gate
    if set(by_id) != REQUIRED_GATE_IDS or len(gates) != len(REQUIRED_GATE_IDS):
        raise PilotError(f"{rel(path, root)}: Gate-Menge ist unvollständig")
    for gate_id, gate in by_id.items():
        status = gate.get("status")
        evidence = gate.get("evidence")
        if status not in {"passed", "blocked"} or not isinstance(evidence, list):
            raise PilotError(f"{rel(path, root)}: ungültiger Status oder Evidenztyp für {gate_id}")
        if status == "passed":
            if not evidence:
                raise PilotError(f"{rel(path, root)}: grünes Gate ohne Evidenz: {gate_id}")
            for evidence_path in evidence:
                if not isinstance(evidence_path, str) or Path(evidence_path).is_absolute():
                    raise PilotError(f"{rel(path, root)}: Evidenzpfad fehlt für {gate_id}")
                resolved_evidence = (root / evidence_path).resolve(strict=False)
                if not resolved_evidence.is_relative_to(root) or not resolved_evidence.is_file():
                    raise PilotError(f"{rel(path, root)}: Evidenzpfad fehlt für {gate_id}")
        elif not str(gate.get("reason", "")).strip():
            raise PilotError(f"{rel(path, root)}: Blockgrund fehlt für {gate_id}")
    all_passed = all(gate["status"] == "passed" for gate in by_id.values())
    if any(by_id[gate_id]["status"] == "passed" for gate_id in BLOCKED_HUMAN_GATES):
        if payload.get("generated_from_real_human_evidence") is not True:
            raise PilotError(f"{rel(path, root)}: menschliches Gate ohne Kennzeichnung realer Evidenz")
    if payload.get("decision") == "GO" and (not all_passed or payload.get("generated_from_real_human_evidence") is not True):
        raise PilotError(f"{rel(path, root)}: GO ohne vollständige reale Evidenz")
    if payload.get("decision") != ("GO" if all_passed else "NO-GO"):
        raise PilotError(f"{rel(path, root)}: Entscheidung widerspricht Gate-Status")
    return by_id


def validate_package(root: Path) -> dict[str, int]:
    validate_contract_documents(root)
    findings = validate_findings(root / "pilot/befundregister.json", root)
    fixture_findings = validate_findings(root / "pilot/examples/synthetic-befundregister.json", root)
    validate_public_evidence(root / "pilot/oeffentliche-evidenz.md", root)
    gates = validate_gates(root / "pilot/gate-status.json", root)
    return {"gates": len(gates), "findings": findings, "fixture_findings": fixture_findings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    subparsers = parser.add_subparsers(dest="command")
    public_parser = subparsers.add_parser("public-evidence")
    public_parser.add_argument("path", type=Path)
    finding_parser = subparsers.add_parser("findings")
    finding_parser.add_argument("path", type=Path)
    gate_parser = subparsers.add_parser("gates")
    gate_parser.add_argument("path", type=Path)
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    try:
        if args.command == "public-evidence":
            validate_public_evidence(args.path.expanduser().resolve(), root)
            print("PUBLIC_EVIDENCE_PASS")
        elif args.command == "findings":
            count = validate_findings(args.path.expanduser().resolve(), root)
            print(f"FINDINGS_PASS count={count}")
        elif args.command == "gates":
            gates = validate_gates(args.path.expanduser().resolve(), root)
            print(f"GATES_PASS count={len(gates)}")
        else:
            result = validate_package(root)
            print("PILOT_CONTRACT_PASS " + " ".join(f"{key}={value}" for key, value in result.items()))
        return 0
    except (PilotError, OSError, UnicodeError, TypeError) as exc:
        print(f"PILOT_CONTRACT_STOP {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
