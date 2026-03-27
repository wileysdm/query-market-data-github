#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PACKAGE_DIR=$(dirname -- "$SCRIPT_DIR")
SRC_DIR="$PACKAGE_DIR/query-market-data"
TARGET_DIR="$HOME/.codex/skills/query-market-data"

if [ ! -d "$SRC_DIR" ]; then
  echo "Source skill directory not found: $SRC_DIR" >&2
  exit 1
fi

mkdir -p "$HOME/.codex/skills"
rm -rf "$TARGET_DIR"
cp -R "$SRC_DIR" "$TARGET_DIR"

echo "Installed to: $TARGET_DIR"
echo "Next: copy query-market-data/references/ck_config.example.py to your own ck_config.py"
echo "Then set: export MARKET_CH_CONFIG=/path/to/your/ck_config.py"
echo "Finally restart Codex."
