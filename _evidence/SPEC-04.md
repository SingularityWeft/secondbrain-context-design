# SPEC-04 Akzeptanzevidenz

## Vor dem Build definierte Evidenz

| Kriterium | Erforderliche Evidenz |
|---|---|
| Briefing | Zielgruppe, Entscheidung/Nutzen, Scope, `synthetic` und offene Fragen in Stufe 1 |
| Claim Ledger | jeder Faktenclaim mit Quelle, Fundstelle, Version/Stand und Evidenzstatus; Annahmen eigener Abschnitt |
| Widerspruch/Lücke | 60-/90-Minuten-Widerspruch und unzureichender Garantieclaim bleiben in Ledger, Struktur und Review sichtbar |
| Human Gate | ohne vollständige Entscheidungsakte kein Stufe-5-Arbeitsstand; technische Fixtures tragen `not-human-evidence` |
| manuelle Änderungen | Hash vor/nach Änderung im finalen Run Record; aktuelle Struktur wird unverändert in Stufe 5 übernommen |
| Ablehnung | abgelehntes Gate erzeugt keinen Arbeitsstand, aber ein Debrief mit verworfenen Claims |
| Run Record | Case/Workflow-Version, Zeit, Quellversionen und -hashes, Artefakthashes, Änderungen, Ergebnis und offene Fragen |
| Debrief | Ergebnis, verworfene Claims, offene Fragen, Wiederverwendbares und nächste Entscheidung |
| Grenzen | kein kundenspezifisches Live-Artefakt, private Methodik, echte Kundendaten, Außenaktion oder Rechtsbewertung |

Die [vollständige technische Beispielkette](workflow/run-001/01-briefing.md) und der [technische Rubrikreview](workflow/run-001/rubric-review.md) liegen unter `_evidence/workflow/run-001/`. Der Status bleibt `not-human-approved`; dies ist keine menschliche Freigabe.
