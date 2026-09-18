# Codex Adapter

Skills are available by name or `$skill-name`; shared `/skill-name` examples refer
to the same skill. Codex uses `AGENTS.md` for these rules, not Claude settings or hooks.

Resolve skill-relative references and scripts from the loaded skill's directory.
`${CLAUDE_SKILL_DIR}` examples mean that directory; do not assume the variable is
set in Codex. Locate another installed skill before using its resources.

Complete authorized inspection, local edits, and relevant validation without
repeated confirmation. A read-only request does not authorize job submission,
cancellation, data cleanup, or Git publication. Ask only for missing decisions
or actions outside the user's established scope.
