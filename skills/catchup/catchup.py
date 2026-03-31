#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# ///
"""
Git catchup helper — fetch remote and report which branches changed.

Subcommands:
  fetch   Snapshot refs, fetch, compare. Prints TSV of changed branches.
  range   Look up the commit range for a specific branch from last fetch.

Usage:
  uv run catchup.py fetch [--exclude PATTERN ...]
  uv run catchup.py range <branch>
"""

import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path

ZERO = "0" * 40

DEFAULT_EXCLUDES = ["dependabot/", "renovate/", "snyk-", "gh-pages"]


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def git_ok(*args: str) -> tuple[bool, str]:
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip()


def repo_tmp_prefix() -> str:
    toplevel = git("rev-parse", "--show-toplevel")
    h = hashlib.sha1(toplevel.encode()).hexdigest()[:8]
    return os.path.join("/tmp", f"catchup-{h}")


def snapshot_path(label: str) -> Path:
    return Path(f"{repo_tmp_prefix()}-{label}.txt")


def read_snapshot(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    refs = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        ref, sha = line.split(None, 1)
        refs[ref] = sha
    return refs


def get_refs() -> dict[str, str]:
    output = git("for-each-ref", "--format=%(refname) %(objectname)", "refs/remotes/")
    refs = {}
    for line in output.splitlines():
        if not line.strip():
            continue
        ref, sha = line.split(None, 1)
        refs[ref] = sha
    return refs


def should_exclude(ref: str, patterns: list[str]) -> bool:
    ref_lower = ref.lower()
    return any(p.lower() in ref_lower for p in patterns)


def cmd_fetch(args: argparse.Namespace) -> None:
    exclude = DEFAULT_EXCLUDES + (args.exclude or [])

    # Snapshot before
    before = get_refs()
    before_path = snapshot_path("before")
    before_path.write_text(
        "\n".join(f"{ref} {sha}" for ref, sha in before.items()) + "\n"
    )

    # Fetch
    try:
        subprocess.run(
            ["git", "fetch", "--all", "--prune", "--jobs=4", "--no-tags", "--quiet"],
            capture_output=True, check=True,
        )
    except subprocess.CalledProcessError:
        subprocess.run(
            ["git", "fetch", "--all", "--prune", "--jobs=4", "--no-tags"],
            capture_output=True,
        )

    # Snapshot after
    after = get_refs()
    after_path = snapshot_path("after")
    after_path.write_text(
        "\n".join(f"{ref} {sha}" for ref, sha in after.items()) + "\n"
    )

    # Compare
    all_refs = set(before) | set(after)
    for ref in sorted(all_refs):
        old = before.get(ref, ZERO)
        new = after.get(ref, ZERO)

        if old == new:
            continue
        if should_exclude(ref, exclude):
            continue

        if old == ZERO:
            status = "new"
        elif new == ZERO:
            status = "deleted"
        else:
            status = "updated"

        print(f"{status}\t{old}\t{new}\t{ref}")


def cmd_range(args: argparse.Namespace) -> None:
    ref = args.branch
    if not ref.startswith("refs/"):
        ref = f"refs/remotes/{ref}"

    before_path = snapshot_path("before")
    after_path = snapshot_path("after")

    if not before_path.exists() or not after_path.exists():
        print("No snapshot found. Run 'fetch' first.", file=sys.stderr)
        sys.exit(1)

    before = read_snapshot(before_path)
    after = read_snapshot(after_path)

    old = before.get(ref, ZERO)
    new = after.get(ref, ZERO)

    if old == new:
        print(f"Branch '{ref}' did not change in the last fetch.", file=sys.stderr)
        sys.exit(1)

    if new == ZERO:
        print(f"Branch '{ref}' was deleted.", file=sys.stderr)
        sys.exit(1)

    if old == ZERO:
        # New branch — find merge-base against default branch
        ok, base = git_ok("merge-base", "origin/HEAD", new)
        if ok and base:
            ok2, n = git_ok("rev-list", "--count", f"{base}..{new}")
            count = n if ok2 else "?"
            print(f"{base}..{new}  {ref}  {count}")
        else:
            print(f"{ZERO}..{new}  {ref}  (new branch, no merge-base)")
        return

    ok, n = git_ok("rev-list", "--count", f"{old}..{new}")
    count = n if ok else "?"
    print(f"{old}..{new}  {ref}  {count}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Git catchup helper")
    sub = parser.add_subparsers(dest="command", required=True)

    fetch_p = sub.add_parser("fetch", help="Fetch and show changed branches")
    fetch_p.add_argument(
        "--exclude", "-x", action="append", default=[],
        help="Extra patterns to exclude (can be repeated)",
    )

    range_p = sub.add_parser("range", help="Show commit range for a branch")
    range_p.add_argument("branch", help="Branch name (e.g. origin/main)")

    args = parser.parse_args()

    ok, _ = git_ok("rev-parse", "--is-inside-work-tree")
    if not ok:
        print("Not a git repository.", file=sys.stderr)
        sys.exit(1)

    if args.command == "fetch":
        cmd_fetch(args)
    elif args.command == "range":
        cmd_range(args)


if __name__ == "__main__":
    main()
