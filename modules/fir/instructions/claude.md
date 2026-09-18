# Fir Claude Code Adapter

Use `/slurm-status` for live Fir capacity, `/connect` to restore SSH access, and
`/onboard` for first-time setup. Use `/slurm-job` to prepare scripts and
`/submit-experiment` for authorized tracked submissions.

Resolve bundled helpers from `${CLAUDE_SKILL_DIR}`. If authentication requires
an interactive terminal, the user can run `! ssh fir.alliancecan.ca` in Claude
Code; the assistant then verifies and reuses the connection.

Claude's node-context hook supplements the shared compute rules. The Fir GPU,
storage, and submission constraints in the shared instructions still apply.
