"""Stufe 1 — die Agent-Loop von Hand.

Alles, was ein Agent ist, steht in diesem File: ein Modellaufruf in einer
Schleife, zwei selbstgeschriebene Tools und die Buchfuehrung ueber die
Historie. Keine Framework-Magie.

    uv run python stage1_manual_loop/agent.py
"""

from pathlib import Path

import anthropic

MODEL = "claude-opus-5"
SANDBOX = (Path(__file__).resolve().parent.parent / "sandbox").resolve()

FRAGE = (
    "Wie lange dauert der Reindex-Job, und kollidiert er mit dem Deploy-Fenster? "
    "Sieh in den Dateien nach und begruende knapp."
)

# Das Schema ist Prompt, nicht Doku: das Modell entscheidet allein anhand von
# `description` und `input_schema`, wann und womit es ein Tool aufruft.
TOOLS: list[anthropic.types.ToolParam] = [
    {
        "name": "list_files",
        "description": "Listet alle Dateien im Projektverzeichnis auf.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "read_file",
        "description": "Liest eine Datei aus dem Projektverzeichnis als Text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Dateiname relativ zum Projektverzeichnis, z. B. notes.md",
                }
            },
            "required": ["path"],
        },
    },
]


def list_files() -> str:
    return "\n".join(sorted(p.name for p in SANDBOX.iterdir() if p.is_file()))


def read_file(path: str) -> str:
    # Die Sicherheitsgrenze liegt hier, nicht im Modell. Das Modell darf
    # "../../.ssh/id_rsa" vorschlagen — durchlassen muss es diese Funktion.
    ziel = (SANDBOX / path).resolve()
    if not ziel.is_relative_to(SANDBOX):
        return f"Fehler: {path} liegt ausserhalb des Projektverzeichnisses."
    if not ziel.is_file():
        return f"Fehler: {path} existiert nicht."
    return ziel.read_text()


def run_tool(name: str, args: dict) -> str:
    """Namen auf Funktionen abbilden. Fehler werden zurueckgegeben, nicht
    geworfen — der Agent soll sie lesen und es anders versuchen koennen."""
    try:
        if name == "list_files":
            return list_files()
        if name == "read_file":
            return read_file(args["path"])
        return f"Fehler: unbekanntes Tool {name}."
    except Exception as exc:  # noqa: BLE001 — bewusst breit, s. o.
        return f"Fehler beim Ausfuehren von {name}: {exc}"


def main() -> None:
    client = anthropic.Anthropic()

    # Die API ist zustandslos. Diese Liste IST das Gedaechtnis des Agents und
    # geht bei jedem Durchlauf komplett erneut raus.
    messages: list[anthropic.types.MessageParam] = [
        {"role": "user", "content": FRAGE}
    ]

    for runde in range(1, 11):  # harte Obergrenze: ein Agent ohne Abbruch ist ein Kostenleck
        antwort = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            tools=TOOLS,
            messages=messages,
        )

        for block in antwort.content:
            if block.type == "text":
                print(f"\n[{runde}] {block.text}")
            elif block.type == "tool_use":
                print(f"[{runde}] -> {block.name}({block.input})")

        # Nur `tool_use` heisst "mach weiter". Alles andere (end_turn,
        # max_tokens, refusal, ...) beendet die Schleife.
        if antwort.stop_reason != "tool_use":
            print(f"\nEnde ({antwort.stop_reason}), {runde} Runde(n), "
                  f"{antwort.usage.input_tokens} in / {antwort.usage.output_tokens} out Token.")
            return

        # Die Assistant-Antwort muss unveraendert in die Historie — inklusive
        # der tool_use-Bloecke, auf die sich die Ergebnisse gleich beziehen.
        messages.append({"role": "assistant", "content": antwort.content})

        # Alle Ergebnisse einer Runde gehen in EINE user-Message. Aufsplitten
        # bringt dem Modell bei, keine parallelen Tool-Calls mehr zu machen.
        ergebnisse: list[anthropic.types.ToolResultBlockParam] = [
            {
                "type": "tool_result",
                "tool_use_id": block.id,  # muss zum tool_use-Block passen
                "content": run_tool(block.name, block.input),
            }
            for block in antwort.content
            if block.type == "tool_use"
        ]
        messages.append({"role": "user", "content": ergebnisse})

    print("\nAbbruch: Rundenlimit erreicht.")


if __name__ == "__main__":
    main()
