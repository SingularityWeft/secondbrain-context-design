# Evidence-to-Artifact

Ein begrenzter, lokaler Workflow für eine generische Workshop-Outline:

1. Briefing
2. Evidence/Claim Ledger
3. Strukturentwurf
4. Human Review
5. freigegebener Arbeitsstand
6. Debrief

Die ersten vier Stufen können technisch vorbereitet werden. Kritische Claims und der finale Arbeitsstand stoppen am Human Gate. Automatisierte Tests verwenden nur als `technical-fixture-not-human` markierte Entscheidungen; deren Arbeitsstand bleibt `not-human-approved` und darf weder an Kundinnen gehen noch veröffentlicht werden.

Der [Router](CONTEXT.md) nennt pro Stufe die minimale Lesemenge. Der synthetische Referenzfall liegt unter [`fixtures/synthetic-workshop/`](fixtures/synthetic-workshop/), die Bewertungsrubrik in [`rubric.json`](rubric.json).

Technischer Lauf in einem temporären Verzeichnis:

```bash
python3 scripts/run_evidence_workflow.py prepare --case workflows/evidence-to-artifact/fixtures/synthetic-workshop/manifest.json --run-dir /private/tmp/clief-workflow-run
```

Danach ist der Status `awaiting-human-review`. Ohne Entscheidungsakte erzeugt `finalize` keinen freigegebenen Arbeitsstand.
