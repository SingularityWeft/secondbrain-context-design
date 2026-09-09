# Akzeptanzvertrag: entpersonalisierter, providerneutraler Agent-Kontext

Status: `passed; included-in-public-root`

## Ziel

Der öffentliche Starter enthält keine Identität aus dem privaten Pilot- oder Owner-Kontext. Lizenz- und Herkunftshinweise bleiben korrekt erhalten. Eine erzeugte lokale Instanz besitzt einen expliziten User-Kontext und kann für jeden dateifähigen Agenten ein begrenztes, prüfbares Kontext-Bundle erzeugen, ohne einen Anbieter aufzurufen oder Daten selbst zu übertragen.

## Erforderliche Evidenz

| Vertrag | Positive Evidenz | Kontrollierter Negativfall |
|---|---|---|
| Öffentlicher Tree ist entpersonalisiert | Repositoryscan mit externer owner-only Denylist findet weder private Begriffe noch gespeicherte Fingerprints | Wiedereinführung eines privaten Suchbegriffs stoppt mit Pfad |
| Produktlogik ist providerneutral | `_core/`, `CONTEXT.md` und `AGENT-INTERFACE.md` definieren den Vertrag; Runtime-Dateien bleiben optionale Adapter | Tests stoppen bei adaptergebundener kanonischer Logik |
| Workspace versteht den User explizit | Setup erzeugt `01-ausrichtung/user-context.md` aus Zielen, Arbeitsstil, Kommunikation, Kapazität und Unterstützungspräferenzen | Fehlende Felder oder offene Marker stoppen vor dem Schreiben |
| Agenten erhalten nur begrenzten Kontext | Lokaler Bundle-Builder nimmt eine Aufgabe und explizite relative Includes, dokumentiert Pfad und SHA-256 und schreibt ausschließlich lokal | Traversal, Symlink, geschützte Daten, fremdes Ziel und bestehende Ausgabedatei stoppen fail-closed |
| Keine versteckte Anbieterabhängigkeit | Bundle-Builder nutzt nur die Python-Standardbibliothek und keine Netzwerk- oder Modellaufrufe | Statischer Vertrag weist Netzwerk-/SDK-Abhängigkeiten ab |
| Sichere Alpha-Grenze bleibt erhalten | Das öffentliche Repo bleibt `S0 synthetic`; reale S1-/S2-Daten sind nur in einer getrennten owner-only Instanz und mit eigenen Bestätigungen erlaubt | S3, Secrets und falsch etikettierte Merkmale stoppen vor Ausgabe |

## Handoff-Grenze

Der entpersonalisierte Tree wird als neue öffentliche Git-Historie initialisiert. Der vorherige Zustand bleibt ausschließlich in einem privaten, owner-only Archiv erhalten.

## Erbrachte Evidenz

- Arbeitsbaum und Git-Objekte enthalten weder private Namen noch davon abgeleitete feste Fingerprints; ein kontrolliertes Wiedereinführen über die externe private Denylist stoppt den Verify.
- Setup und Kontext-Bundle bilden Ziele, Arbeitsstil, Kommunikation, Kapazitätsgrenzen und Unterstützungspräferenzen aus rein synthetischen Antworten ab.
- Der Bundle-Builder schreibt deterministisch und exklusiv unter `05-reviews/agent-context/`, dokumentiert relative Quellen samt SHA-256 und ruft weder Provider noch Netzwerk auf.
- Traversal, Symlinks, bestehende Ziele, unzulässige Datenklassen, erkannte Secrets und ungültige Zeitangaben stoppen vor einer Ausgabe.
- Der skeptische Security-Diff-Review deckte zwölf sicherheitsrelevante Änderungsflächen ab, fand einen niedrigen Privacy-Befund zu festen Identitäts-Hashes und führte zur Entfernung dieser Fingerprints. Regex-Erkennung, Prozesse desselben OS-Users und Downstream-Agent-Verhalten bleiben dokumentierte Grenzen.
