# entscheidung-dokumentieren

## Zweck

Eine offene Entscheidung innerhalb der erklärten Instanz-Datenklasse so dokumentieren, dass Fakten, Annahmen, Optionen, Owner und Human Gate getrennt bleiben.

## Trigger

„Dokumentiere diese offene Entscheidung.“

## Eingaben

ID, Datum, Frage, Fakten, Annahmen, Optionen, Owner, Human Gate und Datenklasse passend zum Instanzmarker.

## Minimale Lesemenge

`_core/human-gates.md` und nur dieses Task-Paket.

## Ausgabe

Genau eine neue Datei in `04-entscheidungen/`; Status bleibt `offen`.

## Stop

Leere Fakten, Annahmen oder Optionen, fehlender Owner/Gate, eine den Instanzmarker überschreitende Datenklasse, `S3`, Secrets oder abweichender vorhandener Output stoppen.

## Human Gates

Der Skill dokumentiert, entscheidet aber nicht. Nur der benannte menschliche Owner darf den Status ändern oder Folgen auslösen.

## Verbotene Zugriffe

Keine automatische Bewertung mit Rechts-, Steuer- oder Compliancewirkung; kein Netzwerk, Connector, Git oder externes Ziel.

## Tests

Der mitgelieferte Referenz-Runner prüft Normal-, Leer-, Konflikt- und Schutzdatenfall ausschließlich mit `S0`; Fakten und Annahmen stehen in getrennten Abschnitten.

## Herkunft und Lizenz

Originärer MoselMinds-Skill, Version 1.1.0, MIT. Kein Fremdskill gebündelt.
