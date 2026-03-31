#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" == "Darwin" ]]; then
  exec pbpaste
fi

if [[ "$(uname -s)" == "Linux" ]]; then
  if [[ -n "${WAYLAND_DISPLAY:-}" ]] && command -v wl-paste >/dev/null 2>&1; then
    exec wl-paste --no-newline
  fi

  if command -v xclip >/dev/null 2>&1; then
    exec xclip -selection clipboard -o
  fi

  if command -v xsel >/dev/null 2>&1; then
    exec xsel --clipboard --output
  fi
fi

echo "No supported clipboard read command found (expected pbpaste, wl-paste, xclip, or xsel)." >&2
exit 1
