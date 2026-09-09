# SecondBrain Context Design Starter

Ein öffentlicher Alpha-Starter für einen lokalen, deutschsprachigen und providerneutralen Unternehmens-Workspace von Solo-Beratungen. Er hilft Menschen und ihren dateifähigen KI-Agents, Unternehmenswissen, persönlichen Arbeitskontext und wiederholbare Abläufe nachvollziehbar zu verwenden, ohne die Knowledge Base an einen einzelnen Modellanbieter zu binden.

Der Starter organisiert Kontext, Arbeitsabläufe, prüfbare Übergaben und menschliche Entscheidungen in lesbaren Dateien. Das öffentliche Repo enthält ausschließlich synthetische Beispieldaten. Eine ausdrücklich bestätigte private Instanz kann reale interne oder vertrauliche Daten lokal außerhalb des Repos halten: keine Datenbank, kein SaaS, keine externen Connectoren und keine automatische Veröffentlichung oder Übertragung.

## Sicher beginnen

Lies zuerst [START-HIER.md](START-HIER.md). Dort stehen Zweck, erwartetes Ergebnis, Datenverbote und die erste lokale Prüfung vor jeder späteren Einrichtung.

## Was dieser Stand leistet

- lokale und nachvollziehbare Richtlinien für Daten, Human Gates und Claims;
- eine [providerneutrale Agent-Schnittstelle](docs/agent-interoperabilitaet.md), die Menschen und beliebige dateifähige Agents über denselben Kontextvertrag nutzen können;
- ein maschinell prüfbarer Sicherheits- und Lizenzvertrag;
- lokale Git-Historie als reversible Änderungsspur.

## Was dieser Stand nicht behauptet

- keine rechtliche Zertifizierung oder Rechtsberatung;
- keine Garantie für Verschlüsselung, Backup, Prozessisolation oder die Datenpraxis eines verwendeten Agenten;
- keine selbstständig durch KI ausgeübte Leitung eines Unternehmens;
- keine nachgewiesene Geschäfts- oder Qualitätswirkung über den dokumentierten technischen Alpha-Stand hinaus.

Die kanonischen Regeln stehen in der [Datenrichtlinie](_core/data-policy.md) und der [Human-Gate-Matrix](_core/human-gates.md). Herkunft und Lizenzhinweise stehen in [NOTICE.md](NOTICE.md), Sicherheitsgrenzen in [SECURITY.md](SECURITY.md).

Der technisch geprüfte Runtime-Default und seine Grenzen stehen in der [Runtime-Matrix](docs/runtime/runtime-matrix.md). Er bleibt auf synthetische Daten beschränkt.

Eine getrennte synthetische oder private Instanz lässt sich über den [Setup-Leitfaden](docs/setup.md) zuerst planen und danach mit dem angezeigten Ziel-Token erzeugen. Private Antworten müssen owner-only außerhalb des Repos liegen und benötigen beim Anwenden eine zusätzliche Bestätigung. Das Setup initialisiert oder verändert kein Git-Repository.

Die Instanz hält User-Ziele, Arbeitsstil, Kommunikations- und Kapazitätspräferenzen explizit lokal. Für Agents ohne direkten Dateizugriff erzeugt `scripts/build_agent_context.py` ein begrenztes lokales Kontext-Bundle mit Quellen und Hashes; eine Übertragung geschieht nicht automatisch.

Vier begrenzte, deutsch benannte [Basisskills](docs/skills.md) decken Capture/Routing, Projektstart, Entscheidungsdokumentation und Wochenreview ab. Ihre Verträge gelten höchstens innerhalb der erklärten Instanz-Datenklasse und besitzen keine Außenaktionen; der mitgelieferte deterministische Test-Runner bleibt rein synthetisch.

Der [Evidence-to-Artifact-Workflow](workflows/evidence-to-artifact/README.md) führt ein synthetisches Briefing über Claim Ledger, Struktur und Human Gate bis zum Debrief. Technische Gate-Fixtures sind ausdrücklich keine menschliche Freigabe.

Der gesamte lokale Vertrag läuft über genau einen Einstieg:

```bash
bash scripts/verify-repo.sh
```

Der Verify ist offline und umfasst Repository-Scans, alle fokussierten Tests sowie den [synthetischen E2E-Fall](examples/synthetische-beratung/README.md). In einem Git-Clone prüft er zusätzlich die vollständige Objekthistorie. Bei einem GitHub-ZIP wird dieser nicht vorhandene Historienteil sichtbar als `NOT_APPLICABLE` markiert; alle Inhaltsprüfungen laufen trotzdem. Der [unabhängige Anfänger-Walkthrough](docs/testing/anfaenger-walkthrough.md) ist ein separates Human Gate und wird nicht durch technische Tests ersetzt.

Das [Pilotpaket](pilot/README.md) trennt freiwillige Einladung, neutralen Testauftrag, Pilotvereinbarung, Einwilligung, Befunde, Retests und öffentliche GO/NO-GO-Entscheidung. Es ist technisch vorbereitet, dokumentiert aber bewusst noch keinen realen Lauf.

## Lizenz

Die originären Bestandteile dieses Repositories stehen unter der [MIT-Lizenz](LICENSE). Externe Ursprünge und davon getrennte Hinweise sind in [NOTICE.md](NOTICE.md) inventarisiert.
