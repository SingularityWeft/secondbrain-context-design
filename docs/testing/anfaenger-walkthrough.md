# Unabhängiger Anfänger-Walkthrough

Status: `blocked – reale unabhängige Testperson fehlt`

Dieser Test darf nicht durch die implementierende Person oder eine KI als bestanden markiert werden. Er besteht aus einem synthetischen Technikcheck und – nach eigener separater Zustimmung – einem begrenzten echten Praxistest in einer privaten Instanz außerhalb des öffentlichen Clones.

## Phase 1 – synthetischer Technikcheck

1. Öffne `START-HIER.md` und erkläre in eigenen Worten Datenklasse und Grenzen.
2. Führe den Setup-Plan für einen neuen temporären Zielordner aus.
3. Prüfe Ziel, Dateiliste und Bestätigungstoken, bevor du `apply` ausführst.
4. Öffne `STATUS.md` in der erzeugten Instanz und nenne die nächste sichere Aktion.
5. Führe den Capture-Skill mit der synthetischen Fixture aus.
6. Wiederhole das Setup nach einer eigenen Änderung an `01-ausrichtung/business-context.md`.
7. Erkläre, welche Datei bewahrt, welche wiederhergestellt und welche Aktion bewusst nicht automatisch ausgeführt wurde.

## Phase 2 – privater Praxistest

1. Wähle einen einzigen echten, überschaubaren Arbeitsfall und entscheide, welche Informationen dafür wirklich erforderlich sind.
2. Prüfe bewusst, ob der gewählte Claude-, Codex-, Grok- oder andere Agent diese Daten sehen darf. Verwende keine Secrets oder `S3 restricted`-Daten.
3. Lass außerhalb des Clones eine owner-only private Instanz als `internal` oder `confidential` planen. Prüfe Ziel, Dateiliste, Warnungen und Bestätigungstoken vor `apply`.
4. Bearbeite den Anwendungsfall nur in dieser privaten Instanz und nur mit freigegebenen Pfaden oder einem begrenzten Kontext-Bundle.
5. Bewerte Verständlichkeit, praktischen Nutzen und jede Stelle, an der du oder dein Agent Unterstützung benötigt habt.
6. Gib ausschließlich bereinigte Beobachtungen zurück. Allgemeingültige Verbesserungen können nach [`CONTRIBUTING.md`](../../CONTRIBUTING.md) als Issue oder Pull Request vorgeschlagen werden.

Die beobachtende Person hilft nicht ungefragt. Sobald Hilfe nötig ist, werden Anlass, Umfang und Wirkung im [Ergebnisformular](ergebnisformular.md) notiert. Der Lauf erhält dann nicht das Ergebnis „ohne Hilfe“.

## Abbruchregeln

- Echte Informationen erscheinen im öffentlichen Clone, Git-Diff, Issue, Pull Request oder geteilten Log.
- Die Testperson soll einen Push, Connector, Versand oder Release ausführen.
- Ein Zielpfad oder eine Wirkung ist unklar und könnte fremde Daten verändern.
- Der Agent soll auf mehr private Dateien zugreifen als für den gewählten Anwendungsfall freigegeben wurden.

Ein Abbruch ist ein valider Befund und kein Testversagen der Person.
