#!/usr/bin/env bash

# Startet Claude Code mit DeepSeek als Backend (Anthropic-kompatible API).
# Erwartet den API-Key in der Umgebungsvariable DEEPSEEK_KEY, z. B.
# export DEEPSEEK_KEY="sk-..." in ~/.bashrc / ~/.zshrc.
#
# Nutzung:
#   claude-deepseek.sh              # normaler Start (blockiert in Peak-Zeiten)
#   claude-deepseek.sh --force      # Start trotz Peak-Zeit erzwingen
#   source claude-deepseek.sh       # falls Env-Vars auch im aktuellen Shell
#                                    # verbleiben sollen (sonst reicht Ausführen)

if [ -z "$DEEPSEEK_KEY" ]; then
    echo "claude-deepseek: DEEPSEEK_KEY ist nicht gesetzt." >&2
    echo "  export DEEPSEEK_KEY=\"<dein DeepSeek API Key>\"" >&2
    return 1 2>/dev/null || exit 1
fi

# 1. Uhrzeit in Wien prüfen (Aktuelle Stunde 0-23), unabhängig von der
#    System-Zeitzone.
current_hour=$(TZ='Europe/Vienna' date +%H)
is_peak=false
force_start=false

# Prüfen, ob --force übergeben wurde
for arg in "$@"; do
    if [ "$arg" = "--force" ]; then
        force_start=true
    fi
done

# Teure Peak-Zeiten für Wien: 03:00 - 06:00 und 08:00 - 12:00
if [ "$current_hour" -ge 3 ] && [ "$current_hour" -lt 6 ]; then
    is_peak=true
elif [ "$current_hour" -ge 8 ] && [ "$current_hour" -lt 12 ]; then
    is_peak=true
fi

# 2. Peak-Sperre auswerten
if [ "$is_peak" = true ] && [ "$force_start" = false ]; then
    echo -e "\033[0;31m⚠️ ACHTUNG: Du befindest dich in der TEUREN DeepSeek-Spitzenzeit (Peak)!\033[0m"
    echo "Aktuelle Uhrzeit in Wien: $(TZ='Europe/Vienna' date +%H:%M) Uhr."
    echo "Der Start von Claude Code wurde abgebrochen, um Kosten zu sparen."
    echo "Nutze 'claude-deepseek.sh --force', wenn du trotzdem arbeiten möchtest."
    # return wird genutzt, falls das Skript gesourct wird (verhindert das
    # Schließen des Terminals); exit greift beim normalen Ausführen.
    return 1 2>/dev/null || exit 1
fi

if [ "$is_peak" = true ] && [ "$force_start" = true ]; then
    echo -e "\033[0;33m⚠️ Peak-Zeit aktiv, aber Start wird erzwungen (--force)...\033[0m"
    # --force aus den Argumenten entfernen, bevor sie an claude weitergereicht werden
    set -- "${@/--force/}"
fi

# 3. Kontostand abfragen und ausgeben (DeepSeek API)
echo "🔄 Rufe DeepSeek-Kontostand ab..."
balance_json=$(curl -s -L -X GET 'https://api.deepseek.com/user/balance' \
    -H 'Accept: application/json' \
    -H "Authorization: Bearer $DEEPSEEK_KEY")

if [[ $balance_json == *"total_balance"* ]]; then
    total_balance=$(echo "$balance_json" | grep -o '"total_balance"[[:space:]]*:[[:space:]]*"[^"]*' | head -1 | grep -o '[^"]*$')
    currency=$(echo "$balance_json" | grep -o '"currency"[[:space:]]*:[[:space:]]*"[^"]*' | head -1 | grep -o '[^"]*$')
    echo -e "\033[0;32m💰 Aktuelles Guthaben: $total_balance $currency\033[0m"
else
    echo "⚠️ Kontostand konnte nicht geladen werden (API-Fehler)."
fi

# 4. Env Vars für die aktuelle Terminal-Session exportieren
echo "🚀 Setze Umgebungsvariablen für Claude Code..."
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_AUTH_TOKEN="$DEEPSEEK_KEY"
export ANTHROPIC_MODEL="deepseek-v4-pro"
export ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-v4-pro"
export ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-v4-pro"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-v4-flash"
export CLAUDE_CODE_SUBAGENT_MODEL="deepseek-v4-flash"
export CLAUDE_CODE_EFFORT_LEVEL="max"
export CLAUDE_CODE_AUTO_COMPACT_WINDOW="786432"

# 5. Claude Code direkt im Anschluss starten
claude "$@"
