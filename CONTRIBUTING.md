# Bereinigtes Feedback und Beiträge

Danke, dass du Erfahrungen aus dem SecondBrain Context Design Starter zurückgibst. Claude, Codex, Grok oder ein anderer Coding-Agent darf bei Diagnose, lokalem Fix und Vorbereitung helfen. Veröffentlicht wird ausschließlich nach bewusster menschlicher Prüfung.

## Erst lokal lösen

1. Lass den Agenten das Problem in deiner privaten Instanz diagnostizieren, ohne private Inhalte nach außen zu übertragen.
2. Prüfe, ob die Ursache allgemein im Starter liegt oder nur deine Maschine, deinen Account, deinen Anbieter beziehungsweise deine private Konfiguration betrifft.
3. Entferne echte Unternehmens-, Kunden- und Personendaten, interne Dokumente, Secrets, persönliche Dateipfade und vollständige Logs aus jeder öffentlichen Reproduktion.

Wenn lokale Unterstützung nicht ausreicht, kannst du dich über den bereits vereinbarten Kontaktweg bei der Maintainerin melden. Sensible Inhalte gehören nie in ein öffentliches GitHub-Issue.

## Issue oder Pull Request?

| Befund | Rückkanal |
|---|---|
| Installation, unklare Anleitung oder reproduzierbarer Fehler ohne fertigen Fix | [bereinigtes GitHub-Issue](https://github.com/SingularityWeft/secondbrain-context-design/issues/new?template=praxistest.yml) |
| Allgemeingültiger kleiner Fix an Dokumentation, Setup oder Tests | Fork, eigener Branch und Pull Request gegen `main` |
| Rein lokale Konfiguration ohne wiederverwendbare Repo-Änderung | lokalen Workaround dokumentieren, kein künstlicher Pull Request |
| Schwachstelle, Secret oder möglicher Datenabfluss | Lauf stoppen und den privaten Weg aus [SECURITY.md](SECURITY.md) verwenden |

## Sicherer Agenten-Workflow

1. Ermittle den getesteten Base-SHA und reproduziere das Problem mit synthetischen oder vollständig bereinigten Angaben.
2. Ändere nur die kleinste allgemein nützliche Fläche. Private Instanzdateien werden niemals in den öffentlichen Clone kopiert.
3. Führe `git diff --check` und `bash scripts/verify-repo.sh` aus.
4. Prüfe Branch, Commit-Autor, Diffstat und vollständigen öffentlichen Diff auf private Inhalte und persönliche Pfade.
5. Verwende einen Fork unter deiner eigenen GitHub-Identität. Frage nie nach Maintainer-Credentials oder Tokens.
6. Zeige vor dem Push Ziel-Remote, Branch und Diff. Push und das Öffnen des Pull Requests brauchen jeweils deine separate Freigabe.
7. Warte die GitHub-CI ab. Nur die Maintainerin entscheidet über Merge, Überarbeitung oder Ablehnung; kein Auto-Merge und kein automatischer Release.

## Inhalt eines guten Issues

- allgemeine, bereinigte Beschreibung;
- erwartetes und tatsächliches Verhalten;
- minimale Reproduktionsschritte mit synthetischen Werten;
- Betriebssystemfamilie, Architektur und relevante Toolversionen, soweit wirklich nötig;
- bereinigter kurzer Logauszug;
- bereits versuchte lokale Lösung;
- Angabe, ob und wobei ein KI-Agent unterstützt hat.

## Inhalt eines guten Pull Requests

- Problem und allgemein nutzbare Root Cause;
- Base-SHA und Test-SHA;
- kleinster Fix und bekannte Grenzen;
- ausgeführte Tests;
- Bestätigung, dass Diff, Commit und PR-Text keine privaten Inhalte enthalten;
- kurze Offenlegung der KI-Unterstützung.

Ein grüner Check ist notwendig, aber keine automatische Annahme. Der öffentliche Patch bleibt überprüfbar und darf keine private Praxisevidenz imitieren.
