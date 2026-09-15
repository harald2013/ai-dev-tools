# agent-examples

Lernprojekt: Agents selbst bauen. Durchgearbeitete Beispiele in drei Stufen,
von der handgeschriebenen Agent-Loop bis zum Claude Agent SDK.

Der Lernplan mit Reihenfolge, Lernzielen und Fortschritt steht in
**[plan.md](plan.md)**. Regeln fuer dieses Verzeichnis: [AGENTS.md](AGENTS.md).

## Aufbau

```
stage1_manual_loop/agent.py   Agent-Loop von Hand         (SDK: anthropic)
stage2_tool_runner/agent.py   Loop faehrt das SDK         (SDK: anthropic)
stage3_agent_sdk/             Claude Code als Bibliothek  (SDK: claude-agent-sdk)
sandbox/                      Spielmaterial, das die Agents lesen duerfen
```

Alle drei Stufen loesen absichtlich dieselbe Aufgabe ("Wie lange dauert der
Reindex-Job, und kollidiert er mit dem Deploy-Fenster?"), damit der
Unterschied im Code sichtbar wird und nicht in der Aufgabe.

## Setup

```bash
uv sync
```

**Stufe 1 + 2** brauchen einen API-Key von console.anthropic.com:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uv run python stage1_manual_loop/agent.py
uv run python stage2_tool_runner/agent.py
```

**Stufe 3** nutzt die installierte Claude-Code-CLI und deren Anmeldung:

```bash
uv run python stage3_agent_sdk/01_hello.py
```

Jeder Lauf kostet Geld. Die Uebungen liegen bei wenigen Cent; `max_turns` und
`max_budget_usd` in den Skripten sind die Bremse.
