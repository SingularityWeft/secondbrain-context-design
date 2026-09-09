#!/usr/bin/env python3
"""Plan, create, and inspect a separate local Clief workspace."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = ROOT / "template"
STATIC_SOURCES = (
    ROOT / "_core" / "data-policy.md",
    ROOT / "_core" / "human-gates.md",
    ROOT / "_core" / "policy.json",
    ROOT / "_core" / "runtime-policy.json",
    ROOT / "_core" / "workspace-contract.md",
)
SKILLS_ROOT = ROOT / "skills"
WORKFLOWS_ROOT = ROOT / "workflows"
STRING_FIELDS = (
    "workspace_id",
    "business_name",
    "owner_role",
    "who",
    "why",
    "what",
    "how",
    "working_style",
    "communication_preferences",
    "capacity_constraints",
    "support_preferences",
    "setup_date",
)
LIST_FIELDS = ("audiences", "offers", "principles", "boundaries", "user_goals")
MARKER_PATTERN = re.compile(r"@@([A-Z0-9_]+)@@")
INSTANCE_MARKER = ".clief-instance.json"
PRIVATE_DATA_CLASSES = {"internal", "confidential"}
ALLOWED_DATA_CLASSES = {"synthetic", *PRIVATE_DATA_CLASSES}
FORBIDDEN_CONTENT_PATTERNS = (
    re.compile(r"(?:passwort|password|api[_ -]?key|zugangsdaten|client[_ -]?secret)\s*[:=]", re.IGNORECASE),
    re.compile(r"s" + r"k-[A-Za-z0-9_-]{20,}"),
    re.compile(r"A" + r"KIA[0-9A-Z]{16}"),
    re.compile(r"g" + r"hp_[A-Za-z0-9]{30,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30}\b"),
    re.compile(r"(?:steuer-id|personalnummer|sozialversicherungsnummer)\s*[:=]", re.IGNORECASE),
)


class SetupError(RuntimeError):
    pass


def emit_error(message: str, code: int = 2) -> int:
    print(json.dumps({"status": "stopped", "reason": message}, ensure_ascii=False), file=sys.stderr)
    return code


def answer_text(answers: dict) -> str:
    values: list[str] = []
    for value in answers.values():
        if isinstance(value, str):
            values.append(value)
        elif isinstance(value, list):
            values.extend(item for item in value if isinstance(item, str))
    return "\n".join(values)


def load_answers(path: Path) -> dict:
    if path.is_symlink():
        raise SetupError("Antwortdatei darf kein Symlink sein")
    try:
        answers = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SetupError(f"Antwortdatei ist nicht lesbar: {exc}") from exc
    data_class = answers.get("data_class")
    if data_class not in ALLOWED_DATA_CLASSES:
        raise SetupError("data_class muss synthetic, internal oder confidential sein")
    expected_synthetic = data_class == "synthetic"
    if answers.get("synthetic") is not expected_synthetic:
        raise SetupError("Datenklasse und synthetic-Kennzeichnung widersprechen sich")
    if answers.get("contains_restricted_data") is not False:
        raise SetupError("S3 restricted muss ausdrücklich ausgeschlossen sein")
    if data_class in PRIVATE_DATA_CLASSES:
        resolved_answers = path.expanduser().resolve()
        if resolved_answers == ROOT.resolve() or resolved_answers.is_relative_to(ROOT.resolve()):
            raise SetupError("Private Antwortdateien dürfen nicht im öffentlichen Starter liegen")
        if path.stat().st_mode & 0o077:
            raise SetupError("Private Antwortdatei erlaubt Gruppen- oder Fremdzugriff")
    text = answer_text(answers)
    if any(pattern.search(text) for pattern in FORBIDDEN_CONTENT_PATTERNS):
        raise SetupError("S3-, Secret- oder Zugangsdatenmuster in der Antwortdatei erkannt")
    for field in STRING_FIELDS:
        value = answers.get(field)
        if not isinstance(value, str) or not value.strip():
            raise SetupError(f"Pflichtfeld fehlt oder ist leer: {field}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,48}", answers["workspace_id"]):
        raise SetupError("workspace_id muss ein kurzer Kleinbuchstaben-Slug sein")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", answers["setup_date"]):
        raise SetupError("setup_date muss das Format JJJJ-MM-TT haben")
    for field in LIST_FIELDS:
        value = answers.get(field)
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
            raise SetupError(f"Pflichtliste fehlt oder enthält leere Werte: {field}")
    return answers


def normalize_target(raw: str) -> Path:
    supplied = Path(raw).expanduser()
    if not supplied.is_absolute():
        raise SetupError("Das Ziel muss als absoluter Pfad angegeben werden")
    if supplied.is_symlink():
        raise SetupError("Ein Symlink darf nicht als Instanzziel dienen")
    target = supplied.resolve(strict=False)
    home = Path.home().resolve()
    unsafe_exact = {Path("/"), home, ROOT.resolve(), ROOT.parent.resolve()}
    if target in unsafe_exact or target.is_relative_to(ROOT.resolve()):
        raise SetupError("Breites, Starter-internes oder Home-Ziel ist nicht erlaubt")
    existing_parent = target.parent
    while not existing_parent.exists() and existing_parent != existing_parent.parent:
        existing_parent = existing_parent.parent
    if existing_parent.is_symlink():
        raise SetupError("Ein Symlink in der Zielkette ist nicht erlaubt")
    return target


def source_items() -> list[tuple[str, bytes]]:
    items: list[tuple[str, bytes]] = []
    for path in sorted(TEMPLATE_ROOT.rglob("*")):
        if path.is_file():
            items.append((str(path.relative_to(TEMPLATE_ROOT)), path.read_bytes()))
    for path in STATIC_SOURCES:
        items.append((str(Path("_core") / path.name), path.read_bytes()))
    for path in sorted(SKILLS_ROOT.rglob("*")):
        if path.is_file():
            items.append((str(Path("skills") / path.relative_to(SKILLS_ROOT)), path.read_bytes()))
    for path in sorted(WORKFLOWS_ROOT.rglob("*")):
        if path.is_file():
            items.append((str(Path("workflows") / path.relative_to(WORKFLOWS_ROOT)), path.read_bytes()))
    return sorted(items)


def template_digest(items: list[tuple[str, bytes]]) -> str:
    digest = hashlib.sha256()
    for relative, content in items:
        digest.update(relative.encode("utf-8") + b"\0" + content + b"\0")
    return digest.hexdigest()


def markdown_list(values: list[str]) -> str:
    return "\n".join(f"- {item.strip()}" for item in values)


def render_files(answers: dict) -> dict[str, bytes]:
    items = source_items()
    digest = template_digest(items)
    replacements = {
        "WORKSPACE_ID": answers["workspace_id"],
        "BUSINESS_NAME": answers["business_name"],
        "OWNER_ROLE": answers["owner_role"],
        "WHO": answers["who"],
        "WHY": answers["why"],
        "WHAT": answers["what"],
        "HOW": answers["how"],
        "WORKING_STYLE": answers["working_style"],
        "COMMUNICATION_PREFERENCES": answers["communication_preferences"],
        "CAPACITY_CONSTRAINTS": answers["capacity_constraints"],
        "SUPPORT_PREFERENCES": answers["support_preferences"],
        "USER_GOALS": markdown_list(answers["user_goals"]),
        "SETUP_DATE": answers["setup_date"],
        "AUDIENCES": markdown_list(answers["audiences"]),
        "OFFERS": markdown_list(answers["offers"]),
        "PRINCIPLES": markdown_list(answers["principles"]),
        "BOUNDARIES": markdown_list(answers["boundaries"]),
        "TEMPLATE_DIGEST": digest,
    }
    rendered: dict[str, bytes] = {}
    for relative, content in items:
        text = content.decode("utf-8")
        for key, value in replacements.items():
            text = text.replace(f"@@{key}@@", value)
        unresolved = sorted(set(MARKER_PATTERN.findall(text)))
        if unresolved:
            raise SetupError(f"Nicht aufgelöste Marker in {relative}: {', '.join(unresolved)}")
        rendered[relative] = text.encode("utf-8")
    manifest = {
        "schema_version": "1.0",
        "workspace_id": answers["workspace_id"],
        "data_class": answers["data_class"],
        "synthetic": answers["synthetic"],
        "contains_restricted_data": False,
        "instance_mode": "example" if answers["synthetic"] else "private",
        "private_setup_acknowledged": not answers["synthetic"],
        "setup_date": answers["setup_date"],
        "template_digest": digest,
        "public_private_separation": "separate-directory",
        "backup": "open",
        "encryption": "open",
        "sync": "not-configured",
        "external_transfer": "human-gate",
        "direct_agent_workspace_access": "blocked" if not answers["synthetic"] else "synthetic-only",
        "context_bundle_required": not answers["synthetic"],
    }
    rendered[INSTANCE_MARKER] = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return dict(sorted(rendered.items()))


def confirmation_token(target: Path, answers: dict, rendered: dict[str, bytes]) -> str:
    payload = {
        "target": str(target),
        "answers": answers,
        "files": {path: hashlib.sha256(content).hexdigest() for path, content in rendered.items()},
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def plan_payload(target: Path, answers: dict, rendered: dict[str, bytes]) -> dict:
    state = "absent"
    if target.exists():
        state = "empty" if not any(target.iterdir()) else "existing"
    return {
        "status": "planned",
        "write_performed": False,
        "target": str(target),
        "target_state": state,
        "data_class": answers["data_class"],
        "private_instance": not answers["synthetic"],
        "requires_private_data_acknowledgement": not answers["synthetic"],
        "warnings": (
            [
                "Private Instanz: Backup, Verschlüsselung und Synchronisation sind nicht automatisch eingerichtet.",
                "Lokale Speicherung erlaubt keine automatische Übertragung an einen Agenten.",
                "S3 restricted und Secrets bleiben verboten.",
            ]
            if not answers["synthetic"]
            else []
        ),
        "planned_paths": list(rendered),
        "confirmation_token": confirmation_token(target, answers, rendered),
    }


def ensure_private_parent(root: Path, parent: Path) -> None:
    current = root
    for part in parent.relative_to(root).parts:
        current = current / part
        if current.exists():
            if current.is_symlink() or not current.is_dir() or current.stat().st_mode & 0o077:
                raise SetupError(f"Unsicherer oder fremder Zielordner: {current.relative_to(root)}")
        else:
            current.mkdir(mode=0o700)


def write_new_file(root: Path, path: Path, content: bytes) -> bool:
    ensure_private_parent(root, path.parent)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise
    return True


def apply_plan(
    target: Path,
    answers: dict,
    rendered: dict[str, bytes],
    supplied_token: str,
    acknowledge_private_data: bool,
) -> int:
    expected = confirmation_token(target, answers, rendered)
    if not hmac.compare_digest(supplied_token, expected):
        raise SetupError("Bestätigungstoken passt nicht zu Ziel, Antworten und Template")
    if answers["data_class"] in PRIVATE_DATA_CLASSES and not acknowledge_private_data:
        raise SetupError("Private Dateninstanz benötigt --acknowledge-private-data")
    if target.exists() and not target.is_dir():
        raise SetupError("Ziel existiert und ist kein Ordner")
    if target.exists() and target.stat().st_mode & 0o077:
        raise SetupError("Vorhandener Zielordner erlaubt Gruppen- oder Fremdzugriff")
    if target.exists() and any(target.iterdir()) and not (target / INSTANCE_MARKER).is_file():
        raise SetupError("Nicht leerer fremder Zielordner ohne Instanzmarker")
    if (target / INSTANCE_MARKER).is_file():
        try:
            marker = json.loads((target / INSTANCE_MARKER).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SetupError("Vorhandener Instanzmarker ist ungültig") from exc
        if (
            marker.get("schema_version") != "1.0"
            or marker.get("workspace_id") != answers["workspace_id"]
            or marker.get("data_class") != answers["data_class"]
            or marker.get("synthetic") is not answers["synthetic"]
            or marker.get("contains_restricted_data") is not False
        ):
            raise SetupError("Vorhandener Instanzmarker gehört nicht zu diesem Workspace")
    target.mkdir(mode=0o700, parents=True, exist_ok=True)

    created: list[str] = []
    skipped: list[str] = []
    conflicts: list[str] = []
    ordered_paths = [INSTANCE_MARKER] + [path for path in rendered if path != INSTANCE_MARKER]
    for relative in ordered_paths:
        destination = target / relative
        if destination.is_symlink():
            conflicts.append(relative)
            continue
        if destination.exists():
            if destination.is_file() and destination.read_bytes() == rendered[relative]:
                skipped.append(relative)
            else:
                conflicts.append(relative)
            continue
        if write_new_file(target, destination, rendered[relative]):
            created.append(relative)
        else:
            conflicts.append(relative)

    result = {
        "status": "conflict" if conflicts else "applied",
        "target": str(target),
        "created": created,
        "skipped": skipped,
        "conflicts": conflicts,
        "git_commands_executed": False,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 3 if conflicts else 0


def read_status(target: Path) -> dict:
    marker = target / INSTANCE_MARKER
    status_path = target / "STATUS.md"
    if not marker.is_file() or not status_path.is_file():
        raise SetupError("Ziel ist keine vollständige Clief-Instanz")
    text = status_path.read_text(encoding="utf-8")
    completed = re.findall(r"^- Letzter abgeschlossener Schritt:\s*(.+)$", text, re.MULTILINE)
    blockers = re.findall(r"^- Blocker:\s*(.+)$", text, re.MULTILINE)
    next_actions = re.findall(r"^- Nächste sichere Aktion:\s*(.+)$", text, re.MULTILINE)
    if len(completed) != 1 or not blockers or len(next_actions) != 1:
        raise SetupError("STATUS.md verletzt den Restart-Vertrag")
    return {
        "status": "ready",
        "data_class": json.loads(marker.read_text(encoding="utf-8"))["data_class"],
        "last_completed": completed[0],
        "blockers": blockers,
        "next_safe_action": next_actions[0],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "apply"):
        command = subparsers.add_parser(name)
        command.add_argument("--answers", required=True, type=Path)
        command.add_argument("--target", required=True)
        if name == "apply":
            command.add_argument("--confirm-token", required=True)
            command.add_argument("--acknowledge-private-data", action="store_true")
    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--target", required=True)
    args = parser.parse_args()

    try:
        target = normalize_target(args.target)
        if args.command == "status":
            print(json.dumps(read_status(target), indent=2, ensure_ascii=False))
            return 0
        answers = load_answers(args.answers)
        rendered = render_files(answers)
        if args.command == "plan":
            print(json.dumps(plan_payload(target, answers, rendered), indent=2, ensure_ascii=False))
            return 0
        return apply_plan(target, answers, rendered, args.confirm_token, args.acknowledge_private_data)
    except (SetupError, OSError, UnicodeError) as exc:
        return emit_error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
