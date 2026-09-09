# @@BUSINESS_NAME@@ – Workspace-Karte

Lade nur den Bereich, der zur aktuellen Aufgabe gehört. Die fachlichen Regeln stehen in `_core/`; `AGENT-INTERFACE.md` ist der gemeinsame Agentenvertrag und Runtime-Dateien routen nur.

| Aufgabe | Einzige kanonische Route |
|---|---|
| neue Anfrage erfassen | `00-eingang/` |
| User-Ziele, Arbeitsstil, Kommunikation, Kapazität, Who, Why, What, How, Zielgruppe, Angebot oder Grenze prüfen | `01-ausrichtung/` |
| aktives Vorhaben bearbeiten | `02-projekte/` |
| wiederverwendbares Wissen suchen oder pflegen | `03-wissen/` |
| Entscheidung dokumentieren oder nachlesen | `04-entscheidungen/` |
| Status oder Review durchführen | `05-reviews/` |
| abgeschlossene Inhalte nachschlagen | `99-archiv/` |
| wiederkehrende Basisaufgabe ausführen | passenden Eintrag in `skills/REGISTRY.json` lesen |
| Evidence-to-Artifact-Workflow ausführen | `workflows/evidence-to-artifact/CONTEXT.md` lesen |
| Kontext für einen Agenten ohne direkten Dateizugriff vorbereiten | `AGENT-INTERFACE.md` lesen und den lokalen Bundle-Builder des Starters verwenden |

Bei Unterbrechung zuerst `STATUS.md` lesen oder `status` über das Setup-Script des Starters ausführen.
