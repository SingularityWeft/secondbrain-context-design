# Runtime-Adapter

Lies zuerst `AGENT-INTERFACE.md`, dann `CONTEXT.md`, und lade nur die dort gerouteten Dateien. Bei einer registrierten Basisaufgabe lade zusätzlich genau den passenden Vertrag aus `skills/`. Die kanonische Produktlogik steht in `_core/`; dieser Adapter darf sie nicht duplizieren oder abschwächen.

Arbeite ausschließlich innerhalb der in `.clief-instance.json` erklärten Datenklasse. `S1 internal` und `S2 confidential` sind nur in einer getrennten privaten Instanz erlaubt; dort ist ein unbeschränkter Agenten-Scan gesperrt und ein aufgabenspezifisches Kontext-Bundle erforderlich. `S3 restricted` und Secrets sind immer gesperrt. Keine externen Writes, Datenübertragungen, Kontakte, Connectoren, Commits, Pushes oder Veröffentlichungen ohne dokumentiertes Human Gate. Bei unbekannter Aktion oder Datenklasse stoppen.

Bei einem allgemein nützlichen Fehler darfst du eine synthetische oder vollständig bereinigte Reproduktion, ein Issue und einen kleinen Patch vorbereiten. Kopiere niemals private Instanzdateien, echte Inhalte, persönliche Pfade oder vollständige Logs in den öffentlichen Clone. Zeige öffentlichen Text und Diff vor jeder Veröffentlichung; Issue, Push und Pull Request benötigen jeweils die Freigabe des Users.
