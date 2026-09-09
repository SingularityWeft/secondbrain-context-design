# Akzeptanzevidenz SPEC-05

Status: `passed-technical`

## Erforderliche Evidenz

| Vertrag | Positive Evidenz | Kontrollierter Negativfall |
|---|---|---|
| Ein kanonischer Offline-Verify prüft alle Repository-Gates | `bash scripts/verify-repo.sh` endet im aktuellen Tree und im frischen Clone mit Exit 0 | Jede Gate-Mutation endet ungleich 0 und nennt den Pfad |
| Setup, vier Skills und Workflow funktionieren zusammen | `python3 scripts/run_e2e.py` erzeugt die dokumentierte Artefaktfolge | Fehlende oder abweichende Artefakte stoppen den Lauf |
| Ein Setup-Zweitlauf bewahrt manuelle und fremde Dateien | Vorher-/Nachher-Hashes und Git-Index sind gleich; Status enthält nur erwartete Arbeitsbaumänderungen | Manipulierter Starter-Output wird als Konflikt gemeldet und nicht überschrieben |
| CI ist minimal und ohne Produktabhängigkeiten | Workflow hat nur Leserechte, gepinntes Checkout und ruft den kanonischen Verify auf | Secret-, Modell-, Connector- oder Netzwerkabhängigkeit im Workflow wird abgewiesen |
| Anfänger-Test wird ehrlich erfasst | Aufgabenpaket und Ergebnisformular unterscheiden „ohne Hilfe“, „mit Hilfe“ und „abgebrochen“ | Ohne reale Testperson bleibt das Gate `blocked` |

## Erwartete Prüfungen

- Struktur-, Markdown-Link-, Marker-, Secret-, persönlicher Pfad-, Claim-, Lizenz- und Policy-Scan.
- Alle Offline-Unit- und Vertragstests aus SPEC-00 bis SPEC-05.
- Synthetischer E2E-Lauf einschließlich Setup-Zweitlauf.
- Sechs isolierte Fail-Closed-Mutationen.
- `git diff --check` und später Fresh-Clone-Verify auf dem freigegebenen SHA.

## Daten- und Gate-Grenzen

- Ausschließlich die erfundene Nordstern-Beratung wird verwendet.
- Technische Decision-Fixtures zählen nicht als menschliche Freigabe.
- Gehostete CI, Anfänger-Walkthrough, Push und Release werden nicht ausgeführt.

## Technischer Lauf 2026-09-08

- Umgebung: Darwin 25.6.0 arm64; Python 3.14.4; git 2.50.1 (Apple Git-155).
- `bash scripts/verify-repo.sh` — PASS; 44 Tests, Repository- und Skill-Vertrag sowie Diff-Checks.
- `python3 scripts/run_e2e.py` — PASS; zwölf geordnete Artefakte, alle Hashes vor/nach Zweitlauf identisch, Git-Index unverändert.
- Erwarteter Arbeitsbaum nach Zweitlauf: nur manuell geänderte `01-ausrichtung/business-context.md` und untracked `00-eingang/fremde-synthetische-notiz.md`.
- Sechs isolierte Negativmutationen — PASS; gebrochener Link, offener Marker, typisches Secret, persönlicher Pfad, verbotener Claim und fehlendes `NOTICE.md` stoppten jeweils mit Pfadangabe.
- CI-Konfiguration wurde statisch geprüft, aber nicht ausgelöst; gehostete CI bleibt ein öffentliches Release-Gate.
- Fresh-Clone: `git clone --no-hardlinks …`, Checkout `8127b98e3f43985c013cc1c61757351b9a369a41`, danach `bash scripts/verify-repo.sh` — PASS mit leerem `git status --porcelain=v1`.

## Ergebnis

SPEC-05 ist für den technischen, synthetischen Alpha-Scope grün. Der echte unabhängige Anfänger-Walkthrough und eine gehostete CI-Ausführung sind nicht durch technische Fixtures ersetzbar und bleiben blockiert.
