#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" == "Darwin" ]]; then
  exec pbcopy
fi

if [[ "$(uname -s)" == "Linux" ]]; then
  if [[ -n "${WAYLAND_DISPLAY:-}" ]] && command -v wl-copy >/dev/null 2>&1; then
    exec wl-copy
  fi

  if command -v xclip >/dev/null 2>&1; then
    exec xclip -selection clipboard
  fi

  if command -v xsel >/dev/null 2>&1; then
    exec xsel --clipboard --input
  fi
fi

echo "No supported clipboard write command found (expected pbcopy, wl-copy, xclip, or xsel)." >&2
exit 1
