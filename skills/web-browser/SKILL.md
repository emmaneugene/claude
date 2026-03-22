---
name: web-browser
description: "Automates browser interactions with Playwright. Use for web scraping, testing, screenshots, form filling, or browsing pages."
---

# Web Browser Automation

Control a browser via Playwright MCP for web automation tasks.

## Core Workflow

1. **Navigate**: `browser_navigate` to a URL
2. **Snapshot**: `browser_snapshot` to see page structure (better than screenshots for actions)
3. **Interact**: Click, type, select using element refs from snapshot
4. **Capture**: `browser_take_screenshot` for visual records

## Key Tools

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Go to URL |
| `browser_snapshot` | Get accessibility tree (use for interactions) |
| `browser_click` | Click element by ref |
| `browser_type` | Type into input |
| `browser_take_screenshot` | Capture visual |
| `browser_fill_form` | Fill multiple fields |
| `browser_wait_for` | Wait for text/element |
| `browser_close` | Close browser |

## Tips

- Always use `browser_snapshot` before interactions to get element refs
- Use `ref` parameter from snapshot for precise targeting
- Screenshots are for visual verification, snapshots are for actions
