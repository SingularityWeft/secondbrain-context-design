# SPEC-02 Akzeptanzevidenz

## Vor dem Build definierte Evidenz

| Kriterium | Erforderliche Evidenz |
|---|---|
| explizite Zielbestätigung | `plan` erzeugt keine Datei und bindet Ziel, Antworten und alle gerenderten Inhalte an einen SHA-256-Token; falscher Token stoppt vor Zielanlage |
| getrennte Instanz | Ziel innerhalb des Starters, Home-Root, breites Developer-Root, Symlink, unsicher berechtigter Zielordner und fremder nicht leerer Ordner werden abgewiesen |
| vollständiger Setup-Slice | alle geplanten Dateien werden genau einmal erzeugt, kein Git-Repository und keine Runtime-Verbindung angelegt |
| aufgelöste Konfiguration | erzeugte Instanz enthält keinen nicht ersetzten Template-Marker |
| eindeutiges Routing | sieben Kernbereiche erscheinen jeweils genau einmal in der Routing-Tabelle |
| Restart | `status` liefert einen letzten Schritt, drei sichtbare Blocker und genau eine nächste sichere Aktion |
| idempotenter Zweitlauf | identische Dateien werden übersprungen; manuell geänderte Datei bleibt unverändert und wird als Konflikt gemeldet |
| partielle Reparatur | fehlende unveränderte Datei wird ergänzt, ohne Konfliktdatei oder fremde untracked Datei zu verändern |
| Git-Grenze | Setup führt keine Git-Befehle aus; der vor dem Zweitlauf leere Index bleibt leer und `git status --short` zeigt Nutzeränderungen weiterhin |
| Anfängerprüfung | technisches Protokoll liegt vor; echter unabhängiger menschlicher Walkthrough bleibt blockiert und wird nicht simuliert |

Fokussierte Tests stehen in [`tests/test_spec_02.py`](../tests/test_spec_02.py). Der menschliche Gate-Status steht im [Walkthrough-Protokoll](../docs/setup-walkthrough.md) und in der [`owner-decision.md`](../docs/runtime/owner-decision.md).
