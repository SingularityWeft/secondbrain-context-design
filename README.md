# SecondBrain Context Design Starter

Ein öffentlicher Alpha-Starter für einen lokalen, deutschsprachigen und providerneutralen Unternehmens-Workspace für Solo-Preneure oder kleine Teams. Er hilft Menschen und ihren dateifähigen AI-Agents, Unternehmenswissen, persönlichen Arbeitskontext und wiederholbare Abläufe sowie Ziele nachvollziehbar zu verwenden, ohne die Knowledge Base an einen einzelnen Modellanbieter zu binden.

Der Starter organisiert Kontext, Arbeitsabläufe, prüfbare Übergaben und menschliche Entscheidungen in lesbaren Dateien. Das öffentliche Repo enthält ausschließlich synthetische Beispieldaten. Eine ausdrücklich bestätigte private Instanz kann reale interne oder vertrauliche Daten lokal außerhalb des Repos halten. Dieses Projekt ist keine Datenbank, kein SaaS und enthält keine externen Connectoren und keine automatische Veröffentlichung oder Übertragung.

## Sicher beginnen

Lies zuerst [START-HIER.md](START-HIER.md). Dort stehen Zweck, erwartetes Ergebnis, Datenverbote und die erste lokale Prüfung vor der Einrichtung.

## Zwei Phasen: Technik prüfen, dann echten Nutzen testen

1. Prüfe gemeinsam mit deinem Agent (Codex, Claude Code, Hermes oder Grok Bot), ob Verify, Installation und Setup auf deinem Rechner funktionieren.
2. Lege danach für einen echten, überschaubaren Anwendungsfall eine getrennte private Instanz außerhalb des geklonten Repositories an. Verwende nur bewusst ausgewählte Arbeitsinformationen und entscheide vorab, welchem Agenten beziehungsweise Anbieter dessen AI-Model du nutzt du diese Daten anvertrauen willst.

Öffentliche GitHub-Repositories, Git-Historie sowie öffentliche Issues und Pull Requests dürfen keine vertraulichen oder personenbezogenen Inhalte, Secrets, internen Dokumente oder persönlichen Dateipfade enthalten. Die private Instanz bleibt lokal beim User und gehört nie in einen öffentlichen Clone.

### Einrichtungsprompt für Claude, Codex oder einen anderen dateifähigen Agenten

Kopiere diesen Prompt in den Agenten, der auf deinem Rechner Dateien bearbeiten darf:

> Hilf mir, den SecondBrain Context Design Starter sicher in zwei Phasen einzurichten. Lies zuerst `START-HIER.md`, `SECURITY.md`, `docs/setup.md` und `docs/agent-interoperabilitaet.md`. Prüfe im öffentlichen Clone ausschließlich mit dem synthetischen Beispiel den Verify- und Setup-Pfad. Berichte mir das Ergebnis und stoppe vor der privaten Phase. Frage mich dann nach einem getrennten lokalen Zielordner außerhalb des Clones, einem einzigen überschaubaren echten Anwendungsfall, der Datenklasse `internal` oder `confidential` und den konkret erlaubten Informationen. Zeige mir vor jedem Zugriff auf echte Daten die Agenten-/Anbietergrenze und warte auf meine Bestätigung. Erzeuge die private Antwortdatei owner-only außerhalb des Repositories, führe zuerst `plan` aus und zeige Ziel, Dateiliste, Warnungen und Bestätigungstoken. Führe `apply` erst nach meiner Bestätigung aus. Verwende keine Secrets oder `S3 restricted`-Daten und schreibe keine echten Inhalte, persönlichen Pfade oder Logs in das öffentliche Repository, Git, Issues oder Pull Requests. Arbeite in der privaten Instanz nur mit den für die konkrete Aufgabe freigegebenen Pfaden oder einem begrenzten Kontext-Bundle. Bei Problemen diagnostiziere zunächst lokal. Ist eine Verbesserung allgemein nützlich, bereite ein vollständig bereinigtes Issue oder einen kleinen Pull Request nach `CONTRIBUTING.md` vor; veröffentliche nichts ohne meine separate Freigabe.

## Was dieser Stand leistet

- lokale und nachvollziehbare Richtlinien für Daten, Human Gates und Claims;
- eine [providerneutrale Agent-Schnittstelle](docs/agent-interoperabilitaet.md), die Menschen und beliebige dateifähige Agents über denselben Kontextvertrag nutzen können;
- einen zweistufigen Praxistest aus synthetischem Technikcheck und getrenntem privaten Anwendungsfall;
- ein maschinell prüfbarer Sicherheits- und Lizenzvertrag;

## Was dieser Stand nicht behauptet

