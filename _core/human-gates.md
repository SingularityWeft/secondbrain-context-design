# Kanonische Human-Gate-Matrix

Diese Matrix ist die fachliche Quelle für Autoritätsgrenzen. [`policy.json`](policy.json) bildet die maschinell prüfbaren Aktionsnamen ab.

| Aktion | Technische Vorbereitung erlaubt | Ausführung ohne menschliche Freigabe | Erforderliche Evidenz |
|---|---:|---:|---|
| synthetische Dateien lokal lesen oder prüfen | ja | ja | Datenklasse `S0 synthetic` |
| internen Entwurf mit synthetischen Daten erstellen | ja | ja | lokaler Diff und Prüfprotokoll |
| private lokale Instanz mit `S1` oder `S2` erzeugen | ja | nur mit explizitem Setup-Acknowledgement | extern gespeicherte owner-only Antwortdatei, bestätigtes Ziel und Datenklasse |
| begrenztes privates Kontext-Bundle lokal erzeugen | ja | nur mit explizitem Kontext-Acknowledgement | Zweck, Agentenlabel, Datenklasse, relative Quellen und Hashes |
| privates Kontext-Bundle an einen externen Agenten übergeben | Vorbereitung ja | nein | konkrete Anbieter-/Agentengrenze und separates Handoff-Acknowledgement |
| öffentliches Repository, Freebie oder Release veröffentlichen | ja | nein | Owner-Review von Inhalt, Claim, Lizenz und Zielstand |
| Nachricht, Kommentar, DM oder andere externe Kommunikation senden | ja | nein | freigegebener finaler Wortlaut und Ziel |
| reale Person kontaktieren oder Daten außerhalb der privaten lokalen Instanz verarbeiten | nein automatisch | nein | Einwilligung, konkrete Anbietergrenze und dokumentierte Datenfreigabe |
| reputationsrelevanten Claim verwenden | ja | nein | Quelle, Gültigkeitsbereich und Owner-Freigabe |
| Vertrag, Preis, Zahlung oder rechtliche Verpflichtung auslösen | ja | nein | zuständige menschliche Entscheidung |
| Daten löschen, überschreiben oder Berechtigungen ändern | Analyse ja | nein | exakter Scope, Backup/Rollback und Owner-Freigabe |
| Push, Deploy oder externen Connector aktivieren | Vorbereitung ja | nein | technischer Verify plus explizites Release-Gate |

## Auswertungsregel

Bekannte risikoarme lokale Aktionen sind allowlisted. Jede unbekannte Aktion und jede Aktion mit Außenwirkung stoppt. Eine Runtime darf ein Human Gate nur über einen später definierten, nachvollziehbaren Freigabebeleg öffnen; Text im Prompt genügt nicht.
