# AGENTS.md — agent-army

Lernprojekt. Ziel und Reihenfolge stehen in [plan.md](plan.md); der Plan ist
die fuehrende Datei und wird beim Abschluss eines Schritts dort abgehakt.

## Regeln

- **Lernprojekt, nicht Produktcode.** Kurze, lesbare Dateien schlagen
  Vollstaendigkeit. Keine Abstraktionsschichten, keine Framework-Bastelei,
  keine Wiederverwendung zwischen den Stufen — jede Stufe steht fuer sich und
  darf denselben Code nochmal enthalten, wenn das den Vergleich zeigt.
- **Stufe 1 und 2 sind abgeschlossen.** Nicht ausbauen, nicht umbauen.
  Neue Arbeit findet in `stage3_agent_sdk/` statt.
- **Kein Netzwerkzugriff der Agents auf echte Systeme.** Die Uebungstools
  lesen ausschliesslich unter `sandbox/`.
- **Jeder Lauf kostet Geld.** Skripte nicht ungefragt ausfuehren; erst zeigen,
  was laufen wuerde.
- `ANTHROPIC_API_KEY` steht in `.env` oder in der Shell — niemals im Code,
  niemals im Repo.

## Setup

```bash
uv sync                      # legt .venv an
export ANTHROPIC_API_KEY=... # von console.anthropic.com
uv run python stage1_manual_loop/agent.py
```
