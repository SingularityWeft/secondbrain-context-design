# Agent-Interoperabilität

Der Workspace bindet seine Produktlogik nicht an einen Modell- oder Agentenanbieter. Der gemeinsame Vertrag besteht aus lesbaren Markdown-/JSON-Dateien:

- `AGENT-INTERFACE.md` – Verhalten und Rückgabeformat;
- `CONTEXT.md` – Routing zur aktuellen Aufgabe;
- `STATUS.md` – letzter Schritt, Blocker und nächste sichere Aktion;
- `01-ausrichtung/user-context.md` – explizite Ziele und Arbeitspräferenzen;
- `01-ausrichtung/business-context.md` – fachlicher Unternehmenskontext;
- `_core/` – Daten-, Workspace- und Human-Gate-Regeln.

`AGENTS.md` und `CLAUDE.md` sind optionale Runtime-Adapter. Ein Agent ohne Unterstützung dieser Dateinamen kann dasselbe Protokoll über ein lokal erzeugtes Kontext-Bundle erhalten. Das belegt Formatinteroperabilität, nicht die Sicherheit, Qualität oder native Integration eines bestimmten Produkts.

## Lokales Kontext-Bundle

Nach einem synthetischen Setup aus dem Starter-Root:

```bash
python3 scripts/build_agent_context.py \
  --workspace /private/tmp/clief-demo-instanz \
  --task "Ordne die synthetische Anfrage und nenne genau eine nächste sichere Aktion." \
  --as-of 2026-09-09T12:00:00+02:00 \
  --include 00-eingang/README.md \
  --output 05-reviews/agent-context/anfrage-routing.md
```

Der Builder schreibt ausschließlich die angegebene neue lokale Datei, überschreibt nichts und ruft weder Netzwerk, Modell noch Connector auf. Das Bundle enthält ein Manifest mit relativen Quellpfaden und SHA-256-Hashes. Die Übergabe an einen externen Agenten ist eine separate bewusste Handlung des Users und muss zu dessen Daten- und Vertrauensgrenze passen.

## Private Instanz

Für `S1 internal` oder `S2 confidential` müssen Zweck und Zielagent ausdrücklich benannt werden:

```bash
python3 scripts/build_agent_context.py \
  --workspace "$HOME/Documents/clief-private" \
  --task "Ordne diese Anfrage und schlage eine nächste sichere Aktion vor." \
  --as-of 2026-09-09T12:00:00+02:00 \
  --agent-label "mein gewählter Agent" \
  --purpose "Projektkontext für diese eine Planungsaufgabe" \
  --handoff-mode local \
  --acknowledge-private-context \
  --include 00-eingang/meine-anfrage.md \
  --output 05-reviews/agent-context/planung.md
```

Direkte Identitätsmerkmale sind in `S1` gesperrt. Bei `S2` verlangt ihre Aufnahme zusätzlich `--allow-direct-identifiers`. Ein für manuelle externe Übergabe bestimmtes Bundle verlangt `--handoff-mode manual-external` und `--acknowledge-external-handoff`. Diese Flags führen selbst keine Übertragung aus.

## Vertrauensgrenze

Quellinhalte werden im Bundle als untrusted data gekennzeichnet und dürfen die kanonischen Regeln nicht überschreiben. Tests und öffentliche Fixtures bleiben vollständig synthetisch. Private Dateien werden auf owner-only Rechte geprüft; Mustererkennung kann dennoch nicht beweisen, dass Inhalte korrekt klassifiziert sind.

Lokale Speicherung allein beweist keine lokale Modellverarbeitung. Vor einem externen Agenten-Handoff muss der User dessen Aufbewahrung, Training, Löschung, Zugriff und Anbietergrenze selbst prüfen.
