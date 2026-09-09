# SPEC-03 Akzeptanzevidenz

## Vor dem Build definierte Evidenz

| Kriterium | Erforderliche Evidenz |
|---|---|
| gemeinsamer Vertrag | Registry stimmt exakt mit vier Skill-Ordnern überein; jeder Vertrag enthält Eingaben, Ausgabe, minimale Lesemenge, Stop, Human Gates, verbotene Zugriffe, Tests und Lizenz |
| Normalfälle | vier synthetische Fixtures erzeugen vier vollständige Golden-Artefakte |
| Leerfälle | jeder Skill stoppt ohne Output bei leerem primären Pflichtinhalt |
| Schutzdatenfälle | jeder Skill stoppt vor Speicherung und nennt eine sichere synthetische Alternative |
| Konfliktfälle | nach manueller Output-Änderung stoppt jeder Wiederholungslauf; Hash bleibt gleich |
| Capture-Integrität | Hash der Inputquelle bleibt beim Normalfall unverändert; Ausgabe schlägt nur Ziel und Grund vor |
| Projektvertrag | Why, Zielnutzer, Ergebnis, Datenklasse, Nicht-Ziele und genau eine nächste Aktion |
| Entscheidungsvertrag | Fakten, Annahmen, Optionen, Owner und Human Gate getrennt; Status offen |
| Reviewvertrag | offene Blocker sichtbar, je Projekt höchstens eine nächste Aktion, kein automatisches Schließen |
| Herkunft | alle vier Skills originär unter MIT; keine Fremdskills gebündelt |

Golden-Artefakte liegen nach dem technischen Lauf unter `_evidence/skills/outputs/`. Endgültige Namen und Trigger bleiben bis zum echten Anfänger-Wording-Test ein Human Gate.
