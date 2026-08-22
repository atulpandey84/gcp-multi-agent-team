#!/usr/bin/env bash
set -euo pipefail

if command -v python3 >/dev/null 2>&1; then
  python3 scripts/bootstrap.py "$@"
elif command -v python >/dev/null 2>&1; then
  python scripts/bootstrap.py "$@"
else
  echo "Python 3.11+ is required. Install Python and enable it on PATH." >&2
  exit 1
fi
