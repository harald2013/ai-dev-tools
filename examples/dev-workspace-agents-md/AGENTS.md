# AGENTS.md

Dieses Verzeichnis enthaelt Repo-Checkouts. Vor jeder Aktion die zum Auftrag
passenden Repo-Anweisungen lesen:

| Repo / Fall | Einstieg vor dem Anlegen eines Checkouts |
|---|---|
| Brain | [brain/TIL-97-agent-workflows/AGENTS.md](brain/TIL-97-agent-workflows/AGENTS.md), danach dessen Workspace- und Workflow-Verweise |
| NRG | [nrg/TIL-97-agent-workflows/AGENTS.md](nrg/TIL-97-agent-workflows/AGENTS.md), danach dessen Workspace- und Workflow-Verweise |
| ai-dev-tools | [ai-dev-tools/main/AGENTS.md](ai-dev-tools/main/AGENTS.md) |
| agent-tools, falls vorhanden | `agent-tools/main/AGENTS.md` |

Die Brain-/NRG-Einstiege zeigen bis zum Merge von TIL-97 auf dessen Checkouts.
Nach dem Merge die Referenzcheckouts aktualisieren und die beiden Links auf
`<repo>/development/AGENTS.md` umstellen, bevor die TIL-97-Checkouts entfernt werden.

Bei einem bestehenden Auftrag die `AGENTS.md` im zugehoerigen Ticket-Checkout
lesen. Bei repo-uebergreifenden Auftraegen gilt das fuer jedes betroffene Repo.

Fehlt der Referenzcheckout, die versionierte `AGENTS.md` des Repos auf GitHub
lesen (Brain/NRG: `development`; ai-dev-tools/agent-tools: `main`).
Ist auch dieser Einstieg nicht erreichbar oder fehlt er, die fehlende
Voraussetzung melden und keinen Checkout- oder Release-Ablauf improvisieren.
