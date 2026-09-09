# Entscheidungsakte – Format

Eine reale Akte benötigt `evidence_type: human-record`, `not_human_evidence: false`, einen benannten menschlichen Owner, Zeitpunkt, Entscheidung für jeden Gate-Claim und `final_artifact_decision`.

Automatisierte Tests dürfen ausschließlich `evidence_type: technical-fixture-not-human` und `not_human_evidence: true` verwenden. Diese Akten prüfen nur die Zustandsmaschine und können keinen menschlich freigegebenen Status erzeugen.

Zulässige Claim-Entscheidungen: `accept`, `change`, `reject`. Bei `change` ist ein neuer Wortlaut Pflicht. Zulässige finale Entscheidungen: `accept`, `reject`. Veröffentlichung und Kundenkommunikation bleiben in beiden Fällen außerhalb des Workflows.
