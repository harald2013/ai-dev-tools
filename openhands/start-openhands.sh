#!/usr/bin/env bash
# Start OpenHands Agent Canvas. Stack definition: openhands/compose.yml.
# Stop with ./tools/stop-openhands.sh.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_FILE="${REPO_ROOT}/openhands/compose.yml"
CONFIG_DIR="${REPO_ROOT}/openhands/.openhands"

is_wsl() {
    [[ -n "${WSL_DISTRO_NAME:-}" ]] || grep -qi microsoft /proc/version 2>/dev/null
}

wsl_ipv4() {
    ip -4 -o addr show eth0 2>/dev/null | awk '{print $4}' | cut -d/ -f1
}

compose() {
    docker compose -f "${COMPOSE_FILE}" "$@"
}

mkdir -p "${CONFIG_DIR}"
export OPENHANDS_UID="$(id -u)"
export OPENHANDS_GID="$(id -g)"

echo "Starting OpenHands Agent Canvas..."
compose up -d --wait --wait-timeout 600 --pull missing

PORT="$(compose port agent-canvas 8000 2>/dev/null | awk -F: '{print $NF}' | head -1)"
PORT="${PORT:-18040}"

echo ""
echo "OpenHands Agent Canvas is running."
echo "  UI:       http://127.0.0.1:${PORT}/canvas"
echo "  Backend:  http://127.0.0.1:${PORT}"
echo "  Stack:    ${COMPOSE_FILE}"
if is_wsl; then
    echo "  Windows:  http://127.0.0.1:${PORT}/canvas  (not localhost — that is IPv6)."
    WSL_IP="$(wsl_ipv4)"
    if [[ -n "${WSL_IP}" ]]; then
        echo "  WSL IP:   http://${WSL_IP}:${PORT}/canvas"
    fi
fi
echo ""
echo "Stop with: ./tools/stop-openhands.sh"
