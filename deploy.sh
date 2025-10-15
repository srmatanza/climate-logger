#!/usr/bin/env bash
set -e

PICO_MOUNT="/Volumes/CIRCUITPY"
SETTINGS_TEMPLATE="settings.template.toml"
SETTINGS_FILE="$PICO_MOUNT/settings.toml"

echo "Installing/updating CircuitPython libs..."
uv run --extra dev circup install -r requirements.txt

echo "Generate settings.toml from template and copying to device..."
uv run --extra dev python3 scripts/generate_settings.py "$SETTINGS_TEMPLATE" "$SETTINGS_FILE"

echo "Copying code.py to device..."
cp code.py "$PICO_MOUNT/code.py"

echo "Done!"
