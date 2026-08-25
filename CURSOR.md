# Cursor project notes

`AGENTS.md` is the authoritative repository guide. Cursor loads the project-wide rule in `.cursor/rules/kenkomirai.mdc`, which points agents to both files.

- Search the codebase before accepting an autocomplete or generated abstraction; verify types and APIs against installed manifests and local contracts.
- Keep edits scoped to the active task. Inspect surrounding code and all references before renaming or changing a public type, route, environment variable, or asset.
- Do not generate fake browser data, generic dashboard filler, invented medical claims, or hard-coded localhost navigation.
- For Python changes, preserve the Mesa 3.5 `step(self)`/`run_for` lifecycle described in `AGENTS.md`.
- For frontend changes, preserve same-origin gateway behavior, accessible interactions, responsive layouts, and the charcoal/lavender/blue design system.
- Treat inline suggestions as untrusted until syntax, types, contract effects, and failure paths have been checked.
- Use terminal commands only when permitted. Never install packages, run destructive commands, or start training implicitly.
- Finish with a focused review of changed files and report what was and was not verified.

Update `AGENTS.md` first when shared project rules change. Update this file only for Cursor-specific workflow guidance.
