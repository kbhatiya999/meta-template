#!/usr/bin/env bash
# Bootstrap a new meta repo from kbhatiya999/harbor.
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/kbhatiya999/harbor/main/setup.sh)
set -euo pipefail

REPO="kbhatiya999/harbor"
PY_PKG="harbor-meta"
GO_MOD="github.com/${REPO}"

# ── prefer uvx (Python, no install step) ─────────────────────────────────────

if command -v uvx &>/dev/null; then
  exec uvx --from "$PY_PKG" harbor "$@"
fi

# ── then npx (Node, no install step) ─────────────────────────────────────────

if command -v npx &>/dev/null; then
  exec npx --yes "@kbhatiya999/harbor" "$@"
fi

# ── then go run (Go, no install step) ──────────────────────────────────────

if command -v go &>/dev/null; then
  exec go run "${GO_MOD}@latest" "$@"
fi

# ── detect platform ───────────────────────────────────────────────────────────

OS=$(uname -s | tr '[:upper:]' '[:lower:]')
case "$OS" in
  darwin|linux) ;;
  mingw*|msys*|cygwin*) OS=windows ;;
  *) echo "Unsupported OS: $OS"; exit 1 ;;
esac

ARCH=$(uname -m)
case "$ARCH" in
  x86_64|amd64)    ARCH=amd64 ;;
  aarch64|arm64)   ARCH=arm64 ;;
  *) echo "Unsupported arch: $ARCH"; exit 1 ;;
esac

EXT=""
[ "$OS" = "windows" ] && EXT=".exe"

# ── resolve latest release tag ────────────────────────────────────────────────

TAG=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
      | grep '"tag_name"' | head -1 | cut -d'"' -f4)

if [ -z "$TAG" ]; then
  echo "Could not resolve latest release from ${REPO}."
  exit 1
fi

# ── download binary ───────────────────────────────────────────────────────────

BIN="harbor-${OS}-${ARCH}${EXT}"
URL="https://github.com/${REPO}/releases/download/${TAG}/${BIN}"

TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

echo "Downloading harbor ${TAG} (${OS}/${ARCH})…"
curl -fsSL "$URL" -o "$TMP"
chmod +x "$TMP"

# ── run ───────────────────────────────────────────────────────────────────────

exec "$TMP" "$@"
