#!/usr/bin/env python3
"""Validate the bounded provider-neutral skill contracts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REQUIRED_HEADINGS = (
    "## Zweck",
    "## Trigger",
    "## Eingaben",
    "## Minimale Lesemenge",
    "## Ausgabe",
    "## Stop",
    "## Human Gates",
    "## Verbotene Zugriffe",
    "## Tests",
    "## Herkunft und Lizenz",
)
EXPECTED_IDS = {
    "capture-und-routing",
    "projekt-start",
    "entscheidung-dokumentieren",
    "wochenreview",
}


def main() -> int:
    try:
        registry = json.loads((SKILLS / "REGISTRY.json").read_text(encoding="utf-8"))
        if registry.get("schema_version") != "1.0" or registry.get("license") != "MIT":
            raise ValueError("Registry-Schema oder Lizenz ungültig")
        if registry.get("external_skills_bundled") is not False:
            raise ValueError("Fremdskill-Grenze ist nicht fail-closed")
        entries = registry.get("skills", [])
        ids = {entry.get("id") for entry in entries}
        folders = {path.name for path in SKILLS.iterdir() if path.is_dir()}
        if ids != EXPECTED_IDS or folders != EXPECTED_IDS or len(entries) != 4:
            raise ValueError("Registry und Skill-Ordner stimmen nicht exakt überein")
        for entry in entries:
            if not re.fullmatch(r"\d+\.\d+\.\d+", entry.get("version", "")):
                raise ValueError(f"Ungültige Skill-Version: {entry.get('id')}")
            if entry.get("output_root") not in {
                "00-eingang",
                "02-projekte",
                "04-entscheidungen",
                "05-reviews",
            }:
                raise ValueError(f"Unbekanntes Output-Ziel: {entry.get('id')}")
            contract = (SKILLS / entry["contract"]).resolve()
            if not contract.is_relative_to(SKILLS.resolve()) or not contract.is_file():
                raise ValueError(f"Fehlender oder externer Vertrag: {entry.get('id')}")
            text = contract.read_text(encoding="utf-8")
            missing = [heading for heading in REQUIRED_HEADINGS if heading not in text]
            if missing:
                raise ValueError(f"Vertrag unvollständig {entry['id']}: {', '.join(missing)}")
            if "Kein Fremdskill gebündelt." not in text:
                raise ValueError(f"Herkunftsgrenze fehlt: {entry['id']}")
            if len(text.splitlines()) > 90:
                raise ValueError(f"Skill-Vertrag ist unnötig lang: {entry['id']}")
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"SKILL_CONTRACT_STOP: {exc}", file=sys.stderr)
        return 2
    print("SKILL_CONTRACT_PASS skills=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
