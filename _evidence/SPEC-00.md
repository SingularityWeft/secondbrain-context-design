# SPEC-00 Akzeptanzevidenz

## Vor dem Build definierte Evidenz

| Kriterium | Evidenz |
|---|---|
| sicherer Einstieg | Strukturprüfung von `START-HIER.md` plus Linkprüfung |
| verbotene öffentliche Claims | Positivtest eines begrenzten Claims und Negativtests der vier Claim-Klassen |
| Human Gates | erlaubte lokale Aktion besteht; externe, unbekannte und reputationsrelevante Aktionen stoppen |
| geschützte Daten | korrekt markierte synthetische Eingabe besteht; fehlklassifizierte oder erkannte geschützte Eingabe stoppt |
| Herkunft und Lizenz | maschinenlesbares Inventar mit Quelle, Commit, Lizenz, Urheberhinweis, Nutzung und Notice; keine unregistrierten Fremdpfade |
| Repository-Hygiene | relative Links, Platzhalter, Nutzerpfade und typische Secrets werden geprüft |

## Claim-Tabelle

| Claim-Klasse | Öffentlich erlaubt | Prüferwartung |
|---|---:|---|
| lokaler, providerneutraler technischer Alpha-Starter | ja | PASS |
| DSGVO-konform | nein | STOP |
| State of the Art | nein | STOP |
| autonome Unternehmensführung | nein | STOP |
| garantierter Umsatz oder garantierte Wirkung | nein | STOP |

## Lizenzliste

- Eigenanteil: MoselMinds GmbH, MIT, siehe [`LICENSE`](../LICENSE).
- ICM/MWP: Commit `02ba5d85c7871b75c7c702a2d8da6524723d53d4`, MIT, Copyright (c) 2026 Model Workspace Protocol Contributors; keine fremden Dateien gebündelt, vollständiger Hinweis in [`NOTICE.md`](../NOTICE.md).

Die ausgeführten Befehle und Ergebnisse werden nach dem grünen Slice in [`RUN-STATE.md`](../RUN-STATE.md) festgehalten.
