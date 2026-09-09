# Start hier

## Zweck

Dieser Starter soll jedem interessierten User einer Solo-Beratung einen eigenen, dateibasierten Arbeitsraum geben, in dem User- und Unternehmenskontext, wiederholbare Abläufe, Prüfungen und Freigaben nachvollziehbar bleiben. Er bindet keinen KI-Anbieter und überträgt von selbst nichts nach außen.

## Erwartetes Ergebnis

Nach dem technischen Alpha-Aufbau existiert ein lokal prüfbarer Workspace mit synthetischem Beispiel, klaren Datenklassen, begrenzten Skills, einem Beratungsworkflow und einem reproduzierbaren Verify-Einstieg. Dieser erste Slice liefert zunächst nur den Produkt-, Lizenz- und Sicherheitsvertrag.

## Datenverbote im öffentlichen Starter

Verwende ausschließlich frei erfundene Inhalte. Nicht eingeben, kopieren oder importieren:

- Namen, Kontaktdaten oder andere personenbezogene Daten realer Menschen;
- echte Kundenunterlagen, Verträge, Angebote, Gesprächsnotizen oder Zugangsdaten;
- Gesundheits-, Finanz-, Rechts- oder Beschäftigtendaten;
- interne SecondBrain-Inhalte oder private Instanzdateien;
- Schlüssel, Tokens, Passwörter oder sonstige Secrets.

Diese Verbote gelten zwingend für das öffentliche Repository, seine Git-Historie, Beispiele und Tests. Eine reale private Instanz wird ausschließlich außerhalb des Repos aus einer owner-only Antwortdatei erzeugt. `S3 restricted` und Secrets bleiben auch dort verboten. Wenn Herkunft oder Schutzbedarf unklar sind, gilt die Eingabe als gesperrt. Die vollständige Klassifikation steht in [_core/data-policy.md](_core/data-policy.md).

## Erste sichere Aktion

Ohne Installation und ohne eigene Daten aus dem Repository-Root ausführen:

```bash
bash scripts/verify-spec-00.sh
```

Erwartet wird `SPEC-00 VERIFY PASS`. Der Befehl liest nur Repository-Dateien und temporär erzeugte synthetische Testdaten. Er führt keine Netzwerk- oder externen Schreibaktionen aus.

Danach die [Human-Gate-Matrix](_core/human-gates.md) lesen. Die Veröffentlichung dieses Alpha-Starters erlaubt keine automatischen Kundenkontakte oder Agentenübertragungen; private Setups, externe Handoffs und jeder spätere Release benötigen weiterhin eigene bewusste Bestätigungen.
