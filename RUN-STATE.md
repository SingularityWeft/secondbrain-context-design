# Run State

## Öffentlicher Release-Kandidat

- Stand: `public-alpha-approved`
- Historie: Das öffentliche Repository wird als neuer Root-Commit auf `main` erzeugt. Frühere Spec-Commits und Git-Objekte gehören ausschließlich in das private, owner-only Archiv.
- Konsolidierter Umfang: `SPEC-00` bis `SPEC-05` technisch vollständig; `SPEC-06` technisch vollständig, reale Human Gates nicht simuliert.
- Akzeptanzevidenz:
  - [`_evidence/SPEC-00.md`](_evidence/SPEC-00.md)
  - [`_evidence/SPEC-01.md`](_evidence/SPEC-01.md)
  - [`_evidence/SPEC-02.md`](_evidence/SPEC-02.md)
  - [`_evidence/SPEC-03.md`](_evidence/SPEC-03.md)
  - [`_evidence/SPEC-04.md`](_evidence/SPEC-04.md)
  - [`_evidence/SPEC-05.md`](_evidence/SPEC-05.md)
  - [`_evidence/SPEC-06.md`](_evidence/SPEC-06.md)
  - [`_evidence/PUBLIC-RESET-2026-09-09.md`](_evidence/PUBLIC-RESET-2026-09-09.md)
  - [`_evidence/PRODUCTION-READINESS-2026-09-09.md`](_evidence/PRODUCTION-READINESS-2026-09-09.md)
- Geliefert: ausschließlich synthetischer Public Starter; separate lokale S1-/S2-Instanzen; expliziter User-Kontext; providerneutrale, begrenzte Agent-Kontextpakete; keine Datenbank, kein SaaS, keine Connectoren und keine automatische Übertragung.
- Technische Prüfungen: Repository-, Skill-, Pilot-, Policy-, Lizenz-, Claim-, Secret-, Pfad-, Platzhalter- und Git-Objekt-Verträge; 73 Unit-/Vertragstests; synthetischer E2E-Lauf; frischer lokaler Clone.
- Behobener Security-Befund: Keine personenspezifischen Namen oder davon abgeleitete Hash-Fingerprints werden im öffentlichen Starter gespeichert. Release-spezifische Begriffe können nur über eine externe owner-only Denylist geprüft werden.
- Bekannte Grenzen: Dateirechte isolieren keine Prozesse desselben OS-Users; Datenklassifizierung und Regex-Scans sind keine semantische Garantie; Backup, Verschlüsselung, Sync sowie Aufbewahrung und Training durch externe Modelle bleiben User- und Anbieterentscheidungen.
- Erteilte Human Gates: Veröffentlichung dieses begrenzten Alpha-Stands als öffentliches GitHub-Freebie und initialer Push an `SingularityWeft/secondbrain-context-design`.
- Weiterhin offene Gates: unabhängige Anfänger-Walkthroughs, technisch isolierter Claude-Desktop-Test sowie rechtliche oder stärkere Claim-/Datenschutzaussagen. Jeder spätere Push, Deploy oder externe Daten-Handoff benötigt eine neue konkrete Freigabe.
- Nächster Schritt: Kontakte zum zweistufigen Test einladen – zuerst synthetischer Technikcheck, danach getrennte private Instanz für einen echten, überschaubaren Anwendungsfall. Nur bereinigte Befunde gelangen in Issues, Pull Requests oder öffentliche Evidenz.
