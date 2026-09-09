# Fix- und Retest-Protokoll

Ein Befund der Klasse `release-blocker` sperrt den privaten Rollout des betroffenen Auftrags und jeden öffentlichen Release, bis ein vollständiger unabhängiger Retest grün ist.

## Fix-Evidenz

- Befund-ID:
- reproduziert auf altem SHA:
- kleinste behobene Ursache:
- Fix-Commit mit neuem vollständigem SHA:
- fokussierte positive und negative Tests:
- Diff-Review:

## Unabhängiger Retest von vorn

- unbeteiligte Testperson:
- Bestätigung: weder ursprüngliche Implementierung noch vorherige Durchführung
- frischer Clone des neuen SHA:
- gesamter betroffener Testauftrag, nicht nur der korrigierte Einzelschritt:
- Start-/Endzeit:
- Hilfe mit Anlass und Umfang:
- Artefaktpfade und Hashes:
- Ergebnis: bestanden / mit Befund / abgebrochen / nicht ausgeführt

Ein Teil-Retest, ein Lauf auf dem alten SHA, eine beteiligte Person oder eine technische Fixture schließt den Release-Blocker nicht.
