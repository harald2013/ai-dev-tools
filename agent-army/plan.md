# Lernplan: Agents selbst bauen

Ziel: **Stufe 3 (Claude Agent SDK) sicher beherrschen.** Stufe 1 und 2 sind
bewusst kurz — sie existieren nur, damit die Mechanik unter Stufe 3 keine
Blackbox ist.

Sprache: Python. Ein einziges uv-Projekt fuer alle Stufen (`pyproject.toml`).

## Die drei Stufen

| Stufe | Paket | Wer schreibt die Loop | Wer stellt die Tools |
|---|---|---|---|
| 1 | `anthropic` | du | du |
| 2 | `anthropic` (Tool Runner) | SDK | du |
| 3 | `claude-agent-sdk` | SDK (Claude-Code-Harness) | SDK (Read/Write/Bash/Grep/...) + du |

Wichtig: Stufe 1/2 und Stufe 3 sind **zwei verschiedene Pakete**, nicht zwei
Ausbaustufen desselben. Stufe 1/2 reden direkt mit der Messages-API. Stufe 3
ist Claude Code als Bibliothek: es startet die Claude-Code-CLI als Subprozess
und spricht ueber sie mit dem Modell.

---

## Stufe 1 — Loop von Hand (kurz)

Datei: `stage1_manual_loop/agent.py` — Code steht, ungelaufen (braucht API-Key).

Ein Agent mit zwei selbstgeschriebenen Tools (`list_files`, `read_file`), die
nur in `sandbox/` lesen duerfen.

Danach verstanden:

- [ ] Die API ist zustandslos: bei jedem Aufruf geht die **komplette**
      `messages`-Historie erneut raus.
- [ ] `stop_reason == "tool_use"` ist das einzige Signal, dass der Agent
      weiterlaufen muss; `"end_turn"` beendet die Schleife.
- [ ] Ein Tool-Ergebnis geht als `user`-Message mit `tool_result`-Bloecken
      zurueck, und `tool_use_id` muss zum `tool_use`-Block passen.
- [ ] Mehrere `tool_use`-Bloecke in einer Antwort ⇒ **alle** Ergebnisse in
      **einer** user-Message zurueck.
- [ ] Das Tool-Schema (`input_schema`) ist das, woran das Modell die
      Argumente ausrichtet — die Beschreibung ist Prompt, nicht Doku.
- [ ] Die Sicherheitsgrenze liegt in **deiner** Tool-Funktion, nicht im Modell
      (siehe Pfad-Check in `read_file`).

## Stufe 2 — Tool Runner (kurz)

Datei: `stage2_tool_runner/agent.py` — Code steht, ungelaufen (braucht API-Key).

Dieselben zwei Tools, dieselbe Aufgabe — aber die Loop schreibt das SDK.

Danach verstanden:

- [ ] `@beta_tool` erzeugt das Tool-Schema aus Signatur + Docstring.
- [ ] `client.beta.messages.tool_runner(...)` ersetzt die ganze while-Schleife
      aus Stufe 1; jede Iteration liefert eine `BetaMessage`.
- [ ] Was der Runner **nicht** abnimmt: Approval-Gates, `pause_turn`,
      Historie (er haelt sie intern, gibt sie aber nicht heraus).
- [ ] Vergleich zu Stufe 1: identisches Verhalten, ~40 Zeilen weniger Code.

Danach sind Stufe 1 und 2 fertig. Sie werden nicht weiter ausgebaut.

---

## Stufe 3 — Claude Agent SDK (das eigentliche Ziel)

Verzeichnis: `stage3_agent_sdk/`

Hier ist der Unterschied nicht "weniger Code", sondern ein anderer
Gegenstand: du bekommst Agent-Loop, Kontextverwaltung, eingebaute Tools,
Permissions, Sessions, Hooks und Subagents geschenkt und **konfigurierst**
statt zu implementieren. Die Arbeit verschiebt sich von "wie rufe ich das
Modell" zu "welche Rechte, welche Tools, welche Abbruchbedingungen".

Schritte, aufeinander aufbauend:

- [x] **3.1 Hello Agent** — `01_hello.py` (laeuft, 6 Turns, ~$0.07)
      `query(prompt=..., options=ClaudeAgentOptions(...))`, Message-Typen
      (`AssistantMessage`/`TextBlock`/`ResultMessage`) auseinanderhalten,
      Kosten und Turn-Zahl aus `ResultMessage` lesen.
- [ ] **3.2 Permissions** — `02_permissions.py`
      `permission_mode`, `allowed_tools`, und der `can_use_tool`-Callback als
      programmatisches Gate (`PermissionResultAllow` / `PermissionResultDeny`).
      Das ist die wichtigste Stufe-3-Faehigkeit: der Agent darf Dateien
      schreiben und Befehle ausfuehren — die Grenze ziehst du hier.
      Bereits in 3.1 aufgefallen und nachgemessen: `allowed_tools` ist die
      **Auto-Freigabe**-Liste, keine Einschraenkung. Mit
      `allowed_tools=["Read","Glob","Grep"]` hat der Agent trotzdem `Bash`
      benutzt; erst `tools=[...]` (bzw. `disallowed_tools`) nimmt es ihm weg.
- [ ] **3.3 Eigene Tools** — `03_custom_tools.py`
      `@tool` + `create_sdk_mcp_server()`: In-Process-MCP-Server, kein
      Subprozess. Vergleich mit Stufe 1/2: dasselbe Konzept, andere Huelle.
      Namensschema der Tools: `mcp__<server>__<tool>`.
- [ ] **3.4 Sessions** — `04_session.py`
      `ClaudeSDKClient` statt `query()`: mehrere Turns im selben Kontext,
      `interrupt()`, `resume`/`continue_conversation`.
- [ ] **3.5 Hooks** — `05_hooks.py`
      `PreToolUse` & Co.: mitloggen, blockieren, Eingaben umschreiben.
      Abgrenzung zu `can_use_tool` (Hook = Lifecycle-Ereignis,
      `can_use_tool` = Freigabe-Entscheidung).
- [ ] **3.6 Subagents** — `06_subagents.py`
      `agents={"name": AgentDefinition(...)}`: Fan-out auf spezialisierte
      Agents mit eigenem Prompt, eigenem Toolset, eigenem Modell.
      Das ist die "agent army".
- [ ] **3.7 Eigener Agent** — `army/`
      Ein Agent fuer eine echte eigene Aufgabe, der 3.2–3.6 kombiniert.
      Aufgabe wird festgelegt, wenn 3.1–3.6 stehen.

## Voraussetzungen

- Stufe 1+2 brauchen einen **API-Key** (`ANTHROPIC_API_KEY`) von
  console.anthropic.com. Jeder Lauf kostet echtes Geld (Opus 5: $5/$25 pro
  1M Token; die Uebungen hier liegen im Cent-Bereich).
- Stufe 3 braucht die Claude-Code-CLI (ist installiert) und laut Anthropic
  fuer alles ausser lokalem Eigengebrauch ebenfalls einen API-Key.

## Regeln fuer dieses Verzeichnis

Siehe [AGENTS.md](AGENTS.md).
