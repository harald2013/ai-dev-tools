"""Stufe 2 — dieselbe Aufgabe, aber das SDK faehrt die Loop.

Unterschied zu Stufe 1: die while-Schleife, die Historie und das
Zusammenbauen der tool_result-Bloecke sind weg. Uebrig bleiben die
Tool-Funktionen. Das Schema baut `@beta_tool` aus Signatur und Docstring.

    uv run python stage2_tool_runner/agent.py
"""

from pathlib import Path

import anthropic
from anthropic import beta_tool

MODEL = "claude-opus-5"
SANDBOX = (Path(__file__).resolve().parent.parent / "sandbox").resolve()

FRAGE = (
    "Wie lange dauert der Reindex-Job, und kollidiert er mit dem Deploy-Fenster? "
    "Sieh in den Dateien nach und begruende knapp."
)


@beta_tool
def list_files() -> str:
    """Listet alle Dateien im Projektverzeichnis auf."""
    return "\n".join(sorted(p.name for p in SANDBOX.iterdir() if p.is_file()))


@beta_tool
def read_file(path: str) -> str:
    """Liest eine Datei aus dem Projektverzeichnis als Text.

    Args:
        path: Dateiname relativ zum Projektverzeichnis, z. B. notes.md.
    """
    # Unveraendert aus Stufe 1: das Gate gehoert in die Tool-Funktion. Der
    # Runner prueft nichts — er ruft auf, was das Modell verlangt.
    ziel = (SANDBOX / path).resolve()
    if not ziel.is_relative_to(SANDBOX):
        return f"Fehler: {path} liegt ausserhalb des Projektverzeichnisses."
    if not ziel.is_file():
        return f"Fehler: {path} existiert nicht."
    return ziel.read_text()


def main() -> None:
    client = anthropic.Anthropic()

    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=16000,
        tools=[list_files, read_file],
        messages=[{"role": "user", "content": FRAGE}],
    )

    # Jede Iteration ist eine Modellantwort. Der Runner fuehrt die Tools aus
    # und haengt die Ergebnisse selbst an — er hoert auf, sobald keine
    # tool_use-Bloecke mehr kommen.
    letzte = None
    for runde, antwort in enumerate(runner, start=1):
        letzte = antwort
        for block in antwort.content:
            if block.type == "text":
                print(f"\n[{runde}] {block.text}")
            elif block.type == "tool_use":
                print(f"[{runde}] -> {block.name}({block.input})")

    if letzte is not None:
        print(f"\nEnde ({letzte.stop_reason}), "
              f"{letzte.usage.input_tokens} in / {letzte.usage.output_tokens} out Token.")


if __name__ == "__main__":
    main()
