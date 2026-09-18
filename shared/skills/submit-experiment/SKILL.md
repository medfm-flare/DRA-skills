---
name: submit-experiment
description: "Prepare and submit Slurm experiments with config snapshots and code provenance. Use when asked to launch a tracked run or submit an existing job script."
argument-hint: "<job_type> <run_config_or_script> [purpose description]"
allowed-tools: Read Edit Write Glob Grep Bash(sbatch *) Bash(salloc *) Bash(srun *) Bash(seff *) Bash(squeue *) Bash(sacct *) Bash(ssh *) Bash(git *) Bash(cp *) Bash(mkdir *) Bash(hostname *) Bash(bash -n *)
---

# Submit a Tracked Experiment

Prepare a reviewable run, submit within the user's authorized scope, and record
the scheduler receipt. `metadata.yaml` owns status and provenance; reports and
indexes are derived. Inputs may be a job script, config, job type, and purpose.
Use supplied context rather than requiring a questionnaire.

## Prepare the run

Read the relevant project instructions, input config/script, and prior run when
needed for naming or lineage. Use the existing experiment layout, or
[references/experiment-layout.md](references/experiment-layout.md) for the default
layout and canonical schema. Do not duplicate that schema in another document.

Resolve the target cluster, execution host, eligible account, resources, command,
and logs. Use `connect` if SSH access needs restoring and `slurm-job` if the script
needs editing. Apply the target guidance in `ccdb-clusters`; check live Fir
availability before a large submission. Ensure log directories exist before sbatch.

For a new unmeasured workload, use a bounded smoke test on the smallest feasible
profile before scaling. A request to draft a script does not authorize a smoke
job. Reuse relevant prior measurements instead of repeating a sizing test for an
unchanged workload. Read the cluster iteration reference when designing the test.

Choose a unique run code and infer the goal, tags, and lineage from evidence.
Record unknown expected metrics as null; do not invent scientific targets.
Snapshot the config and script, capture the actual executed checkout's Git commit
and dirty state, and prepare the narrative stub. Use `status: prepared` until
Slurm accepts a job. Capture staged and unstaged tracked changes and relevant
untracked inputs; a commit hash plus an unstaged-only diff is not reproducible.

## Submission boundary

Show the concrete run code, target, account, resource/time bounds, objective,
provenance limitations, and command before launching. If the user already
authorized this run and its bounds, proceed without asking again. Otherwise ask
for the unresolved launch decision after preparation is complete. A changed
target, materially larger allocation, or additional run needs authorization when
outside the established scope. Respect a requested review-only or dry-run boundary.

Use the established remote checkout or agreed file transfer for remote work.
Submission does not implicitly authorize `git push`, overwriting remote changes,
or committing unrelated files. Verify the remote code/config matches the snapshot.

## Submit and reconcile

Run `sbatch --parsable <script>` on the target submission host from the correct
working directory. Save the returned job ID immediately, then set `submitted`
and the submission timestamp in metadata. Use the prepared script/config snapshot
or verify that the submitted inputs are identical. Record every authorized smoke,
train, or evaluation job in its intended run/stage.

If sbatch or SSH fails after it may have reached the scheduler, check the saved
receipt and `squeue`/`sacct` by user, run name, and submission time before retrying.
An uncertain result must not create a duplicate job. Keep status
`submission_unknown` until reconciled; a definite rejection is `submission_failed`.
Do not describe either as a running or failed workload.

Completion means the scheduler receipt and metadata agree. Report run code, job
ID, target, metadata path, and usable log command. Do not wait for training to
finish unless the user requested monitoring or end-to-end results.
