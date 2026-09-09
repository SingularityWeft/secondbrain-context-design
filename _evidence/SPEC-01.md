# SPEC-01 Akzeptanzevidenz

## Vor dem Build definierte Evidenz

| Kriterium | Erforderliche technische Evidenz |
|---|---|
| frisches Testprofil | pro Lauf neu erzeugtes, leeres Runtime-Home ohne Benutzerkonfiguration |
| erlaubter Arbeitsbereich | Repository-Datei unter Sandbox lesbar; Schreibtest nur im ignorierten temporären Testbereich |
| Git-Grenze | Schreibversuch in `.git` endet mit technischer Berechtigungsverweigerung |
| externer Canary | existierender Canary außerhalb des Repositories bleibt unlesbar; kein Inhalt im Log |
| sensible Hostpfade | echtes Home, Developer-Root, Cloud-Sync und Secret-Verzeichnis werden einzeln abgewiesen |
| Shell und Netzwerk | lokaler Shell-Smoke besteht; Socket-Verbindung endet mit technischer Berechtigungsverweigerung |
| Container-Socket | Vorhandensein wird ohne Inhalt inventarisiert; Zugriff bleibt gesperrt oder Socket ist abwesend |
| Runtime-Stand | OS, Build, Runtime-Version und getesteter Repository-SHA im anonymisierten JSON-Protokoll |
| Claude Desktop | Version inventarisiert; ohne echten Isolationstest ausdrücklich ungeprüft und synthetisch-only |
| Owner-Entscheidung | technische Empfehlung sichtbar; fehlende Signatur bleibt offen und wird nicht simuliert |

Der Post-Commit-Lauf gegen `89bd45cd3aaa0f3339c738eb0039d3ed7dea8e22` ist im [anonymisierten Runtime-Protokoll](runtime/macos-codex-probe.json) festgehalten.
