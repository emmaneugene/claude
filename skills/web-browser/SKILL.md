---
name: web-browser
description: Browser automation via Chrome DevTools Protocol. Navigate, evaluate JS, take screenshots, pick elements, and extract content.
---

# Browser Tools

Browser automation using `dev-browser` (Playwright-based) with `cdp` for managing Chrome instances.

## Prerequisites

- `dev-browser` — run `dev-browser --help` for full usage
- `cdp` — run `cdp --help` for full usage

## Two modes

**Daemon-managed** — simplest, no setup needed:
```bash
dev-browser --browser myproject --headless <<'EOF'
const page = await browser.getPage("main");
await page.goto("https://example.com");
EOF
```
`dev-browser` launches and manages its own Chromium. Add `--headless` for unattended runs; omit it to watch the window. Use `dev-browser browsers` to list instances.

**Connect to a cdp-managed Chrome** — use when you need your real browser profile (cookies, logins, extensions) or want to attach to an already-running browser:
```bash
cdp start --name myproject          # blocks until ready; CDP URL printed on stdout
dev-browser --connect http://localhost:9222 <<'EOF'
const page = await browser.getPage("main");
await page.goto("https://example.com");
EOF
cdp stop --name myproject
```

`cdp start` options: omit `--new-profile` to inherit your real profile, use `--name` for multiple instances, `--headless` for unattended runs.

## Inspecting pages

Use `page.snapshotForAI()` to get an AI-optimised accessibility tree for element discovery — prefer this over screenshots or raw HTML when you need to find and interact with elements.
