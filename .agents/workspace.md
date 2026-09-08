# Workspace

- Repository: `git@github.com:harald2013/ai-dev-tools.git`.
- Der einzige Referenz- und Arbeitscheckout ist
  `/home/harald/dev/ai-dev-tools/main/` auf `main`.
- Keine Ticket-Checkouts, Feature-Branches oder PRs.
- Vor jeder neuen Aufgabe Status pruefen und `git pull --ff-only` ausfuehren.
  Vorhandene Aenderungen erhalten; bei Konflikten nichts verwerfen.
- Implementieren, die fuer die Aenderung passenden Pruefungen ausfuehren,
  nur die eigenen Dateien stagen, mit sprechender englischer Commit-Message
  ohne Ticket-Praefix committen und `git push origin main` ausfuehren.
- Diese direkte main-Route gilt ausschliesslich fuer ai-dev-tools.
- Bei GitHub-Netzwerkfehlern oder scheinbaren Authentifizierungsproblemen
  denselben Befehl mit Netzwerk-Eskalation wiederholen, bevor neue
  Authentifizierung angefordert wird.
- Falls ein Linear-Ticket existiert: In Progress und In Review selbst pflegen;
  Done nur nach ausdruecklicher Zustimmung des Users.
- Der versionierte Workspace-Wegweiser liegt unter
  [examples/dev-workspace-agents-md/AGENTS.md](../examples/dev-workspace-agents-md/AGENTS.md).
  Bei Aenderungen am lokalen `/home/harald/dev/AGENTS.md` dieses Beispiel
  konsistent halten. Es enthaelt nur Verweise; Repo-Regeln stehen im Repo.
