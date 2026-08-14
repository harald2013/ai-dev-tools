# dev-workspace-agents-md

Dieses Verzeichnis enthält ein reales, in Benutzung befindliches Beispiel für
eine `AGENTS.md`, wie sie im lokalen `~/dev`-Verzeichnis eines Entwicklers
liegt.

## Zweck

Die `AGENTS.md` dient AI Coding Agents (z. B. Claude Code) als Anleitung, wie
sie sich in einem Verzeichnis mit mehreren Git-Repos zurechtfinden, in dem
regelmäßig an verschiedenen Aufträgen/Tickets parallel gearbeitet wird. Sie
legt fest:

- wie pro Auftrag ein isolierter Checkout angelegt wird (Branch-, Ordner- und
  PR-Namenskonvention),
- wo ein dauerhafter Referenz-Checkout des Default-Branch liegt,
- wie mit Ticket-Status (z. B. in Linear) umgegangen wird,
- welche Ausnahmen einzelne Repos vom Standard-Workflow haben (z. B. ein Repo
  ohne Ticket-Nummern, das direkt auf `main` bespielt wird).

Das Beispiel soll zeigen, wie eine solche `AGENTS.md` für eine eigene
Multi-Repo-Dev-Umgebung aussehen kann, und als Vorlage zum Anpassen dienen —
nicht als universelle Lösung, sondern als konkretes, funktionierendes
Beispiel für die eigene Struktur und Konventionen.
