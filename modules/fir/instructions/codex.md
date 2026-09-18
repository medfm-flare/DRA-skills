# Fir Codex Adapter

Use `$slurm-status` for live Fir capacity, `$connect` to restore SSH access, and
`$onboard` for first-time setup. Use `$slurm-job` to prepare scripts and
`$submit-experiment` for authorized tracked submissions.

Resolve bundled helpers from the installed skill directory; do not assume
`${CLAUDE_SKILL_DIR}` is set. If authentication requires an interactive terminal,
the user runs `ssh fir.alliancecan.ca` in their terminal, then Codex verifies
and reuses the connection. Use the connect skill's Windows path where applicable.

Codex receives the shared compute and Fir rules through `AGENTS.md`; it does
not rely on Claude's node-context hook.
