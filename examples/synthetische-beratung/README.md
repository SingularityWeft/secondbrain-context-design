# Synthetischer E2E-Fall: Nordstern Beratung

Dieser Fall verbindet Setup, vier Basisskills und den Evidence-to-Artifact-Workflow vollständig offline. Alle Namen, Angebote, Aussagen und Quellen sind erfunden und mit `synthetic` gekennzeichnet.

Ausführen:

```bash
python3 scripts/run_e2e.py
```

Der Lauf arbeitet nur in einem temporären, getrennten Workspace und entfernt ihn anschließend. Er erzeugt und prüft diese Reihenfolge:

1. Workspace-Vertrag und sieben Arbeitsbereiche durch das bestätigte Setup.
2. `00-eingang/capture-demo.md` durch Capture und Routing.
3. `02-projekte/prozessklarheit-demo/PROJEKT.md` durch Projektstart.
4. `04-entscheidungen/toolwahl-demo.md` durch Entscheidungsdokumentation.
5. `05-reviews/2026-w37-demo.md` durch Wochenreview.
6. Providerneutrales lokales Kontext-Bundle mit User-Kontext, relativen Quellen und Hashes.
7. Stufen 1 bis 4 des Evidence-to-Artifact-Workflows.
8. Technischer Gate-Test, Stufe 5 und Stufe 6; keine menschliche Freigabe.
9. Setup-Zweitlauf mit bewahrter manueller Änderung, untracked Fremddatei und wiederhergestellter fehlender Template-Datei.

Erfolg bedeutet nur technische Reproduzierbarkeit mit synthetischen Daten. Fachliche Nützlichkeit, Anfänger-Verständlichkeit und öffentlicher Release bleiben eigene Human Gates.
