# capture-und-routing

## Zweck

Eine Quelle innerhalb der erklärten Instanz-Datenklasse unverändert in einem neuen Eingangsartefakt festhalten und ein Ziel mit Begründung vorschlagen.

## Trigger

„Erfasse diesen Eingang und schlage die passende Route vor.“

## Eingaben

Ein Task-Paket mit ID, Datum, Quelltitel, Quellzusammenfassung, Zielvorschlag, Routing-Begründung und Datenklasse passend zum Instanzmarker.

## Minimale Lesemenge

`_core/data-policy.md`, `CONTEXT.md` und nur dieses Task-Paket.

## Ausgabe

Genau eine neue Datei in `00-eingang/`; Quell-ID, Titel und Zusammenfassung bleiben enthalten. Keine Quelldatei wird verschoben oder verändert.

## Stop

Leere Pflichtfelder, eine den Instanzmarker überschreitende Datenklasse, `S3`, Secrets, unbekannte Route oder abweichender vorhandener Output stoppen vor dem Schreiben.

## Human Gates

Verschieben, Priorisieren, Kontaktieren und jede Außenaktion benötigen eine menschliche Entscheidung.

## Verbotene Zugriffe

Keine anderen Eingänge, kein Voll-Workspace-Scan, kein Home, Netzwerk, Connector, Git oder externes Ziel.

## Tests

Der mitgelieferte Referenz-Runner prüft Normal-, Leer-, Konflikt- und Schutzdatenfall ausschließlich mit `S0`; zusätzlich bleibt der Hash der Eingabedatei gleich.

## Herkunft und Lizenz

Originärer MoselMinds-Skill, Version 1.1.0, MIT. Kein Fremdskill gebündelt.
