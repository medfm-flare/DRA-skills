---
name: connect
description: "Establish or restore SSH access to Fir from an already configured machine. Use for connection checks or expired sessions; use onboard for first-time key setup."
allowed-tools: Read Bash(ssh *) Bash(hostname *) Bash(whoami) Bash(sinfo *) Bash(${CLAUDE_SKILL_DIR}/scripts/*)
---

# Connect to Fir

Establish a verified shell and Slurm path using the existing SSH configuration.
Do not generate or upload keys here; use `onboard` for missing setup or newly
registered keys. Never collect passwords, key passphrases, or Duo codes.

## Choose the execution path

Check `hostname -f` and the intended target. On the target cluster, verify `whoami`
and `sinfo --version` locally. Being on a different Alliance cluster does not
mean Fir commands should run there.

From a laptop, inspect the effective SSH configuration for `fir.alliancecan.ca`
(`ssh -G` accounts for aliases and Include files). If the username or key is
missing or rejected, use the relevant onboarding setup guidance.

## Reuse or restore the connection

- **Unix with a live master:** `ssh -O check fir.alliancecan.ca`, then verify
  `ssh fir.alliancecan.ca 'hostname -f; whoami; sinfo --version'`.
- **Unix with an expired master:** tell the user a Duo push is coming, then run
  [scripts/warm-socket.sh](scripts/warm-socket.sh) with `fir.alliancecan.ca` using
  its resolved absolute path. It requires `timeout` and an available SSH key.
  If the helper fails, stop automatic retries and have the user run
  `ssh fir.alliancecan.ca` in their own terminal, then verify again.
- **Windows or incompatible multiplexing:** read [references/windows.md](references/windows.md)
  for the bundled askpass path and stale-socket bypass flags. Batch related
  commands into one connection to avoid repeated Duo pushes.

The helper selects a Duo option; only the user approves authentication. A locked
key must be unlocked by the user in their terminal or SSH agent. A Duo prompt
means the key was accepted, not that onboarding must be repeated.

Finish by reporting the verified host/user and whether subsequent commands run
locally or over SSH. If blocked, identify the failed stage and the single user
action needed. Do not claim a connection succeeded without remote output.
