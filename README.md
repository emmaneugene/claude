# Claude Code config

Global configuration for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

Clone or symlink this repo to `~/.claude` to apply settings, skills, and behavior instructions across all Claude Code sessions.

```sh
git clone <repo-url> ~/.claude
# or
ln -s /path/to/this/repo ~/.claude
```

## What's here

- **`CLAUDE.md`** — Global instructions injected into every Claude Code session
- **`settings.json`** — Model, permissions, and UI preferences
- **`skills/`** — Custom skills (see https://github.com/emmaneugene/agents)
