# Primärer technischer Pfad

## Entscheidung

Technischer Default für den Alpha-MVP ist **Codex CLI im lokalen macOS-Sandbox-Wrapper**, Status `restricted-synthetic-only`.

Die Wahl beruht auf einem ausführbaren Prozess- und Canary-Test, nicht auf einem Vertraulichkeitsclaim. Der Wrapper setzt ein leeres temporäres Home, sperrt das reale Home sowie typische Benutzer-, Cloud-, Secret-, Socket- und Netzwerkpfade und erlaubt den aktuellen Repository-Root. Schreibzugriffe auf `.git` bleiben gesperrt. Der Codex-Prozess wurde nur mit `--version` gestartet; es gab keinen Modellaufruf und keine Übertragung.

## Grenzen

- Gilt nur für macOS 26.6.2, `sandbox-exec` und Codex CLI 0.150.0-alpha.12.2.
- macOS-Systempfade bleiben lesbar, soweit der Prozess sie zum Start benötigt.
- Der Wrapper ist kein Nachweis für einen vollständigen KI-Lauf, Anbieterendpunkte oder eine vertrauliche Verarbeitung.
- Das veraltete beziehungsweise nicht als stabile öffentliche Sicherheitsgrenze garantierte `sandbox-exec` erhöht das Portabilitäts- und Wartungsrisiko.
- Eine spätere Netzfreigabe benötigt einen neuen technischen Vertrag und ein Human Gate.
- Reale Unternehmens-, Kunden- und Personendaten bleiben gesperrt.

## Befehle

Isolation prüfen:

```bash
python3 scripts/runtime_isolation_probe.py
```

Einen rein lokalen synthetischen Befehl im gleichen Profil starten:

```bash
bash scripts/run-synthetic-isolated.sh /usr/bin/true
```

Der Wrapper verweigert die Ausführung außerhalb von macOS oder ohne `sandbox-exec`. Er bietet keine Option, die Netzsperre zu umgehen.
