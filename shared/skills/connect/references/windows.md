# Windows SSH and Duo Push


On Windows, `ssh -O check` may report `No ControlPath specified`, `Not a socket`, or another
ControlMaster failure. Use the bundled askpass helper to select **Duo Push** automatically. The
helper never approves the second factor: tell the user that a push is coming, and they must approve
it on their own device. Never ask for a Duo passcode in chat.

Resolve the helper from the user's Codex home so the command is portable across Windows accounts.
`SSH_ASKPASS` is an executable-path value, so keep the environment value unquoted. PowerShell
preserves spaces in the assigned string; embedded quote characters would become part of the path:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$askpassPath = Join-Path $codexHome 'skills\connect\scripts\fir-duo-push-askpass.cmd'
if (-not (Test-Path -LiteralPath $askpassPath -PathType Leaf)) {
    throw "SSH askpass helper not found: $askpassPath"
}
$env:SSH_ASKPASS = $askpassPath
$env:SSH_ASKPASS_REQUIRE = 'force'
$env:DISPLAY = 'codex'
ssh -o ControlMaster=no -o ControlPath=none fir.alliancecan.ca "hostname -f && whoami && sinfo --version 2>&1"
```

`ControlMaster=no` and `ControlPath=none` deliberately bypass stale or incompatible socket settings.
The helper returns an empty response to password and key-passphrase prompts, so an encrypted key
must already be unlocked in `ssh-agent`; otherwise use Mode A in a separate terminal.

Without working multiplexing, every independent SSH connection can trigger another Duo push. Batch
related commands into one connection:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$askpassPath = Join-Path $codexHome 'skills\connect\scripts\fir-duo-push-askpass.cmd'
if (-not (Test-Path -LiteralPath $askpassPath -PathType Leaf)) {
    throw "SSH askpass helper not found: $askpassPath"
}
$env:SSH_ASKPASS = $askpassPath
$env:SSH_ASKPASS_REQUIRE = 'force'
$env:DISPLAY = 'codex'
@'
hostname -f
whoami
squeue -u $(whoami)
'@ | ssh -o ControlMaster=no -o ControlPath=none fir.alliancecan.ca bash -s
```

Avoid parallel `ssh` or `scp` calls from Windows when multiplexing is unavailable or unreliable.
Each connection may send a separate push and can time out while waiting for approval.
