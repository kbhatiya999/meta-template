#!/usr/bin/env bash
# Run harbor without installing it.
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/kbhatiya999/meta-template/main/setup.sh)
set -euo pipefail

if ! command -v uvx &>/dev/null; then
  echo "harbor runs on uv. Install it first:"
  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

exec uvx harbor-meta "$@"
