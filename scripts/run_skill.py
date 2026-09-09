#!/usr/bin/env python3
"""Deterministic reference runner for the four synthetic-only base skills."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "skills" / "REGISTRY.json"
SAFE_ALTERNATIVE = (
    "Verwende eine vollständig erfundene, als synthetic markierte Kopie "
    "in einer getrennten Testinstanz."
)
ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{2,64}")
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")
ROUTES = {
    "00-eingang",
    "01-ausrichtung",
    "02-projekte",
    "03-wissen",
    "04-entscheidungen",
    "05-reviews",
    "99-archiv",
}


class SkillStop(RuntimeError):
    def __init__(self, reason: str, message: str, exit_code: int = 2) -> None:
        super().__init__(message)
        self.reason = reason
        self.exit_code = exit_code


def require_text(value: object, field: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise SkillStop("EMPTY_INPUT", f"Pflichttext fehlt: {field}")
    text = value.strip()
    if not text and not allow_empty:
        raise SkillStop("EMPTY_INPUT", f"Pflichttext ist leer: {field}")
    if "\n" in text or "\r" in text or len(text) > 800:
        raise SkillStop("INVALID_INPUT", f"Pflichttext ist nicht atomar: {field}")
    return text


def require_list(value: object, field: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise SkillStop("EMPTY_INPUT", f"Pflichtliste fehlt oder ist leer: {field}")
    return [require_text(item, field) for item in value]


def validate_common(payload: dict) -> None:
    if payload.get("data_class") != "synthetic" or payload.get("synthetic") is not True:
        raise SkillStop("STOP_DATA_POLICY", "Nicht synthetische oder unklare Datenklasse")
    serialized = json.dumps(payload, ensure_ascii=False)
    protected = (
        re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
        re.compile(r"\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30}\b"),
        re.compile(r"(?:passwort|password|api[_ -]?key|zugangsdaten)\s*[:=]", re.IGNORECASE),
        re.compile(r"(?:kundennummer|personalnummer|steuer-id)\s*[:=]", re.IGNORECASE),
    )
    if any(pattern.search(serialized) for pattern in protected):
        raise SkillStop("STOP_DATA_POLICY", "Geschütztes oder reales Merkmal erkannt")
    identifier = require_text(payload.get("id"), "id")
    if not ID_PATTERN.fullmatch(identifier):
        raise SkillStop("INVALID_INPUT", "ID muss ein sicherer Kleinbuchstaben-Slug sein")


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def frontmatter(skill: str, date: str) -> str:
    return (
        "---\n"
        "data_class: synthetic\n"
        "synthetic: true\n"
        f"skill: {skill}\n"
        f"date: {date}\n"
        "---\n"
    )


def render_capture(payload: dict) -> tuple[str, str]:
    date = require_text(payload.get("date"), "date")
    if not DATE_PATTERN.fullmatch(date):
        raise SkillStop("INVALID_INPUT", "Datum muss JJJJ-MM-TT entsprechen")
    title = require_text(payload.get("source_title"), "source_title")
    summary = require_text(payload.get("source_summary"), "source_summary")
    route = require_text(payload.get("suggested_target"), "suggested_target")
    if route not in ROUTES:
        raise SkillStop("INVALID_INPUT", "Unbekannte Zielroute")
    reason = require_text(payload.get("routing_reason"), "routing_reason")
    identifier = payload["id"]
    text = (
        frontmatter("capture-und-routing", date)
        + f"\n# Eingang: {title}\n\n"
        + "- Status: erfasst, nicht verschoben\n"
        + f"- Quelle-ID: `{identifier}`\n\n"
        + "## Unveränderte Quellangaben\n\n"
        + f"- Titel: {title}\n"
        + f"- Zusammenfassung: {summary}\n\n"
        + "## Routenvorschlag\n\n"
        + f"- Ziel: `{route}/`\n"
        + f"- Begründung: {reason}\n\n"
        + "## Human Gate\n\n"
        + "Quelle bleibt im Eingang. Verschieben und Priorisieren benötigen eine menschliche Bestätigung.\n"
    )
    return f"00-eingang/{identifier}.md", text


def render_project(payload: dict) -> tuple[str, str]:
    date = require_text(payload.get("date"), "date")
    if not DATE_PATTERN.fullmatch(date):
        raise SkillStop("INVALID_INPUT", "Datum muss JJJJ-MM-TT entsprechen")
    why = require_text(payload.get("why"), "why")
    users = require_list(payload.get("target_users"), "target_users")
    outcome = require_text(payload.get("desired_outcome"), "desired_outcome")
    non_goals = require_list(payload.get("non_goals"), "non_goals")
    boundaries = require_list(payload.get("boundaries"), "boundaries")
    next_action = require_text(payload.get("next_action"), "next_action")
    identifier = payload["id"]
    text = (
        frontmatter("projekt-start", date)
        + f"\n# Projekt: {identifier}\n\n"
        + "- Status: Entwurf, menschliche Freigabe offen\n"
        + "- Datenklasse: `S0 synthetic`\n\n"
        + f"## Why\n\n{why}\n\n"
        + f"## Zielnutzer\n\n{bullet_list(users)}\n\n"
        + f"## Gewünschtes Ergebnis\n\n{outcome}\n\n"
        + f"## Nicht-Ziele\n\n{bullet_list(non_goals)}\n\n"
        + f"## Grenzen\n\n{bullet_list(boundaries)}\n\n"
        + f"## Nächste sichere Aktion\n\n- {next_action}\n"
    )
    return f"02-projekte/{identifier}/PROJEKT.md", text


def render_decision(payload: dict) -> tuple[str, str]:
    date = require_text(payload.get("date"), "date")
    if not DATE_PATTERN.fullmatch(date):
        raise SkillStop("INVALID_INPUT", "Datum muss JJJJ-MM-TT entsprechen")
    question = require_text(payload.get("question"), "question")
    facts = require_list(payload.get("facts"), "facts")
    assumptions = require_list(payload.get("assumptions"), "assumptions")
    options = require_list(payload.get("options"), "options")
    owner = require_text(payload.get("owner"), "owner")
    human_gate = require_text(payload.get("human_gate"), "human_gate")
    identifier = payload["id"]
    text = (
        frontmatter("entscheidung-dokumentieren", date)
        + f"\n# Entscheidung: {question}\n\n"
        + "- Status: offen\n"
        + f"- Owner: {owner}\n"
        + f"- Human Gate: {human_gate}\n\n"
        + f"## Fakten\n\n{bullet_list(facts)}\n\n"
        + f"## Annahmen\n\n{bullet_list(assumptions)}\n\n"
        + f"## Optionen\n\n{bullet_list(options)}\n\n"
        + "## Entscheidung und Folgen\n\nNoch nicht menschlich entschieden. Keine Folge wird automatisch ausgelöst.\n"
    )
    return f"04-entscheidungen/{identifier}.md", text


def render_review(payload: dict) -> tuple[str, str]:
    date = require_text(payload.get("date"), "date")
    if not DATE_PATTERN.fullmatch(date):
        raise SkillStop("INVALID_INPUT", "Datum muss JJJJ-MM-TT entsprechen")
    period = require_text(payload.get("period"), "period")
    projects = payload.get("projects")
    if not isinstance(projects, list) or not projects:
        raise SkillStop("EMPTY_INPUT", "Aktive Projektliste fehlt oder ist leer")
    sections: list[str] = []
    for project in projects:
        if not isinstance(project, dict):
            raise SkillStop("INVALID_INPUT", "Projektstand muss ein Objekt sein")
        project_id = require_text(project.get("id"), "projects.id")
        if not ID_PATTERN.fullmatch(project_id):
            raise SkillStop("INVALID_INPUT", "Projekt-ID ist ungültig")
        title = require_text(project.get("title"), "projects.title")
        status = require_text(project.get("status"), "projects.status")
        blockers = require_list(project.get("blockers"), "projects.blockers", allow_empty=True)
        next_action = require_text(project.get("next_action"), "projects.next_action", allow_empty=True)
        blocker_text = bullet_list(blockers) if blockers else "- keine offenen Blocker gemeldet"
        action_text = f"- {next_action}" if next_action else "- keine; Restart-Entscheidung bleibt offen"
        sections.append(
            f"### {title} (`{project_id}`)\n\n"
            f"- Status: {status}\n\n"
            f"Blocker:\n\n{blocker_text}\n\n"
            f"Nächste Aktion, maximal eine:\n\n{action_text}"
        )
    decisions = require_list(payload.get("open_decisions"), "open_decisions", allow_empty=True)
    decision_text = bullet_list(decisions) if decisions else "- keine offenen Entscheidungen gemeldet"
    identifier = payload["id"]
    text = (
        frontmatter("wochenreview", date)
        + f"\n# Wochenreview {period}\n\n"
        + "- Status: Entwurf, nichts automatisch geschlossen\n\n"
        + "## Aktive und pausierte Projekte\n\n"
        + "\n\n".join(sections)
        + f"\n\n## Offene Entscheidungen\n\n{decision_text}\n\n"
        + "## Human Gate\n\nStatusänderungen, Priorisierung und Abschluss bleiben menschlich.\n"
    )
    return f"05-reviews/{identifier}.md", text


RENDERERS = {
    "capture-und-routing": render_capture,
    "projekt-start": render_project,
    "entscheidung-dokumentieren": render_decision,
    "wochenreview": render_review,
}


def validate_workspace(workspace: Path) -> Path:
    resolved = workspace.expanduser().resolve()
    if resolved == ROOT.resolve() or resolved.is_relative_to(ROOT.resolve()):
        raise SkillStop("INVALID_WORKSPACE", "Öffentlicher Starter und private Instanz müssen getrennt bleiben")
    marker = resolved / ".clief-instance.json"
    if not marker.is_file():
        raise SkillStop("INVALID_WORKSPACE", "Getrennte Clief-Instanz mit Marker fehlt")
    try:
        metadata = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SkillStop("INVALID_WORKSPACE", "Instanzmarker ist ungültig") from exc
    if metadata.get("data_class") != "synthetic" or metadata.get("synthetic") is not True:
        raise SkillStop("STOP_DATA_POLICY", "Instanz ist nicht synthetic-only")
    return resolved


def safe_write(workspace: Path, relative: str, content: str) -> str:
    destination = (workspace / relative).resolve(strict=False)
    if not destination.is_relative_to(workspace) or destination.is_symlink():
        raise SkillStop("INVALID_OUTPUT", "Output-Ziel verlässt den Workspace oder ist ein Symlink")
    encoded = content.encode("utf-8")
    if destination.exists():
        if destination.is_file() and destination.read_bytes() == encoded:
            return "unchanged"
        raise SkillStop(
            "OUTPUT_CONFLICT",
            "Vorhandener Output weicht ab; bewahre ihn und verwende bewusst eine neue Revisions-ID.",
            3,
        )
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise SkillStop("OUTPUT_CONFLICT", "Output entstand parallel; nichts wurde überschrieben.", 3) from exc
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    return "created"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()
    try:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        registered = {entry["id"] for entry in registry["skills"]}
        if args.skill not in registered or args.skill not in RENDERERS:
            raise SkillStop("UNKNOWN_SKILL", "Skill ist nicht in der lokalen Registry registriert")
        workspace = validate_workspace(args.workspace)
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise SkillStop("INVALID_INPUT", "Task-Paket muss ein JSON-Objekt sein")
        validate_common(payload)
        relative, content = RENDERERS[args.skill](payload)
        write_status = safe_write(workspace, relative, content)
        print(json.dumps({"status": write_status, "skill": args.skill, "output": relative}, ensure_ascii=False))
        return 0
    except SkillStop as exc:
        print(
            json.dumps(
                {"status": "stopped", "reason": exc.reason, "message": str(exc), "safe_alternative": SAFE_ALTERNATIVE},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return exc.exit_code
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(
            json.dumps(
                {"status": "stopped", "reason": "INVALID_INPUT", "message": str(exc), "safe_alternative": SAFE_ALTERNATIVE},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
