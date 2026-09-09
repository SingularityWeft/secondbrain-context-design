# Akzeptanzevidenz SPEC-06

Status: `passed-technical; pilot-gates-partially-blocked; public-alpha-approved`

## Erforderliche technische Evidenz

| Vertrag | Positive Evidenz | Kontrollierter Negativfall |
|---|---|---|
| Einladung, Testauftrag und Pilotvereinbarung sind getrennt und vollständig | Statischer Vertragscheck findet Aufwand, Unentgeltlichkeit, Dank, Ablehnung, Abbruch, Nichtüberredung und Supportgrenze | Entfernte Pflichtaussage stoppt mit Dokumentpfad |
| Einwilligung und Datengrenzen sind explizit | Formular trennt Primärtest, private Pilotphase, Feedbacknutzung, Namensnennung und Widerruf | Ein Gate ohne Evidenzreferenz kann nicht auf grün gesetzt werden |
| Lauf und Hilfe sind ehrlich protokollierbar | Formular enthält SHA, Zeit, Weg, Hilfe, Artefakte, Blocker, Frictions und Fragen | Leere reale Evidenz bleibt `blocked` |
| Befunde sind triagierbar | Registerschema erzwingt Reproduktion, Evidenz und exakt eine erlaubte Klasse | Unvollständiger synthetischer Befund wird abgewiesen |
| Release-Blocker lösen einen unabhängigen Voll-Retest aus | Retestvertrag verlangt unbeteiligte Person, neuen SHA und vollständigen betroffenen Auftrag | Teil-Retest oder gleiche beteiligte Person reicht nicht |
| Öffentliche Evidenz ist anonymisiert | Kandidat wird auf Namen, Kontakte, Pfade, Secrets, private Inhalte und Claims geprüft | Jede geschützte Mutation stoppt mit Pfad |
| Öffentliche Entscheidung ist fail-closed | Maschineller Gate-Status und Tabelle ergeben `NO-GO`, solange ein Pflichtgate blockiert ist | Erzwungenes GO ohne vollständige Evidenz stoppt |

## Nicht durch technische Tests ersetzbar

- Entscheidung und Primärlauf der eingeladenen Testperson.
- Unabhängige Anfänger-Walkthroughs und Retests.
- Technisch isolierter Claude-Desktop-Test.
- Die Freigabe des Owners für das begrenzte öffentliche Alpha-Freebie und seinen initialen Push ist in [`PUBLICATION-APPROVAL-2026-09-09.md`](PUBLICATION-APPROVAL-2026-09-09.md) belegt. Stärkere Claims und rechtliche Datenschutzbewertungen bleiben offen.

## Technischer Lauf 2026-09-08

- Umgebung: Darwin 25.6.0 arm64; Python 3.14.4; git 2.50.1 (Apple Git-155).
- `python3 -m unittest tests.test_spec_06` — PASS; neun Testmethoden mit positiven Verträgen und dreizehn isolierten Negativmutationen.
- `python3 scripts/check_pilot.py` — PASS; sieben Gates, leeres reales Befundregister und eine klar markierte technische Befund-Fixture.
- `bash scripts/verify-repo.sh` — PASS; 53 Tests sowie Repository-, Skill-, Pilot- und Diff-Verträge.
- Öffentliche Evidenzmutationen für Namen, E-Mail, Telefon, persönlichen Pfad, Secret, Private-Content-Markierung, unnötiges Umgebungsdetail und verbotenen Claim stoppten jeweils mit Pfadangabe.
- Kein Human Test, keine Unterschrift, keine private Instanz, kein Claude-Desktop-Isolationstest und keine externe Aktion wurden ausgeführt oder simuliert.

## Bekannte technische Grenze

Der Scanner erkennt definierte Identitäts-, Kontakt-, Pfad-, Secret- und Claim-Muster. Ob frei formulierter Text indirekt private Business-Inhalte offenbart, braucht zusätzlich menschlichen Owner-Review; die Metadatenprüfung allein ist kein Datenschutzbeweis.

## Fresh-Clone-Nachweis

- `git clone --no-hardlinks …`, Checkout `31a3c40eb11f4fed6b35082471e5cff4dc332cf4`, danach `bash scripts/verify-repo.sh` — PASS mit 53 Tests.
- `git status --porcelain=v1` im frischen Clone — leer.
- Technisches Ergebnis: SPEC-06 ist grün; der öffentliche Alpha-Code-Release ist scopegebunden freigegeben. Primärlauf, unabhängige Walkthroughs, Desktop-Isolation und weitergehende Reife-/Claim-Gates bleiben `blocked`.
