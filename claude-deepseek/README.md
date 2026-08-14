# claude-deepseek

Startet die Claude Code CLI mit DeepSeek als Backend, über DeepSeeks
Anthropic-kompatiblen API-Endpoint (`https://api.deepseek.com/anthropic`).

## Voraussetzungen

- Claude Code CLI ist installiert (`npm install -g @anthropic-ai/claude-code`).
- Ein DeepSeek API-Key ist in `DEEPSEEK_KEY` gesetzt, z. B. dauerhaft in
  `~/.bashrc` / `~/.zshrc`:

  ```bash
  export DEEPSEEK_KEY="sk-..."
  ```

  Der Key landet damit nie im Repo/Git-Verlauf.

## Nutzung

```bash
./claude-deepseek.sh
```

Das Script:

1. bricht in den (in Wien) teuren DeepSeek-Peak-Zeiten (03:00–06:00 und
   08:00–12:00) standardmäßig ab, um Kosten zu sparen — mit
   `./claude-deepseek.sh --force` lässt sich das übersteuern,
2. zeigt das aktuelle DeepSeek-Guthaben an,
3. setzt die nötigen `ANTHROPIC_*`/`CLAUDE_CODE_*`-Umgebungsvariablen für die
   aktuelle Session,
4. startet `claude` mit den übrigen Argumenten.

Optional ins `PATH` legen (z. B. Symlink in `~/.local/bin`), um es von
überall als `claude-deepseek.sh` aufzurufen.

## Bekannte Einschränkungen

- Modell-Namen (`deepseek-v4-pro`, `deepseek-v4-flash`) folgen dem aktuellen
  Stand der [DeepSeek-Doku für Claude-Code-Integration](https://api-docs.deepseek.com/quick_start/agent_integrations/claude_code/)
  und können sich mit neuen DeepSeek-Modellversionen ändern.
- Nicht jedes Claude-Code-Feature ist über einen Drittanbieter-Endpoint
  garantiert 1:1 kompatibel (z. B. Extended Thinking, bestimmte Tool-Use-
  Details).
