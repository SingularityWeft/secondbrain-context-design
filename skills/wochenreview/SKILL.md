# wochenreview

## Zweck

Einen Wochenstand innerhalb der erklärten Instanz-Datenklasse mit offenen Projekten, Entscheidungen, Blockern und Restart-Punkten zusammenführen.

## Trigger

„Erstelle aus diesem Arbeitsstand ein Wochenreview.“

## Eingaben

Review-ID, Zeitraum, aktive Projekte mit höchstens einer nächsten Aktion, offene Entscheidungen und Datenklasse passend zum Instanzmarker.

## Minimale Lesemenge

Nur die im Task-Paket genannten Projekt- und Entscheidungsstände; kein Voll-Workspace-Scan.

## Ausgabe

Genau eine neue Datei in `05-reviews/`; je Projekt null oder eine nächste Aktion, alle offenen Blocker bleiben sichtbar.

## Stop

Leere Projektliste, mehrere nächste Aktionen je Projekt, eine den Instanzmarker überschreitende Datenklasse, `S3`, Secrets oder abweichender vorhandener Output stoppen.

## Human Gates

Der Skill schließt, priorisiert oder verschiebt nichts. Alle Statusänderungen und Folgen bleiben menschlich.

## Verbotene Zugriffe

Kein Voll-Vault-Scan, keine automatische Priorisierung, kein Netzwerk, Connector, Git oder externes Ziel.

## Tests

Der mitgelieferte Referenz-Runner prüft Normal-, Leer-, Konflikt- und Schutzdatenfall ausschließlich mit `S0`; kein Projekt erhält mehr als eine nächste Aktion.

## Herkunft und Lizenz

Originärer MoselMinds-Skill, Version 1.1.0, MIT. Kein Fremdskill gebündelt.
