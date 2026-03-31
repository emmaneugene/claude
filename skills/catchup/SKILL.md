---
name: catchup
description: >
  Fetches remote and summarises what changed on updated branches since last
  fetch. Use when asked to catch up on a repo, see what changed upstream,
  or review recent remote activity.
---

# Git Catchup

Fetch the remote and produce a scannable summary of what changed on each
updated branch.

## Script

A single helper script with two subcommands:

| Command | Purpose | Output |
|---|---|---|
| `catchup.py fetch` | Snapshot → fetch → compare | TSV: `STATUS OLD_SHA NEW_SHA REF` per changed branch |
| `catchup.py range <ref>` | Look up saved SHAs for one branch | `OLD_SHA..NEW_SHA REF N_COMMITS` |

Always run these rather than reimplementing the snapshot logic manually.

## Workflow

### 1. Snapshot & Fetch

```bash
uv run skills/catchup/catchup.py fetch
```

Output is TSV with one line per changed branch:
```
updated  <old-sha>  <new-sha>  refs/remotes/origin/main
new      0000...    <new-sha>  refs/remotes/origin/feature-x
deleted  <old-sha>  0000...    refs/remotes/origin/old-branch
```

Default excluded patterns: `dependabot/`, `renovate/`, `snyk-`, `gh-pages`.
Pass extra patterns with `--exclude`:
```bash
uv run skills/catchup/catchup.py fetch --exclude "release-" --exclude "wip/"
```

To get the commit range for a specific branch:
```bash
uv run skills/catchup/catchup.py range origin/main
# → <old-sha>..<new-sha>  refs/remotes/origin/main  7
```

Deleted branches can be noted but don't need summaries.

### 2. Present the list

For each updated branch, show: **branch name** and **number of new commits**.

Sort by most-recent commit date, descending.

- **≤ 5 branches**: proceed to summarise all of them.
- **> 5 branches**: show the list and ask the user which ones to
  summarise. Accept numbers, branch names, `all`, or a grep pattern.

### 3. Summarise each selected branch

For each branch, look at **at most 20** new commits (the most recent ones
if there are more).

**Start cheap, escalate if needed:**

1. Read commit messages and `git diff --stat` for the commit range:
   ```bash
   git log --oneline <old-sha>..<new-sha> -20
   git diff --stat <old-sha>..<new-sha>
   ```
2. If the commit messages are low-signal (e.g. dominated by "fix", "wip",
   "update", merge commits, or squash blobs with no meaningful body),
   read the actual diffs for those unclear commits:
   ```bash
   git diff <old-sha>..<new-sha> -- <relevant paths>
   ```
   Keep it targeted — use the diffstat to pick the interesting files
   rather than dumping everything.

**Per branch, produce:**

- A **one-line TLDR** (what this batch of changes is about)
- Concise **bullets** for notable changes
- Mention of any large-scale operations (renames, deletions, new modules)

### 4. Output format

```
## <branch-name> (N new commits)

TLDR: <one sentence>

- bullet 1
- bullet 2
```

Group all branch summaries together. No filler, no recap of the process.
If a branch has > 20 new commits, note how many were skipped at the end of
its section.
