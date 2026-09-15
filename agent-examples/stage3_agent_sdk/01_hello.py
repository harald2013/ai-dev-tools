"""Stufe 3.1 — Hello Agent.

Dieselbe Frage wie in Stufe 1 und 2 — aber hier schreibst du kein einziges
Tool. `Read`, `Glob` und `Grep` bringt das SDK mit, samt Agent-Loop und
Kontextverwaltung. Uebrig bleibt Konfiguration: welches Verzeichnis, welche
Tools, welche Grenzen.

    uv run python stage3_agent_sdk/01_hello.py
"""

import asyncio
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    query,
)

SANDBOX = (Path(__file__).resolve().parent.parent / "sandbox").resolve()

FRAGE = (
    "Wie lange dauert der Reindex-Job, und kollidiert er mit dem Deploy-Fenster? "
    "Sieh in den Dateien nach und begruende knapp."
)


async def main() -> None:
    options = ClaudeAgentOptions(
        cwd=str(SANDBOX),                        # der Agent sieht nur dieses Verzeichnis
        # `tools` legt fest, WELCHE Tools es ueberhaupt gibt.
        # Nicht zu verwechseln mit `allowed_tools`: das ist nur die
        # Auto-Freigabe-Liste und schraenkt nichts ein — steht Bash nicht
        # drin, benutzt der Agent es trotzdem (nachgemessen).
        tools=["Read", "Glob", "Grep"],
        permission_mode="default",
        system_prompt="Du antwortest knapp und auf Deutsch.",
        max_turns=10,        # Rundenlimit, wie die for-Schleife in Stufe 1
        max_budget_usd=0.50, # harte Kostenbremse
        setting_sources=None,  # KEINE ~/.claude- oder Projekt-Settings laden:
                               # die Uebung soll reproduzierbar sein
    )

    # `query` ist ein async Generator: er liefert Nachrichten, waehrend der
    # Agent laeuft. Es gibt mehrere Nachrichtentypen — sie auseinanderzuhalten
    # ist die eigentliche Uebung dieses Schritts.
    async for message in query(prompt=FRAGE, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    print(f"-> {block.name}({block.input})")
                elif isinstance(block, ThinkingBlock):
                    print("-> (denkt nach)")

        elif isinstance(message, ResultMessage):
            # Kommt genau einmal, ganz am Schluss.
            print(
                f"\nFertig: {message.num_turns} Turns, "
                f"{message.duration_ms / 1000:.1f}s, "
                f"${message.total_cost_usd or 0:.4f}, "
                f"stop_reason={message.stop_reason}"
            )
            print(f"Session: {message.session_id}")  # damit laesst sich spaeter fortsetzen


if __name__ == "__main__":
    asyncio.run(main())
