# AGENTS.md — Repo-weite Regeln

Workspace, Arbeitscheckout und Commit/Push-Ablauf:
[.agents/workspace.md](.agents/workspace.md) vor Arbeitsbeginn lesen.

Gilt repo-weit. Unterverzeichnisse können eigene `AGENTS.md` mit spezifischeren
Regeln haben (z. B. `openhands/AGENTS.md`); diese ergänzen die hier genannten
Regeln, widersprechen ihnen nicht.

## Zweck des Repos

Spielwiese für AI-Tests. Jedes Unterverzeichnis im Root behandelt ein eigenes,
in sich abgeschlossenes Thema. Die Themen sind unabhängig voneinander und
brauchen keine Verbindung zu den anderen Root-Verzeichnissen.

Arbeitsweise: Es wird immer in genau einem ausgewählten Verzeichnis gearbeitet.
Änderungen bleiben in diesem Verzeichnis; andere Themen werden nicht angefasst
und keine Querverbindungen zwischen ihnen erzeugt.

## Doku: kein historischer Kontext

Doku (`AGENTS.md`, `README.md`, alle `*.md`) beschreibt nur den aktuell
gültigen Soll-/Ist-Zustand — nicht, wie es früher war oder was entfernt bzw.
ersetzt wurde.

- **Wer/warum/wann geändert:** gehört in die Commit-Message (`git log`), nicht
  in Doku oder Code.
- **Folgenreiche Architektur-/Design-Entscheidung:** nur auf explizite
  Entscheidung hin als ADR ablegen (z. B. `docs/adr/0001-<titel>.md`, Format
  frei). Ohne expliziten Beschluss kein ADR-Verzeichnis und kein Eintrag —
  nicht auf Vorrat.
