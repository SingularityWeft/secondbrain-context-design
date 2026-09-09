# Runtime-Matrix

Stand: 2026-09-08 auf macOS 26.6.2 (Build 25G83).

| Pfad | Status | Datei-/Home-Isolation | Shell | Netzwerk | Connectoren | Kosten | Bedienaufwand |
|---|---|---|---|---|---|---|---|
| Providerneutrales lokales Kontext-Bundle | Formatvertrag für jeden UTF-8-textfähigen Agenten | User wählt explizite Dateien; Bundle bleibt zunächst lokal | nicht erforderlich | Builder ohne Netzwerk | keine | keine Builder-Kosten | lokale CLI plus bewusste Übergabe |
| Codex CLI 0.150.0-alpha.12.2 im lokalen Sandbox-Wrapper | **primärer technischer Default; eingeschränkt auf synthetische Daten** | Canary, echtes Home, Developer-Root außerhalb des Repositories, Cloud-Sync und Secret-Pfade technisch gesperrt | innerhalb des erlaubten Prozesses möglich | gesperrt | durch leeres Runtime-Home nicht konfiguriert | keine zusätzlichen lokalen Toolkosten; Modellnutzung nicht getestet | Terminal und lokaler Verify |
| Claude Code 2.1.263 mit `--restricted`, `--safe-mode` und strengem MCP-Modus | eingeschränkt, nicht als Primärpfad verifiziert | dokumentierte Produktflags, aber kein vollständiger Lauf im frischen Testprofil | eingeschränkt konfigurierbar | nicht technisch in diesem Spike belegt | streng konfigurierbar, nicht praktisch geprüft | nicht bewertet | Terminal |
| Claude Desktop 1.49585.0 | **isolation-unverified / synthetic-only** | kein frischer technisch isolierter Desktop-Lauf | unbekannt für den konkreten Desktop-Modus | unbekannt | Benutzerkonfiguration nicht inspiziert | nicht bewertet | grafische Oberfläche |
| Docker 29.5.3 | nicht unterstützt in diesem Alpha | CLI vorhanden, Daemon und lokales Testimage nicht verfügbar; kein Dienst gestartet | nicht geprüft | nicht geprüft | kein Mount geprüft | nicht bewertet | zusätzliche Container-Bedienung |

`Unterstützt` bedeutet hier nie Freigabe für echte Daten. Der primäre Pfad beweist nur die lokale Prozessgrenze für den angegebenen Stand; KI-Inferenz und externe Anbieterkommunikation wurden absichtlich nicht ausgeführt.

Für nicht einzeln getestete Agents gilt: Das Markdown-/JSON-Format kann manuell bereitgestellt werden, aber native Dateirechte, Datenverarbeitung, Modellqualität und Isolation sind `unverified`. Ein Agentenname allein öffnet kein Datengate.
