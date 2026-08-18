#!/usr/bin/env bash
# Tear down the OpenHands Agent Canvas stack from openhands/compose.yml.
# Bind mounts (openhands/.openhands, openhandswork/) stay.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_FILE="${REPO_ROOT}/openhands/compose.yml"

echo "Stopping OpenHands Agent Canvas..."
docker compose -f "${COMPOSE_FILE}" down

echo "Done."
