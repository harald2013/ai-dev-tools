# AGENTS.md — Repo-weite Regeln

Gilt für das gesamte Repository, nicht nur für einzelne Unterverzeichnisse.
Unterverzeichnisse können eigene `AGENTS.md`-Dateien mit spezifischeren Regeln
haben (z. B. `openhands/AGENTS.md`) — diese ergänzen die hier genannten Regeln,
widersprechen ihnen aber nicht.

## Dokumentationsprinzip: Kein historischer Kontext in Doku-Dateien

Dokumentation in diesem Repository (`AGENTS.md`, `README.md`, sonstige
`*.md`-Dateien) beschreibt ausschließlich den aktuell gültigen Soll-/Ist-
Zustand — nicht *wie es früher war* oder *was entfernt/ersetzt wurde* ("früher
gab es X, das wurde entfernt, weil..."). Diese Art von Information gehört
nicht in laufende Doku, weil sie mit jeder weiteren Änderung veraltet,
verwirrt (welcher Teil ist noch relevant, welcher ist nur Rückblick?) und die
Datei aufbläht.

- **Wer/warum/wann etwas geändert wurde:** gehört in die **Commit-Historie**
  (`git log`) — die Begründung steht in der Commit-Message, nicht im Code oder
  in der Doku.
- **Eine bewusste, folgenreiche Architektur-/Design-Entscheidung** mit
  Alternativen und Trade-offs, die für künftige Entscheidungen relevant
  bleibt: **nur auf explizite Entscheidung hin** als eigenes ADR ablegen
  (z. B. `docs/adr/0001-<titel>.md`, Format frei wählbar, z. B. MADR). Ohne
  einen solchen expliziten Beschluss wird **kein** ADR-Verzeichnis oder
  -Eintrag angelegt — nicht auf Vorrat.
- Diese Regel gilt repo-weit, für jede Doku-Datei in jedem Unterverzeichnis.
