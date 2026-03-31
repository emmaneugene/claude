---
name: publish-gist
description: Publishes markdown files as GitHub Gists using the gh CLI, automatically detecting and embedding referenced local images and GIFs. Use when asked to publish, share, or create a gist from a markdown file.
---

# Publish Markdown as GitHub Gist

Publish a markdown file as a GitHub Gist. Local images and GIFs referenced in the markdown are included in the gist, and their paths are rewritten to raw GitHub URLs so they render correctly.

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`)
- `git` installed
- Python 3

## Usage

```bash
python3 publish-gist.py <markdown-file> [--name "filename"] [--public] [--desc "description"] [--web]
```

Run the script from this skill's directory using its absolute or relative path.

### Options

| Flag | Description |
|------|-------------|
| `--name "..."` | Custom filename for the markdown in the gist (default: original filename). The gist title is the first filename alphabetically, so this controls the gist's display name. `.md` is appended if missing. |
| `--public` | Make the gist publicly listed (default: secret/unlisted) |
| `--desc "..."` | Set a description for the gist |
| `--web` | Open the gist in a browser after creation |

### Examples

```bash
# Publish a private gist
python3 /path/to/publish-gist/publish-gist.py ./notes/writeup.md

# Publish a public gist with a description and custom name
python3 /path/to/publish-gist/publish-gist.py ./docs/guide.md --name "Setup Guide" --public --desc "Setup guide"

# Publish and open in browser
python3 /path/to/publish-gist/publish-gist.py ./report.md --web
```

## How It Works

1. **Parse** -- Scans the markdown for local image/GIF references in both `![alt](path)` and `<img src="path">` syntax. Remote URLs are left untouched.
2. **Resolve** -- Resolves each image path relative to the markdown file's directory. Missing files are warned about and skipped.
3. **Create** -- Uses `gh gist create` to create the gist with just the markdown file.
4. **Clone** -- Clones the gist's git repo (every gist is a git repo), copies images in with sanitized flat filenames, commits, and pushes. This is how binary files get into the gist since `gh gist create` does not support them.
5. **Rewrite** -- Constructs stable raw.githubusercontent.com URLs for each image and rewrites the references in the markdown.
6. **Update** -- Uses `gh gist edit` to replace the markdown with the rewritten version so images render correctly on GitHub.

## Workflow for the Agent

1. Identify the markdown file the user wants to publish.
2. Ask the user if they want it public or private (default: private).
3. Ask for an optional description.
4. Run the script:
   ```bash
   python3 /absolute/path/to/publish-gist/publish-gist.py "/path/to/file.md" [flags]
   ```
5. Report the gist URL back to the user.

## Troubleshooting

- **`gh` not authenticated**: Run `gh auth login`.
- **Images not rendering**: Ensure image paths in the markdown are relative to the markdown file's location. Absolute paths or paths relative to a different root won't resolve.
- **Binary file warnings**: GitHub Gists support binary files (png, gif, jpg, etc.) -- these are expected.
