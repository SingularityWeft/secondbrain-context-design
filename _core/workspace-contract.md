# Kanonischer Workspace-Vertrag

## Zweck

Der Workspace hält User-Kontext, Unternehmenskontext, Arbeitsartefakte und Entscheidungen einer Solo-Beratung als lokale, lesbare Dateien. Er bleibt ohne Runtime nutzbar; `AGENT-INTERFACE.md` definiert den providerneutralen Austauschvertrag. Runtime-Adapter routen nur und sind keine Quelle der Produktlogik.

## Bereiche

| Bereich | Kanonische Aufgabe |
|---|---|
| `00-eingang/` | neue, noch nicht eingeordnete Arbeitsanfragen |
| `01-ausrichtung/` | explizite User-Ziele und Präferenzen sowie Who, Why, What, How, Zielgruppen, Angebote, Prinzipien und Grenzen |
| `02-projekte/` | aktive, begrenzte Vorhaben und ihre Artefakte |
| `03-wissen/` | geprüfte wiederverwendbare Referenzen |
| `04-entscheidungen/` | Entscheidungen mit Grund, Auswirkung und Status |
| `05-reviews/` | Status-, Qualitäts- und Rückblickartefakte |
| `99-archiv/` | abgeschlossene oder verworfene Inhalte; keine Löschung durch Setup |

Jeder Bereich hat genau eine Route in `CONTEXT.md`. Inhalte werden nicht zwischen Bereichen dupliziert, sondern relativ verlinkt.

## Setup- und Restart-Vertrag

1. Das öffentliche Starter-Repository und die private Instanz sind verschiedene Verzeichnisse.
2. `plan` zeigt alle Schreibpfade und einen daran gebundenen Bestätigungstoken.
3. `apply` schreibt erst bei exakt passendem Ziel, Antwortsatz und Token.
4. Ein vorhandener Zielordner muss bereits private Rechte ohne Gruppen- oder Fremdzugriff haben.
5. Bestehende abweichende Dateien werden niemals überschrieben; sie erscheinen als Konflikt.
6. Ein Wiederholungslauf ergänzt nur fehlende Artefakte und lässt fremde Dateien unberührt.
7. Das Setup führt keine Git-Befehle aus.
8. `STATUS.md` enthält genau einen letzten abgeschlossenen Schritt, sichtbare Blocker und eine nächste sichere Aktion.

## Daten- und Betriebsdefault

Im öffentlichen Starter und in Tests ist nur `S0 synthetic` erlaubt. Eine getrennte private Instanz darf nach expliziter Bestätigung `S1 internal` oder `S2 confidential` verwenden; `S3 restricted` bleibt gesperrt. Backup, Verschlüsselung, Synchronisation und jeder externe Agenten-Handoff bleiben `offen`, bis der Workspace-Owner sie bewusst entscheidet und technisch prüft.
