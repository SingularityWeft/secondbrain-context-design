# Vier sichere Basisskills

Die [Skill-Registry](../skills/REGISTRY.json) ist der maschinenlesbare Einstieg. Jeder Skill ist ein kleiner Markdown-Vertrag und kann von Menschen oder verschiedenen KI-Runtimes gelesen werden. In einer privaten Instanz gilt dabei höchstens die Datenklasse aus `.clief-instance.json`; `S3` und Secrets bleiben gesperrt. Das Python-Script ist nur ein deterministischer `S0`-Referenz-Runner für Tests und lokale synthetische Artefakte, nicht der Agent selbst.

| Skill | Zweck | Lokales Ziel | Außenwirkung |
|---|---|---|---|
| `capture-und-routing` | Eingang unverändert erfassen und Ziel begründet vorschlagen | `00-eingang/` | keine; Verschieben blockiert |
| `projekt-start` | ein begrenztes Projekt mit genau einer nächsten Aktion anlegen | `02-projekte/` | keine |
| `entscheidung-dokumentieren` | Fakten, Annahmen, Optionen, Owner und Gate trennen | `04-entscheidungen/` | keine; Entscheidung bleibt menschlich |
| `wochenreview` | offene Projekte, Entscheidungen, Blocker und Restart-Punkte bündeln | `05-reviews/` | keine; nichts wird geschlossen |

Beispiel für eine bereits getrennt eingerichtete synthetische Instanz:

```bash
python3 scripts/run_skill.py --workspace /private/tmp/clief-demo-instanz --skill capture-und-routing --input tests/fixtures/skills/capture-und-routing.json
```

Bei `STOP_DATA_POLICY`, `EMPTY_INPUT`, `OUTPUT_CONFLICT` oder unbekanntem Skill wird nichts überschrieben. Die sichere Alternative ist stets eine vollständig erfundene, klar markierte Kopie beziehungsweise eine bewusst neu benannte Revision.
