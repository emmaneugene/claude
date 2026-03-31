---
name: clipboard
description: "Interact with system clipboard using native shell tools on macOS or linux."
---

# Clipboard

Use this skill when the user wants you to interact with the system clipboard.

- Prefer **writing** to the clipboard. That is the main use case.
- Only **read** the clipboard when the user explicitly asks for it.
- Use the helper scripts instead of reimplementing OS detection each time.

## Write to clipboard

Pipe the exact text to `write-clipboard.sh` via the `bash` tool.

Use a heredoc for multiline content:

```bash
write-clipboard.sh <<'EOF'
Exact text to copy
EOF
```

For content that already lives in a file, prefer piping the file directly:

```bash
write-clipboard.sh < path/to/file.txt
```

After copying, briefly confirm what was copied.

## Read clipboard

If the user explicitly asks to inspect clipboard contents, run:

```bash
read-clipboard.sh
```

Summarize or quote the clipboard contents as appropriate. No scaffolding or commentary.

## Notes

- These scripts support macOS (`pbcopy`/`pbpaste`) and Linux via Wayland (`wl-copy`/`wl-paste`) or X11 (`xclip`/`xsel`).
- If no supported clipboard backend exists, explain the failure clearly and mention the missing utility.
- Do not create extra files just to copy text unless it's the safest option for large content.
