# Kanonische Datenrichtlinie

Diese Datei ist die fachliche Quelle für Datenklassen. Die maschinenlesbare Spiegelung in [`policy.json`](policy.json) darf keine schwächere Regel enthalten.

## Datenklassen

| Klasse | Bedeutung | Beispiele | Alpha-Starter |
|---|---|---|---|
| `S0 synthetic` | vollständig erfunden, keiner realen Person oder Organisation zuordenbar | Fantasieunternehmen, erfundene Leistungen, reservierte Beispieldomains | im Public Repo und in Beispielinstanzen erlaubt |
| `S1 internal` | interne, nicht öffentliche Betriebsinformation ohne Personendaten | echte Strategie, interne Kennzahlen, unveröffentlichte Prozesse | nur in ausdrücklich bestätigter privater Instanz außerhalb des Repos |
| `S2 confidential` | Kunden-, Vertrags-, Kommunikations- oder personenbezogene Daten | Angebote, Transkripte, Kontaktdaten, Kundenfeedback | nur in ausdrücklich bestätigter privater Instanz; Agenten-Handoff separat bestätigen |
| `S3 restricted` | Secrets oder besonders geschützte beziehungsweise folgenreiche Daten | Zugangsdaten, Gesundheits-, Finanz-, Rechts- oder Beschäftigtendaten | immer gesperrt |

## Fail-closed-Regeln

1. Der öffentliche Starter, alle versionierten Fixtures und technische Tests enthalten nur `S0 synthetic`.
2. `S1 internal` und `S2 confidential` dürfen nur aus einer owner-only Antwortdatei außerhalb des Repos in eine getrennte private Instanz geschrieben werden; `apply` verlangt eine ausdrückliche Bestätigung.
3. Erkannte Secret-, Konto-, Credential- oder `S3`-Muster stoppen auch bei anderer Kennzeichnung.
4. Direkte Identitätsmerkmale in einem `S2`-Agenten-Bundle benötigen eine zusätzliche ausdrückliche Freigabe; `S1` darf sie nicht enthalten.
5. Fehlende oder widersprüchliche Kennzeichnung stoppt die Verarbeitung; unklare Herkunft wird mindestens als `S2 confidential` behandelt.
6. Der öffentliche Starter enthält keine private Instanz und liest keine SecondBrain-, Home- oder Nachbarverzeichnisse.
7. Unbeschränkter Agentenzugriff auf eine private Instanz ist gesperrt. Kontext-Bundle-Erzeugung ist eine lokale Schreibaktion; eine spätere Übergabe an einen Agenten ist ein eigenes Human Gate und wird vom Builder nicht ausgeführt.

## Freigabegrenze

Der Setup-Pfad stellt owner-only Dateirechte und Public/private-Trennung her, aber weder Backup noch Verschlüsselung oder Prozessisolation. Vor `S2`-Nutzung müssen der Workspace-Owner und der konkrete Agentenweg Aufbewahrung, Löschung, Zugriff, Synchronisation und Anbietergrenze bewusst entscheiden. Lokale Speicherung beweist keine lokale Modellverarbeitung.