- keine rechtliche Zertifizierung oder Rechtsberatung;
- keine Garantie für Verschlüsselung, Backup, Prozessisolation oder die Datenpraxis eines verwendeten AI-Agenten;
- keine selbstständig durch KI ausgeübte Leitung eines Unternehmens;
- keine nachgewiesene Geschäfts- oder Qualitätswirkung über den dokumentierten technischen Alpha-Stand hinaus.

Die kanonischen Regeln stehen in der [Datenrichtlinie](_core/data-policy.md) und der [Human-Gate-Matrix](_core/human-gates.md). Herkunft und Lizenzhinweise stehen in [NOTICE.md](NOTICE.md), Sicherheitsgrenzen in [SECURITY.md](SECURITY.md).

Der technisch geprüfte isolierte Runtime-Default und seine Grenzen stehen in der [Runtime-Matrix](docs/runtime/runtime-matrix.md). Dieser bereitgestellte Prüfpfad bleibt auf synthetische Daten beschränkt. Ein privater Praxistest mit Claude, Codex, Grok oder einem anderen Agenten ist eine separate bewusste Anbieter- und Datenentscheidung des Users und kein Sicherheitsclaim dieses Repositories.

Eine getrennte synthetische oder private Instanz lässt sich über den [Setup-Leitfaden](docs/setup.md) zuerst planen und danach mit dem angezeigten Ziel-Token erzeugen. Private Antworten müssen owner-only außerhalb des Repos liegen und benötigen beim Anwenden eine zusätzliche Bestätigung. Das Setup initialisiert oder verändert kein Git-Repository.

Die Instanz hält User-Ziele, Arbeitsstil, Kommunikations- und Kapazitätspräferenzen explizit lokal. Für Agents ohne direkten Dateizugriff erzeugt `scripts/build_agent_context.py` ein begrenztes lokales Kontext-Bundle mit Quellen und Hashes; eine Übertragung geschieht nicht automatisch!

Vier begrenzte, deutsch benannte [Basisskills](docs/skills.md) decken Capture/Routing, Projektstart, Entscheidungsdokumentation und Wochenreview ab. Ihre Verträge gelten höchstens innerhalb der erklärten Instanz-Datenklasse und besitzen keine Außenaktionen; der mitgelieferte deterministische Test-Runner bleibt rein synthetisch.

Der [Evidence-to-Artifact-Workflow](workflows/evidence-to-artifact/README.md) führt ein synthetisches Briefing über Claim Ledger, Struktur und Human Gate bis zum Debrief. Technische Gate-Fixtures sind ausdrücklich keine menschliche Freigabe.

Der gesamte lokale Vertrag läuft über diesen Einstieg:

```bash
bash scripts/verify-repo.sh
```

Der Verify ist offline und umfasst Repository-Scans, alle fokussierten Tests sowie den [synthetischen E2E-Fall](examples/synthetische-beratung/README.md). In einem Git-Clone prüft er zusätzlich die vollständige Objekthistorie. Bei einem GitHub-ZIP wird dieser nicht vorhandene Historienteil sichtbar als `NOT_APPLICABLE` markiert; alle Inhaltsprüfungen laufen trotzdem. Der [unabhängige Anfänger-Walkthrough](docs/testing/anfaenger-walkthrough.md) ist ein separates Human Gate und wird nicht durch technische Tests ersetzt.

Das [Pilotpaket](pilot/README.md) trennt freiwillige Einladung, synthetischen Technikcheck, privaten Praxistest, Einwilligung, Befunde, Retests und öffentliche GO/NO-GO-Entscheidung. Es ist technisch vorbereitet, dokumentiert aber bewusst noch keinen realen Lauf.

Bei Installationsproblemen oder allgemein nützlichen Verbesserungen helfen die Hinweise in [CONTRIBUTING.md](CONTRIBUTING.md). Öffentliche Rückmeldungen werden immer auf eine bereinigte Reproduktion ohne private Inhalte reduziert.

Bei Problemen können Claude, Codex, Grok oder andere dateifähige Agents zunächst lokal unterstützen. Wenn das Problem damit nicht lösbar ist, melde dich gern über ein bereinigtes Issue oder den bereits vereinbarten direkten Kontaktweg bei der Maintainerin.

Die Entwicklungen im Bereich Artificial Intelligence, Agentic Engineering und Machine Learning schreiten mit erwartbar exponentieller Steigerung voran, daher können sich im Verlauf der Zeit größere Änderungen an diesem Repository ergeben. 

## Lizenz

Die originären Bestandteile dieses Repositories stehen unter der [MIT-Lizenz](LICENSE). Externe Ursprünge und davon getrennte Hinweise sind in [NOTICE.md](NOTICE.md) inventarisiert.
