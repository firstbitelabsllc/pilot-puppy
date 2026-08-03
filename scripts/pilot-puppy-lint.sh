#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -P "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

if command -v ruff >/dev/null 2>&1; then
  exec ruff check scripts tests browser
fi

exec "${ROOT}/scripts/pilot-puppy-python.sh" -m ruff check scripts tests browser
