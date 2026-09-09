# Einmaliger Setup-Fragebogen

Alle Angaben werden flach in einer JSON-Datei beantwortet. Das versionierte Beispiel und alle technischen Tests verwenden ausschließlich erfundene Inhalte. Eine echte private Antwortdatei muss außerhalb des Repos liegen und owner-only Rechte besitzen.

| Feld | Frage |
|---|---|
| `workspace_id` | Welcher kurze technische Name identifiziert die Instanz? |
| `business_name` | Wie heißt die Beratung? |
| `owner_role` | Welche Rolle führt den Workspace? |
| `who` | Für wen arbeitet die Beratung? |
| `why` | Warum existiert sie? |
| `what` | Welche Leistung liefert sie? |
| `how` | Wie wird diese Leistung erbracht? |
| `user_goals` | Welche persönlichen Arbeitsziele soll der Workspace unterstützen? |
| `working_style` | Wie arbeitet der User am besten? |
| `communication_preferences` | Wie sollen Agents kommunizieren und strukturieren? |
| `capacity_constraints` | Welche Zeit-, Energie- oder Parallelitätsgrenzen sollen sichtbar bleiben? |
| `support_preferences` | Welche Art von Unterstützung ist hilfreich und welche nicht? |
| `audiences` | Welche Zielgruppen werden bedient? |
| `offers` | Welche Angebote gibt es? |
| `principles` | Welche Arbeitsprinzipien gelten? |
| `boundaries` | Welche Grenzen dürfen nicht überschritten werden? |
| `setup_date` | Welches Datum soll das Setup-Protokoll tragen? |

Zusätzlich sind eine konsistente Datenklasse und `contains_restricted_data: false` zwingend:

- Beispiel: `data_class: synthetic`, `synthetic: true`;
- private interne Instanz: `data_class: internal`, `synthetic: false`;
- private vertrauliche Instanz: `data_class: confidential`, `synthetic: false`.

Das vollständige synthetische Format steht in [`synthetic-answers.json`](synthetic-answers.json). `S3 restricted` und Secrets werden nicht unterstützt.
