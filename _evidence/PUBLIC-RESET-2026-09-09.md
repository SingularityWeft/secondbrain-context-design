# Akzeptanzvertrag: sauberes Public Freebie mit privater Instanz

Status: `technical-pass; public-alpha-approved`

## Ziel

Der veröffentlichungsfähige Starter besitzt eine neue, entpersonalisierte Git-Historie. Er enthält nur synthetische Beispiele, kann aber außerhalb des Repositorys eine owner-only private Instanz für `S1 internal` oder `S2 confidential` erzeugen und daraus bewusst begrenzte lokale Agenten-Kontext-Bundles erstellen.

## Akzeptanzevidenz

| Vertrag | Positive Evidenz | Kontrollierter Negativfall |
|---|---|---|
| Saubere öffentliche Historie | Neuer Root-Commit auf `main`; private Denylist prüft Arbeitsbaum und alle gespeicherten Git-Objekte | Ein privater Suchbegriff im Tree oder Commit stoppt den Verify mit Pfad beziehungsweise Objekt-ID |
| Recoverable Reset | Alter Repositoryzustand liegt in einem owner-only privaten Archiv außerhalb des Public Repo | Archivziel mit Gruppen-/Fremdzugriff oder bestehendem Konflikt stoppt |
| Public/private-Trennung | Starter und Tests enthalten nur synthetische Werte; reale Antwortdateien innerhalb des Repos werden abgewiesen | Private Antwortdatei im Starter, breites Ziel oder fehlende Apply-Bestätigung stoppt vor Schreiben |
| Private lokale Instanz | `plan` zeigt Datenklasse und Warnungen; `apply --acknowledge-private-data` erzeugt `S1`/`S2` außerhalb des Repos mit Ordner `0700`, Dateien `0600` und ohne Git/Netzwerk | `S3`, Secret-Muster, widersprüchliche Kennzeichnung und falscher Token stoppen fail-closed |
| Providerneutraler Agenten-Handoff | Private Bundles enthalten Zweck, frei gewähltes Agentenlabel, Handoff-Modus, Quellen und Hashes; der Builder überträgt nichts | Fehlende Private-Bestätigung, fehlender Zweck/Agent, nicht bestätigter externer Handoff, Traversal, Symlink oder bestehendes Ziel stoppt |
| Quellen sind Daten | Bundle und Agentenvertrag kennzeichnen eingebettete Quellen als untrusted data, die Policy und Human Gates nicht überschreiben | Vertragstest stoppt, wenn diese Grenze fehlt |
| Release-Kandidat reproduzierbar | Vollverify im neuen Repo und in einem frischen lokalen Clone des finalen Root-Commits | Kein Test, Claim-, Lizenz-, Secret- oder Platzhalterscan wird abgeschwächt |

## Veröffentlichungsgrenze

Die scopegebundene Owner-Freigabe für das öffentliche Alpha-Freebie und seinen initialen GitHub-Push ist separat dokumentiert. Sie ist keine Freigabe für Deployments, automatische Distribution, externe Datenübertragung oder stärkere reputationsrelevante Claims.

## Erbrachte technische Evidenz

- Der vorherige Repositoryzustand wird vollständig und wiederherstellbar in einem owner-only Archiv außerhalb des öffentlichen Repositories gehalten.
- Das Public Repo besitzt genau einen neuen Root-Commit auf `main`; alte oder nicht erreichbare Git-Objekte führen zum Abbruch.
- Die externe private Denylist ist weder als Klartext noch als Hash Bestandteil des Repositories. Repo-interne, verlinkte oder zu breit lesbare Denylists werden abgelehnt.
- S1-/S2-Setup und private Agent-Kontextpakete verlangen getrennte Bestätigungen; S3, Secrets, Traversal, Symlinks, Überschreiben und automatische externe Übertragung bleiben gesperrt.
- Der vollständige Verify läuft sowohl im finalen Arbeitsbaum als auch in einem frischen lokalen Clone.
