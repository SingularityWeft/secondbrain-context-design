# projekt-start

## Zweck

Eine Projektidee innerhalb der erklärten Instanz-Datenklasse als begrenztes Projekt mit genau einer nächsten sicheren Aktion anlegen.

## Trigger

„Starte aus dieser Idee ein begrenztes Projekt.“

## Eingaben

ID, Datum, Why, Zielnutzer, gewünschtes Ergebnis, Datenklasse, Nicht-Ziele, Grenzen und eine nächste Aktion.

## Minimale Lesemenge

`_core/data-policy.md`, `_core/workspace-contract.md` und nur dieses Task-Paket.

## Ausgabe

Genau eine neue `02-projekte/ID/PROJEKT.md` mit allen Pflichtabschnitten.

## Stop

Leere Pflichtfelder, eine den Instanzmarker überschreitende Datenklasse, `S3`, Secrets, mehrere nächste Aktionen oder abweichender vorhandener Output stoppen.

## Human Gates

Projektfreigabe, echte Beteiligte, Budget, Vertrag, Außenkontakt und Scope-Erweiterung bleiben menschlich.

## Verbotene Zugriffe

Kein Eingangsscan, keine Kontakte, kein Kalender, Netzwerk, Connector, Git oder externes Ziel.

## Tests

Der mitgelieferte Referenz-Runner prüft Normal-, Leer-, Konflikt- und Schutzdatenfall ausschließlich mit `S0`; der Normalfall enthält genau eine nächste Aktion.

## Herkunft und Lizenz

Originärer MoselMinds-Skill, Version 1.1.0, MIT. Kein Fremdskill gebündelt.
