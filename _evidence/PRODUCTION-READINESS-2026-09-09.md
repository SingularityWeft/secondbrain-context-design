# Production Readiness Gate: öffentlicher Freebie-Kandidat

## Entscheidung

- Technischer Release-Kandidat: `GO`
- Öffentliche Alpha-Veröffentlichung: `GO` durch scopegebundene Owner-Freigabe
- Validierte Produktreife oder stärkere Wirkungs-/Datenschutzclaims: `NO-GO`, bis die unten genannten Human Gates echte Evidenz besitzen

## Bewertete Domänen

| Domäne | Status | Evidenz oder Grenze |
|---|---|---|
| Produkt und Korrektheit | technisch bereit | SPEC-00 bis SPEC-06, 73 Tests, fokussierte Negativfälle und synthetischer E2E-Lauf |
| Security und Privacy | technisch bereit mit dokumentierten Grenzen | S0-Public/S1-S2-Private-Trennung, S3-/Secret-Sperre, owner-only Rechte, externe Privacy-Denylist, Security-Review; rechtliche Datenschutzprüfung bleibt Human Gate |
| Daten und Migrationen | nicht anwendbar | Keine Datenbank, kein SaaS und keine Migration; lokale Dateien werden ohne Überschreiben erzeugt |
| Reliability und Betrieb | für lokalen Starter angemessen | Deterministischer Offline-Verify, Restart-Status und fail-closed Konflikte; kein gehosteter Dienst oder Hintergrundprozess |
| Performance und Kosten | nicht anwendbar | Keine Modell-, API-, Storage- oder Egress-Aufrufe durch das Repository |
| User Experience | Human Gate offen | Technische Setup- und Fehlerpfade sind dokumentiert; unabhängige Anfänger-Walkthroughs wurden nicht simuliert |
| Delivery und Supply Chain | technisch bereit | Standardbibliothek-only, gepinnter Checkout, MIT plus ICM-Herkunft, neue geschlossene Git-Historie und Fresh-Clone-Verify |
| KI-spezifisches Verhalten | begrenzt bereit | Providerneutrale Schnittstelle, explizite Includes, Quellen als untrusted data und Human Gates; Downstream-Modellverhalten und Claude-Desktop-Isolation bleiben ungeprüft |
| Launch Operations | Alpha-Push freigegeben | Initiales öffentliches GitHub-Freebie ist freigegeben; spätere Pushes, Deployments, automatische Distribution und stärkere Claims benötigen neue Freigabe |

## Offene Reife- und Claim-Gates

- unabhängige Anfänger-Walkthroughs und erforderliche Retests;
- technisch isolierter Claude-Desktop-Test;
- redaktionelle und rechtliche Prüfung von Name, Claims und Datenschutzgrenzen;
- rechtliche oder stärkere Datenschutz-, Qualitäts- und Wirkungsclaims sowie jeder spätere Außen-Write.

Diese Gates werden nicht durch Unit-Tests, synthetische Fixtures oder technische Dokumentation ersetzt.
