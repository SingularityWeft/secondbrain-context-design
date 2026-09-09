# Pilotpaket

Dieses Paket bereitet einen fair begrenzten, synthetischen Primärlauf vor. Es dokumentiert keine erfolgte Zustimmung, keinen realen Test und keine Freigabe.

Die Dokumente werden in dieser Reihenfolge verwendet:

1. [Testeinladung](01-testeinladung.md) – freiwillige Entscheidung vor jedem Auftrag.
2. [Technischer Testauftrag](02-technischer-testauftrag.md) – neutraler Einstieg ohne vorweggenommene Hilfe.
3. [Pilotvereinbarung](03-pilotvereinbarung.md) – Umfang, Dank und Supportgrenze getrennt vom Testergebnis.
4. [Einwilligung und Datenschutz](04-einwilligung-und-datenschutz.md) – einzelne, widerrufbare Entscheidungen.
5. [Laufprotokoll](05-laufprotokoll.md) – Weg, Zeit, Hilfe, Artefakte und Beobachtungen.
6. [Befundregister](befundregister.json) – strukturierte Triage.
7. [Retest-Protokoll](07-retest-protokoll.md) – vollständiger unabhängiger Neustart nach Release-Blockern.
8. [GO/NO-GO](08-go-no-go.md) – private Pilotphase und öffentlicher Freebie-Release als getrennte Gates.

Der maschinenlesbare [Gate-Status](gate-status.json) bleibt fail-closed. `python3 scripts/check_pilot.py` prüft nur die technische Vollständigkeit, niemals die Authentizität einer Unterschrift oder eines Human Tests.
