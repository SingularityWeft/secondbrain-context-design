# Setup einer lokalen Instanz

## Voraussetzungen

- SPEC-01-Verify ist grün.
- Das Ziel ist ein neuer oder leerer lokaler Ordner außerhalb dieses Starter-Repositories.
- Für den Beispielweg sind alle Antworten frei erfunden und entsprechen [`synthetic-answers.json`](../setup/synthetic-answers.json).
- Eine private Antwortdatei liegt außerhalb dieses Repos, gehört nur dem User und hat Dateirechte `0600`.
- Backup, Verschlüsselung und Synchronisation werden nicht automatisch eingerichtet; `S3 restricted` und Secrets bleiben gesperrt.

Der empfohlene Praxistest hat zwei Phasen: Zuerst wird der folgende synthetische Beispielweg vollständig abgeschlossen. Erst danach entscheidet der User separat über einen einzigen echten Anwendungsfall, die private Datenklasse und den Agenten beziehungsweise Anbieter, der ausgewählte Informationen sehen darf.

## 1. Geplante Pfade prüfen

```bash
python3 scripts/setup_workspace.py plan --answers setup/synthetic-answers.json --target /private/tmp/clief-demo-instanz
```

Die Ausgabe nennt ausschließlich geplante relative Dateien, das normalisierte Ziel und einen `confirmation_token`. Der Plan schreibt nichts.

## 2. Exaktes Ziel bestätigen und anwenden

Den im eigenen Plan ausgegebenen 64-stelligen Wert kopieren und beim `apply`-Aufruf direkt hinter die Option `--confirm-token` setzen. Ziel und Antwortdatei müssen exakt dieselben sein wie beim angezeigten Plan.

Der Beispielpfad ist nur für synthetische Tests. Das Script lehnt das Starter-Repository, das Home-Verzeichnis, nicht leere fremde Ziele, manipulierte Instanzmarker, Symlink-Ziele und unbestätigte Pläne ab. Es initialisiert weder Git noch Netzwerkdienste.

## 3. Optional: echte private Instanz

Lege zunächst außerhalb des Repos eine eigene Antwortdatei an. Nutze dieselben Fachfelder wie im synthetischen Beispiel und setze zusätzlich konsistent:

```json
{
  "data_class": "internal",
  "synthetic": false,
  "contains_restricted_data": false
}
```

`internal` ist für echte interne Betriebsinformationen ohne Personendaten. Für personenbezogene oder vertrauliche Inhalte ist `confidential` nötig. Zugangsdaten sowie Gesundheits-, Finanz-, Rechts- oder Beschäftigtendaten gehören zu `S3 restricted` und werden nicht unterstützt.

Beginne nicht mit einem vollständigen Import. Wähle einen kleinen echten Arbeitsfall, zum Beispiel die Planung eines internen Projekts oder die Strukturierung eines eigenen Angebots, und gib nur die dafür notwendigen Informationen frei. Wenn Claude, Codex, Grok oder ein anderer Agent hilft, prüfe vorher dessen Aufbewahrung, Training, Löschung, Zugriffs- und Anbietergrenze. Der Agent darf reale Inhalte ausschließlich in der privaten Instanz bearbeiten.

```bash
chmod 600 "$HOME/.config/clief/private-answers.json"
python3 scripts/setup_workspace.py plan \
  --answers "$HOME/.config/clief/private-answers.json" \
  --target "$HOME/Documents/clief-private"
```

Prüfe Ziel, Datenklasse, alle geplanten Pfade und Warnungen. Erst danach anwenden:

```bash
python3 scripts/setup_workspace.py apply \
  --answers "$HOME/.config/clief/private-answers.json" \
  --target "$HOME/Documents/clief-private" \
  --confirm-token DEN_TOKEN_AUS_DEM_PLAN \
  --acknowledge-private-data
```

Das Acknowledgement bestätigt nur die lokale Speicherung. Es erlaubt keine Übergabe an einen Agenten und ersetzt weder Backup noch Verschlüsselung.

## 4. Restart prüfen

```bash
python3 scripts/setup_workspace.py status --target /private/tmp/clief-demo-instanz
```

Alternativ `STATUS.md` in der Instanz öffnen. Bei Konflikten nichts löschen oder überschreiben: Die gemeldete Datei manuell vergleichen und bewusst entscheiden.

## 5. Agent-Kontext begrenzen

Nach dem Setup zuerst `AGENT-INTERFACE.md` und `01-ausrichtung/user-context.md` prüfen. Für einen Agenten ohne direkten lokalen Dateizugriff den [providerneutralen Bundle-Builder](agent-interoperabilitaet.md) verwenden. Private Bundles verlangen Zweck, Agentenlabel und ein eigenes Acknowledgement. Das Bundle bleibt lokal, bis der User es bewusst innerhalb einer geprüften Daten- und Anbietergrenze weitergibt.

Probleme zuerst lokal mit dem gewählten Agenten diagnostizieren. Nur die verallgemeinerbare Ursache und einen bereinigten Fix nach [CONTRIBUTING.md](../CONTRIBUTING.md) zurückgeben; private Instanzdateien, echte Inhalte und persönliche Pfade bleiben lokal.

## 6. Optionaler privater Release-Scan

Maintainer können private Suchbegriffe zeilenweise in einer owner-only Datei außerhalb des Repositories hinterlegen und damit Arbeitsbaum sowie Git-Objekte prüfen:

```bash
chmod 600 /sicherer/pfad/private-release-denylist.txt
CLIEF_PRIVATE_DENYLIST=/sicherer/pfad/private-release-denylist.txt bash scripts/verify-repo.sh
```

Die Datei wird weder kopiert noch gehasht oder anderweitig im öffentlichen Repository gespeichert. Symlinks, repo-interne Dateien und Gruppen- oder Weltzugriff werden abgelehnt.
