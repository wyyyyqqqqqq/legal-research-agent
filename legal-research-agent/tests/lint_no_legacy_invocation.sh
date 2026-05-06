#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Runtime instructions should not reference old agent IDs. Migration docs and
# tests may mention them for comparison, so this lint scans only runtime files.
SCAN_PATHS=(
  "$ROOT_DIR/CLAUDE.md"
  "$ROOT_DIR/skills"
  "$ROOT_DIR/scripts"
  "$ROOT_DIR/templates"
  "$ROOT_DIR/knowledge"
)

if grep -R -n -E 'general-legal-research|game-legal-research' "${SCAN_PATHS[@]}"; then
  echo "FAIL: forbidden legacy agent ID found in runtime files" >&2
  exit 1
fi

echo "OK: no legacy agent IDs in runtime files"
