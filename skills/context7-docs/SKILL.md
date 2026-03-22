---
name: context7-docs
description: "Queries up-to-date library documentation via Context7. Use when asked about library APIs, framework usage, or need current docs."
---

# Context7 Documentation Lookup

Query current documentation for any programming library or framework.

## Workflow

1. First resolve the library ID:
   - Use `mcp__context7__resolve_library_id` with the library name
   - This returns the Context7-compatible library ID

2. Then query the docs:
   - Use `mcp__context7__query_docs` with the resolved library ID
   - Be specific in your query for best results

## Example

```
# Find React hooks documentation
1. resolve_library_id("react", "how to use hooks")
2. query_docs("/facebook/react", "useEffect cleanup examples")
```

## Tips

- Limit to 3 calls per question
- Be specific: "JWT auth in Express.js" not just "auth"
- Include version if needed: "/vercel/next.js/v14.3.0"
