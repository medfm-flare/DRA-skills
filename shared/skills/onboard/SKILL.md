---
name: onboard
description: "Install DRA configuration and set up first-time Alliance Canada SSH access for Claude Code or Codex. Use for a new machine or a newly registered key."
allowed-tools: Read Edit Write Bash(git clone *) Bash(hostname *) Bash(whoami) Bash(ssh *) Bash(ssh-keygen *) Bash(sshare *) Bash(sacctmgr *) Bash(mkdir *) Bash(chmod *) Bash(*/setup.sh *)
---

# Set Up DRA Skills

Install this bundle for the user's chosen assistant and establish Alliance SSH
access when needed. SSH identity and the Slurm allocation account are separate.
An installation request authorizes the described configuration work; ask only
for unresolved identity, target, or account choices.

## Discover existing setup

Use the current checkout when it contains `setup.sh`; otherwise locate the user's
DRA checkout. If cloning is needed, use
`https://github.com/medfm-flare/DRA-skills` (the usual destination is `~/DRA-config`).
Respect an explicit Claude/Codex choice. If unspecified, detect `~/.claude` and
`~/.codex` and configure the initialized tools. A missing tool directory requires
the user to run that tool once. Claude additionally needs `python3` and `jq`.

Check the actual hostname and target. Already on the target cluster: use local
Slurm queries. On a laptop: reuse working SSH via `connect`. Read
[references/fir-ssh-setup.md](references/fir-ssh-setup.md) only for first-time
key registration, SSH configuration, key-format issues, or failed authentication.

Preserve existing keys and unrelated SSH configuration. Register only the public
key; the user handles CCDB login, private-key passphrases, and Duo approval.
Newly registered keys can take time to propagate; do not keep retrying login or
replace a key merely because it has not propagated yet.

## Configure and verify

After shell access is verified, query the cluster username and `sshare -U -l
--parsable2`. Select an eligible allocation for the user's project; use the
`ccdb-clusters` account helper when a choice is needed. Do not infer Alliance
identity from the laptop username or require a ControlMaster socket on Windows.

Show the resolved target, username, account, and assistant targets. Preserve other
saved values while updating `<repo>/build/.env.local`:

```text
FIR_USERNAME=<cluster username>
FIR_ACCOUNT=<eligible GPU account>
FIR_GPU_TYPE=<chosen GPU type>
```

Run from that checkout:

```bash
./setup.sh --modules fir --targets <claude|codex|claude,codex> --non-interactive
```

Verify the selected tool's managed instruction block and installed skill links,
including the generated `slurm-status` skill. Preserve content outside the lab
markers. Report what was installed and any remaining authentication prerequisite.
Installation is complete when the links and configuration are valid; a full
routing evaluation or a real Slurm job is not required for ordinary onboarding.

For changes to skill descriptions, use the repository's `evals/routing-trigger.json`
as a separate routing check. For later SSH expiry use `connect`; for updates rerun
the installer with the same selected targets after updating the checkout.
