#!/usr/bin/env python3
"""Claude Code statusline.

Reads session JSON on stdin (see https://code.claude.com/docs/en/statusline)
and prints two plain-text rows:

    1. current directory (with git branch) · session/thread id
    2. model + reasoning effort · context usage (used% / window size)
       · rate-limit bars for the 5-hour and weekly windows

Segments on a row are joined by a middot. The git branch is appended only
inside a repo; the rate-limit segment is appended only once that data is
available (after the first API response, Pro/Max accounts only).
"""

import json
import os
import subprocess
import sys
import time

SEP = " · "
BAR_WIDTH = 8


def pretty_model(model: dict) -> str:
    """claude-opus-4-8 -> 'Opus 4.8'; falls back to display_name."""
    mid = model.get("id") or ""
    parts = mid.split("-")
    if parts and parts[0] == "claude":
        parts = parts[1:]
    # Drop a trailing date token like 20251001.
    if len(parts) > 1 and parts[-1].isdigit() and len(parts[-1]) >= 6:
        parts = parts[:-1]
    if parts:
        family = parts[0].capitalize()
        version = ".".join(p for p in parts[1:] if p.isdigit())
        return f"{family} {version}".strip()
    return model.get("display_name") or "?"


def git_branch(cwd: str) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", cwd, "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return ""


def bar(pct: float) -> str:
    filled = min(BAR_WIDTH, max(0, round(pct / 100 * BAR_WIDTH)))
    return "━" * filled + "─" * (BAR_WIDTH - filled)


def until(resets_at) -> str:
    """Compact time-to-reset, e.g. '4h7m' or '5d10h'."""
    if not resets_at:
        return ""
    secs = max(0, int(resets_at) - int(time.time()))
    days, rem = divmod(secs, 86400)
    hours, rem = divmod(rem, 3600)
    mins = rem // 60
    if days:
        return f"{days}d{hours}h"
    if hours:
        return f"{hours}h{mins}m"
    return f"{mins}m"


def rate_limit_line(data: dict) -> str:
    """Second row: '5h ━━──── 1% [4h7m] | Week ──────── 3% [5d10h]'."""
    limits = data.get("rate_limits") or {}
    parts = []
    for key, label in (("five_hour", "5h"), ("seven_day", "Week")):
        window = limits.get(key)
        if not window:
            continue
        pct = window.get("used_percentage")
        if pct is None:
            continue
        eta = until(window.get("resets_at"))
        eta = f" [{eta}]" if eta else ""
        parts.append(f"{label} {bar(pct)} {round(pct)}%{eta}")
    return " | ".join(parts)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    # Line 1: current-dir (+ branch) · thread-id
    cwd = (data.get("workspace") or {}).get("current_dir") or data.get("cwd") or ""
    home = os.path.expanduser("~")
    shown = "~" + cwd[len(home) :] if home and cwd.startswith(home) else cwd
    branch = git_branch(cwd) if cwd else ""
    if branch:
        shown = f"{shown} ({branch})"
    line1 = [shown]
    session_id = data.get("session_id") or ""
    if session_id:
        line1.append(session_id)

    # Line 2: model-with-reasoning · context-used (e.g. '0.0%/400K')
    label = pretty_model(data.get("model") or {})
    effort = (data.get("effort") or {}).get("level")
    if effort:
        label = f"{label} {effort}"
    ctx = data.get("context_window") or {}
    pct = ctx.get("used_percentage") or 0
    size_k = round((ctx.get("context_window_size") or 200000) / 1000)
    line2 = [label, f"{pct:.1f}%/{size_k}K"]

    # Line 2 also carries rate limits once available.
    rate_line = rate_limit_line(data)
    if rate_line:
        line2.append(rate_line)

    print(SEP.join(line1))
    print(SEP.join(line2))


if __name__ == "__main__":
    main()
