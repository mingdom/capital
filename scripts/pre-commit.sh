#!/usr/bin/env bash
set -euo pipefail

echo "[pre-commit] Formatting with Black..."
if command -v black >/dev/null 2>&1; then
  black --check .
else
  echo "Black not found in PATH. Did you run 'make dev'?" >&2
  exit 1
fi

echo "[pre-commit] Linting with Ruff..."
if command -v ruff >/dev/null 2>&1; then
  ruff check .
else
  echo "Ruff not found in PATH. Did you run 'make dev'?" >&2
  exit 1
fi

echo "[pre-commit] OK"
