# Runtime-Vertrag

Der Produktkern bleibt providerneutral. Runtime-Adapter dürfen die Regeln aus [`_core/`](../../_core/) nicht ersetzen oder abschwächen.

Die kanonische Schnittstelle ist ein begrenztes lokales Datei-Bundle gemäß [Agent-Interoperabilität](../agent-interoperabilitaet.md). Sie benötigt keine native Unterstützung für einen bestimmten Runtime-Dateinamen. Die folgenden Runtime-Befunde dokumentieren nur konkret geprüfte oder ungeprüfte Ausführungsprofile und definieren nicht das Produkt.

## Einstieg

1. Providerneutralen Datei- und Bundle-Vertrag prüfen.
2. [Runtime-Matrix](runtime-matrix.md) für den tatsächlich verwendeten Agenten lesen.
3. Falls der geprüfte lokale CLI-Pfad verwendet wird, den [primären technischen Pfad](primary-path.md) und `bash scripts/verify-spec-01.sh` prüfen.
4. Den Repository-eigenen Isolationsnachweis nur für seinen dokumentierten synthetischen Umfang verwenden. Ein echter privater Praxistest verlangt eine bewusste Agenten-/Anbieterentscheidung, Datenminimierung und ein aufgabenspezifisches Kontext-Bundle oder einzeln freigegebene Pfade.

Die maschinenlesbare Entscheidung steht in [`_core/runtime-policy.json`](../../_core/runtime-policy.json). Claude Desktop hat einen [separaten ungeprüften Status](claude-desktop.md).
