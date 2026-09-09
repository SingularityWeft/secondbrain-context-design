# Sicherheitsrichtlinie

## Unterstützter Stand

Dieses öffentliche Repository und seine Tests arbeiten ausschließlich mit synthetischen Daten. Der Setup-Pfad kann außerhalb des Repos eine getrennte owner-only Instanz für `S1 internal` oder `S2 confidential` erzeugen. `S3 restricted`, Secrets und automatische externe Übertragung bleiben gesperrt.

Release-spezifische Namen oder andere private Suchbegriffe gehören nicht in den Starter – auch nicht als Hash. Maintainer können sie stattdessen zeilenweise in einer externen Datei mit Modus `0600` hinterlegen und den Vollverify mit `CLIEF_PRIVATE_DENYLIST=/sicherer/pfad/denylist.txt bash scripts/verify-repo.sh` ausführen. Der Checker verweigert Symlinks, repo-interne und zu breit lesbare Denylists.

## Sichere Betriebsgrenze

- Im Repository nur synthetische Daten verwenden; private Antwortdateien und Instanzen immer außerhalb halten.
- Keine externe Runtime, Datenbank, Synchronisation oder Connectoren voraussetzen.
- Keine Secrets in Dateien, Prompts, Commits oder Testausgaben speichern.
- Eine Prompt-Anweisung gilt nicht als technische Isolation.
- Private Setup- und Kontextaktionen benötigen eigene Acknowledgements; unklare Daten und unbekannte Aktionen werden fail-closed gestoppt.
- Dateirechte `0700`/`0600` ersetzen weder Festplattenverschlüsselung noch Backup, Prozessisolation oder Anbieterprüfung.
- Claude Desktop bleibt `isolation-unverified / synthetic-only`, bis ein echter technischer Isolationstest dokumentiert ist.
- Der primäre technische CLI-Pfad ist nur unter dem dokumentierten macOS-Sandboxprofil und ausschließlich mit synthetischen Daten unterstützt. Systemdateien bleiben für den Prozess lesbar; Benutzerdaten und Netzwerk werden technisch gesperrt.

## Befunde melden

Bis zu einer öffentlichen Freigabe Sicherheitsbefunde lokal dokumentieren und der Repository-Ownerin über einen bereits vereinbarten privaten Kanal vorlegen. Keine echten Secrets in einen Befund kopieren. Bei möglicher Offenlegung die betroffene Ausführung stoppen, Artefakte unverändert sichern und keine Veröffentlichung vornehmen.

## Keine Garantie

Die Richtlinien und Prüfskripte reduzieren bekannte Risiken, ersetzen aber weder technische Sandboxen noch eine rechtliche oder sicherheitsfachliche Einzelfallprüfung.
