# Claude Code Adapter

Use `/skill-name` for skills; `slurm-queue`, `slurm-resource`, and `slurm-storage`
are also available as agents. Resolve bundled helpers from `${CLAUDE_SKILL_DIR}`.

`settings.json` configures permissions, statusline, and hooks. The node-context
hook is advisory; the shared login-node rules still apply.

Complete authorized inspection, local edits, and relevant validation without
repeated confirmation. A read-only request does not authorize job submission,
cancellation, data cleanup, or Git publication.
