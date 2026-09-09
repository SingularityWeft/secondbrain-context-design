#!/usr/bin/env python3
"""Prepare and finalize the synthetic Evidence-to-Artifact workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_EVIDENCE = {"supported", "insufficient", "contradicted", "unverified"}
ALLOWED_DECISIONS = {"accept", "change", "reject"}
PROTECTED_PATTERNS = (
    re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30}\b"),
    re.compile(r"(?:passwort|password|api[_ -]?key|zugangsdaten)\s*[:=]", re.IGNORECASE),
    re.compile(r"(?:kundennummer|personalnummer|steuer-id)\s*[:=]", re.IGNORECASE),
)


class WorkflowStop(RuntimeError):
    def __init__(self, reason: str, message: str, exit_code: int = 2) -> None:
        super().__init__(message)
        self.reason = reason
        self.exit_code = exit_code


def digest_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def require_text(value: object, field: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise WorkflowStop("INVALID_INPUT", f"Textfeld fehlt: {field}")
    text = value.strip()
    if not text and not allow_empty:
        raise WorkflowStop("INVALID_INPUT", f"Textfeld ist leer: {field}")
    if "\n" in text or "\r" in text or len(text) > 1200:
        raise WorkflowStop("INVALID_INPUT", f"Textfeld ist nicht atomar: {field}")
    return text


def require_list(value: object, field: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise WorkflowStop("INVALID_INPUT", f"Liste fehlt oder ist leer: {field}")
    return [require_text(item, field) for item in value]


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkflowStop("INVALID_INPUT", f"JSON nicht lesbar: {path.name}") from exc
    if not isinstance(value, dict):
        raise WorkflowStop("INVALID_INPUT", f"JSON muss ein Objekt sein: {path.name}")
    return value


def validate_synthetic(value: dict) -> None:
    if value.get("data_class") != "synthetic" or value.get("synthetic") is not True:
        raise WorkflowStop("STOP_DATA_POLICY", "Nur explizit synthetische Daten sind erlaubt")


def reject_protected_text(text: str, context: str) -> None:
    if any(pattern.search(text) for pattern in PROTECTED_PATTERNS):
        raise WorkflowStop("STOP_DATA_POLICY", f"Geschütztes oder reales Merkmal erkannt: {context}")


def validate_case(case_path: Path) -> tuple[dict, dict[str, dict]]:
    case = load_json(case_path)
    validate_synthetic(case)
    reject_protected_text(json.dumps(case, ensure_ascii=False), "Case-Manifest")
    for field in ("schema_version", "workflow_version", "case_id", "run_id", "started_at"):
        require_text(case.get(field), field)
    briefing = case.get("briefing")
    if not isinstance(briefing, dict):
        raise WorkflowStop("INVALID_INPUT", "Briefing fehlt")
    for field in ("audience", "decision_or_benefit", "scope"):
        require_text(briefing.get(field), f"briefing.{field}")
    require_list(briefing.get("open_questions"), "briefing.open_questions")
    require_list(case.get("outline_sections"), "outline_sections")
    require_list(case.get("reusable"), "reusable")
    require_text(case.get("next_decision"), "next_decision")

    case_root = case_path.resolve().parent
    sources: dict[str, dict] = {}
    for source in case.get("sources", []):
        if not isinstance(source, dict):
            raise WorkflowStop("INVALID_INPUT", "Quelleneintrag ist ungültig")
        source_id = require_text(source.get("id"), "sources.id")
        source_path = (case_root / require_text(source.get("file"), "sources.file")).resolve()
        if not source_path.is_relative_to(case_root) or not source_path.is_file():
            raise WorkflowStop("INVALID_INPUT", f"Quelle fehlt oder verlässt den Case: {source_id}")
        source_text = source_path.read_text(encoding="utf-8")
        reject_protected_text(source_text, f"Quelle {source_id}")
        sources[source_id] = {
            "id": source_id,
            "file": str(source_path.relative_to(case_root)),
            "version": require_text(source.get("version"), "sources.version"),
            "as_of": require_text(source.get("as_of"), "sources.as_of"),
            "sha256": digest_file(source_path),
            "line_count": len(source_text.splitlines()),
        }
    if not sources:
        raise WorkflowStop("INVALID_INPUT", "Mindestens eine synthetische Quelle ist erforderlich")

    claims = case.get("claims")
    if not isinstance(claims, list) or not claims:
        raise WorkflowStop("INVALID_INPUT", "Claim-Liste fehlt")
    seen: set[str] = set()
    for claim in claims:
        if not isinstance(claim, dict):
            raise WorkflowStop("INVALID_INPUT", "Claim ist ungültig")
        claim_id = require_text(claim.get("id"), "claims.id")
        if claim_id in seen:
            raise WorkflowStop("INVALID_INPUT", f"Doppelte Claim-ID: {claim_id}")
        seen.add(claim_id)
        claim_type = require_text(claim.get("type"), "claims.type")
        if claim_type not in {"fact", "assumption"}:
            raise WorkflowStop("INVALID_INPUT", f"Unbekannter Claim-Typ: {claim_id}")
        require_text(claim.get("statement"), "claims.statement")
        require_text(claim.get("as_of"), "claims.as_of")
        evidence = require_text(claim.get("evidence_status"), "claims.evidence_status")
        if evidence not in ALLOWED_EVIDENCE:
            raise WorkflowStop("INVALID_INPUT", f"Unbekannter Evidenzstatus: {claim_id}")
        if not isinstance(claim.get("critical"), bool):
            raise WorkflowStop("INVALID_INPUT", f"Kritikalität fehlt: {claim_id}")
        require_text(claim.get("contradiction_group"), "claims.contradiction_group", allow_empty=True)
        if claim_type == "fact":
            source_id = require_text(claim.get("source_id"), "claims.source_id")
            if source_id not in sources:
                raise WorkflowStop("INVALID_INPUT", f"Faktenclaim ohne bekannte Quelle: {claim_id}")
            locator = require_text(claim.get("locator"), "claims.locator")
            match = re.fullmatch(r"L(\d+)-L(\d+)", locator)
            if not match or int(match.group(1)) < 1 or int(match.group(2)) > sources[source_id]["line_count"]:
                raise WorkflowStop("INVALID_INPUT", f"Ungültige Fundstelle: {claim_id}")
    return case, sources


def markdown_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def cell(value: object) -> str:
    return str(value).replace("|", "\\|") or "—"


def gate_claim_ids(case: dict) -> list[str]:
    return sorted(
        claim["id"]
        for claim in case["claims"]
        if claim["critical"] or claim.get("contradiction_group")
    )


def render_briefing(case: dict) -> str:
    briefing = case["briefing"]
    return (
        "# Stufe 1 – Briefing\n\n"
        f"- Zielgruppe: {briefing['audience']}\n"
        f"- Entscheidung/Nutzen: {briefing['decision_or_benefit']}\n"
        f"- Scope: {briefing['scope']}\n"
        "- Datenklasse: `S0 synthetic`\n\n"
        f"## Offene Fragen\n\n{markdown_list(briefing['open_questions'])}\n"
    )


def render_ledger(case: dict, sources: dict[str, dict]) -> str:
    facts = [claim for claim in case["claims"] if claim["type"] == "fact"]
    assumptions = [claim for claim in case["claims"] if claim["type"] == "assumption"]
    fact_rows = "\n".join(
        f"| `{cell(claim['id'])}` | {cell(claim['statement'])} | `{cell(claim['source_id'])}` "
        f"v{cell(sources[claim['source_id']]['version'])} | `{cell(claim['locator'])}` | {cell(claim['as_of'])} | "
        f"`{cell(claim['evidence_status'])}` | {cell(claim['contradiction_group'])} | {'ja' if claim['critical'] else 'nein'} |"
        for claim in facts
    )
    assumption_rows = "\n".join(
        f"| `{cell(claim['id'])}` | {cell(claim['statement'])} | {cell(claim['as_of'])} | "
        f"`{cell(claim['evidence_status'])}` | {'ja' if claim['critical'] else 'nein'} |"
        for claim in assumptions
    )
    contradictions = sorted({claim["contradiction_group"] for claim in facts if claim["contradiction_group"]})
    return (
        "# Stufe 2 – Evidence/Claim Ledger\n\n"
        "## Faktenclaims\n\n"
        "| ID | Claim | Quelle/Version | Fundstelle | Stand | Evidenz | Widerspruch | kritisch |\n"
        "|---|---|---|---|---|---|---|---|\n"
        f"{fact_rows}\n\n"
        "## Annahmen\n\n"
        "| ID | Annahme | Stand | Evidenz | kritisch |\n"
        "|---|---|---|---|---|\n"
        f"{assumption_rows}\n\n"
        "## Sichtbare Widersprüche und Lücken\n\n"
        + markdown_list([f"Widerspruchsgruppe `{item}` ist ungelöst." for item in contradictions])
        + "\n"
        + markdown_list(
            [
                f"Claim `{claim['id']}` bleibt `{claim['evidence_status']}`."
                for claim in case["claims"]
                if claim["evidence_status"] in {"insufficient", "unverified"}
            ]
        )
        + "\n"
    )


def render_structure(case: dict) -> str:
    sections = "\n".join(f"{index}. {title}" for index, title in enumerate(case["outline_sections"], 1))
    contradictions = sorted({claim["contradiction_group"] for claim in case["claims"] if claim["contradiction_group"]})
    gaps = [claim for claim in case["claims"] if claim["evidence_status"] in {"insufficient", "unverified"}]
    return (
        "# Stufe 3 – Strukturentwurf\n\n"
        "Status: `draft-awaiting-human-review`\n\n"
        f"## Workshop-Outline\n\n{sections}\n\n"
        "## Nicht geglättete Evidenzgrenzen\n\n"
        + markdown_list([f"Widerspruch `{item}` bleibt offen." for item in contradictions])
        + "\n"
        + markdown_list([f"`{claim['id']}` bleibt {claim['evidence_status']}." for claim in gaps])
        + "\n\n## Arbeitsnotiz\n\n"
        "Dieser Entwurf darf vor Stufe 4 menschlich geändert werden. Änderungen werden per Hash nachvollzogen.\n"
    )


def render_review(case: dict) -> str:
    rows = "\n".join(
        f"| `{claim['id']}` | {cell(claim['statement'])} | `{claim['evidence_status']}` | "
        f"{cell(claim['contradiction_group'])} | accept / change / reject |"
        for claim in case["claims"]
        if claim["id"] in gate_claim_ids(case)
    )
    return (
        "# Stufe 4 – Human Review\n\n"
        "Status: `awaiting-human-review`\n\n"
        "| Claim | Aussage | Evidenz | Widerspruch | erforderliche Entscheidung |\n"
        "|---|---|---|---|---|\n"
        f"{rows}\n\n"
        "Zusätzlich ist `final_artifact_decision: accept` oder `reject` erforderlich. "
        "Ohne vollständige Akte entsteht kein Stufe-5-Arbeitsstand.\n"
    )


def safe_write(path: Path, content: bytes) -> str:
    if path.is_symlink():
        raise WorkflowStop("OUTPUT_CONFLICT", f"Symlink-Output gesperrt: {path.name}", 3)
    if path.exists():
        if path.is_file() and path.read_bytes() == content:
            return "unchanged"
        raise WorkflowStop("OUTPUT_CONFLICT", f"Vorhandenes Artefakt wurde verändert: {path.name}", 3)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise WorkflowStop("OUTPUT_CONFLICT", f"Artefakt entstand parallel: {path.name}", 3) from exc
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    return "created"


def artifact_hashes(run_dir: Path, names: list[str]) -> dict[str, str]:
    return {name: digest_file(run_dir / name) for name in names}


def prepare(case_path: Path, run_dir: Path) -> int:
    case, sources = validate_case(case_path)
    if run_dir.is_symlink():
        raise WorkflowStop("OUTPUT_CONFLICT", "Run-Verzeichnis darf kein Symlink sein", 3)
    run_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    snapshot = {"case": case, "sources": list(sources.values())}
    artifacts = {
        "00-case-snapshot.json": (json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
        "01-briefing.md": render_briefing(case).encode("utf-8"),
        "02-evidence-ledger.md": render_ledger(case, sources).encode("utf-8"),
        "03-structure-draft.md": render_structure(case).encode("utf-8"),
        "04-human-review.md": render_review(case).encode("utf-8"),
    }
    results = {name: safe_write(run_dir / name, content) for name, content in artifacts.items()}
    record = {
        "schema_version": "1.0",
        "case_id": case["case_id"],
        "run_id": case["run_id"],
        "workflow_version": case["workflow_version"],
        "started_at": case["started_at"],
        "status": "awaiting-human-review",
        "data_class": "synthetic",
        "sources": list(sources.values()),
        "artifacts": artifact_hashes(run_dir, list(artifacts)),
        "gate_claim_ids": gate_claim_ids(case),
        "open_questions": case["briefing"]["open_questions"],
        "external_writes": False,
    }
    record_name = "run-record.prepare.json"
    results[record_name] = safe_write(
        run_dir / record_name, (json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    )
    print(json.dumps({"status": "awaiting-human-review", "artifacts": results}, ensure_ascii=False))
    return 0


def validate_decision(decision: dict, case: dict) -> tuple[str, dict]:
    validate_synthetic(decision)
    reject_protected_text(json.dumps(decision, ensure_ascii=False), "Entscheidungsakte")
    evidence_type = require_text(decision.get("evidence_type"), "evidence_type")
    not_human = decision.get("not_human_evidence")
    if evidence_type == "technical-fixture-not-human":
        if not_human is not True:
            raise WorkflowStop("INVALID_GATE", "Technische Fixture muss als not-human-evidence markiert sein", 4)
    elif evidence_type == "human-record":
        if not_human is not False:
            raise WorkflowStop("INVALID_GATE", "Menschliche Akte darf keine technische Fixture sein", 4)
    else:
        raise WorkflowStop("INVALID_GATE", "Unbekannter Evidenztyp", 4)
    require_text(decision.get("actor"), "actor")
    require_text(decision.get("recorded_at"), "recorded_at")
    claim_decisions = decision.get("claim_decisions")
    if not isinstance(claim_decisions, dict):
        raise WorkflowStop("INVALID_GATE", "Claim-Entscheidungen fehlen", 4)
    required = gate_claim_ids(case)
    if sorted(claim_decisions) != required:
        raise WorkflowStop("INVALID_GATE", "Gate-Claims sind nicht vollständig entschieden", 4)
    claims = {claim["id"]: claim for claim in case["claims"]}
    for claim_id, item in claim_decisions.items():
        if not isinstance(item, dict) or item.get("decision") not in ALLOWED_DECISIONS:
            raise WorkflowStop("INVALID_GATE", f"Ungültige Entscheidung: {claim_id}", 4)
        replacement = require_text(item.get("replacement"), "replacement", allow_empty=True)
        if item["decision"] == "change" and not replacement:
            raise WorkflowStop("INVALID_GATE", f"Änderung ohne Ersatztext: {claim_id}", 4)
        if claims[claim_id]["evidence_status"] in {"insufficient", "unverified"} and item["decision"] == "accept":
            raise WorkflowStop("INVALID_GATE", f"Unzureichender kritischer Claim kann nicht unverändert akzeptiert werden: {claim_id}", 4)
    for group in {claim["contradiction_group"] for claim in case["claims"] if claim["contradiction_group"]}:
        members = [claim["id"] for claim in case["claims"] if claim["contradiction_group"] == group]
        kept = [claim_id for claim_id in members if claim_decisions[claim_id]["decision"] in {"accept", "change"}]
        if len(kept) > 1:
            raise WorkflowStop("INVALID_GATE", f"Widerspruch bleibt doppelt akzeptiert: {group}", 4)
    final = decision.get("final_artifact_decision")
    if final not in {"accept", "reject"}:
        raise WorkflowStop("INVALID_GATE", "Finale Artefaktentscheidung fehlt", 4)
    return evidence_type, claim_decisions


def render_dispositions(decisions: dict) -> str:
    return "\n".join(
        f"| `{claim_id}` | `{item['decision']}` | {cell(item.get('replacement', ''))} |"
        for claim_id, item in sorted(decisions.items())
    )


def finalize(run_dir: Path, decision_path: Path) -> int:
    snapshot = load_json(run_dir / "00-case-snapshot.json")
    prepare_record = load_json(run_dir / "run-record.prepare.json")
    case = snapshot.get("case")
    if not isinstance(case, dict):
        raise WorkflowStop("INVALID_RUN", "Case-Snapshot ist ungültig")
    for name, expected in prepare_record.get("artifacts", {}).items():
        if name == "03-structure-draft.md":
            continue
        path = run_dir / name
        if not path.is_file() or digest_file(path) != expected:
            raise WorkflowStop("OUTPUT_CONFLICT", f"Nicht freigegebenes Zwischenartefakt verändert: {name}", 3)
    draft = run_dir / "03-structure-draft.md"
    if not draft.is_file():
        raise WorkflowStop("INVALID_RUN", "Strukturentwurf fehlt")
    reject_protected_text(draft.read_text(encoding="utf-8"), "aktueller Strukturentwurf")
    decision = load_json(decision_path)
    evidence_type, claim_decisions = validate_decision(decision, case)
    original_hash = prepare_record["artifacts"]["03-structure-draft.md"]
    current_hash = digest_file(draft)
    rejected = sorted(claim_id for claim_id, item in claim_decisions.items() if item["decision"] == "reject")
    changed = sorted(claim_id for claim_id, item in claim_decisions.items() if item["decision"] == "change")
    final_decision = decision["final_artifact_decision"]
    results: dict[str, str] = {}

    if final_decision == "accept":
        status = "not-human-approved" if evidence_type == "technical-fixture-not-human" else "human-reviewed-not-released"
        warning = (
            "Eine technische Fixture ist keine menschliche Freigabe."
            if evidence_type == "technical-fixture-not-human"
            else "Dieser Arbeitsstand ist menschlich geprüft, aber nicht zur Veröffentlichung oder Kundenübergabe freigegeben."
        )
        working = (
            "# Stufe 5 – Freigegebener Arbeitsstand\n\n"
            f"Status: `{status}`\n\n"
            f"> {warning} Veröffentlichung und Kundenübergabe bleiben gesperrt.\n\n"
            "## Claim-Entscheidungen\n\n"
            "| Claim | Entscheidung | Ersatztext |\n|---|---|---|\n"
            + render_dispositions(claim_decisions)
            + "\n\n## Aktuell geprüfter Strukturinput\n\n"
            + draft.read_text(encoding="utf-8")
        )
        results["05-working-state.md"] = safe_write(run_dir / "05-working-state.md", working.encode("utf-8"))
        result_status = "technical-fixture-complete-awaiting-real-human" if evidence_type == "technical-fixture-not-human" else "human-reviewed-not-released"
    else:
        result_status = "rejected-no-working-state"

    debrief = (
        "# Stufe 6 – Debrief\n\n"
        f"- Ergebnis: `{result_status}`\n"
        f"- Struktur manuell verändert: {'ja' if original_hash != current_hash else 'nein'}\n\n"
        f"## Verworfene Claims\n\n{markdown_list([f'`{item}`' for item in rejected])}\n\n"
        f"## Geänderte Claims\n\n{markdown_list([f'`{item}`' for item in changed]) if changed else '- keine'}\n\n"
        f"## Offene Fragen\n\n{markdown_list(case['briefing']['open_questions'])}\n\n"
        f"## Wiederverwendbares\n\n{markdown_list(case['reusable'])}\n\n"
        f"## Nächste Entscheidung\n\n- {case['next_decision']}\n"
    )
    results["06-debrief.md"] = safe_write(run_dir / "06-debrief.md", debrief.encode("utf-8"))
    final_names = ["06-debrief.md"] + (["05-working-state.md"] if final_decision == "accept" else [])
    final_record = {
        "schema_version": "1.0",
        "case_id": case["case_id"],
        "run_id": case["run_id"],
        "workflow_version": case["workflow_version"],
        "started_at": case["started_at"],
        "decision_recorded_at": decision["recorded_at"],
        "decision_evidence_type": evidence_type,
        "not_human_evidence": decision["not_human_evidence"],
        "status": result_status,
        "sources": prepare_record["sources"],
        "artifacts": {
            **prepare_record["artifacts"],
            "03-structure-draft.md": current_hash,
            **artifact_hashes(run_dir, final_names),
        },
        "decision_record_sha256": digest_file(decision_path),
        "changes": {
            "structure_original_sha256": original_hash,
            "structure_current_sha256": current_hash,
            "manual_change_detected": original_hash != current_hash,
            "changed_claims": changed,
            "rejected_claims": rejected,
        },
        "result": result_status,
        "open_questions": case["briefing"]["open_questions"],
        "external_writes": False,
    }
    results["run-record.final.json"] = safe_write(
        run_dir / "run-record.final.json",
        (json.dumps(final_record, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
    )
    print(json.dumps({"status": result_status, "artifacts": results}, ensure_ascii=False))
    return 0 if final_decision == "accept" else 4


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--case", required=True, type=Path)
    prepare_parser.add_argument("--run-dir", required=True, type=Path)
    finalize_parser = subparsers.add_parser("finalize")
    finalize_parser.add_argument("--run-dir", required=True, type=Path)
    finalize_parser.add_argument("--decision", required=True, type=Path)
    args = parser.parse_args()
    try:
        run_dir = args.run_dir.expanduser().resolve(strict=False)
        if args.command == "prepare":
            return prepare(args.case.expanduser().resolve(), run_dir)
        return finalize(run_dir, args.decision.expanduser().resolve())
    except WorkflowStop as exc:
        print(json.dumps({"status": "stopped", "reason": exc.reason, "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return exc.exit_code
    except (OSError, KeyError, TypeError, UnicodeError) as exc:
        print(json.dumps({"status": "stopped", "reason": "INVALID_RUN", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
