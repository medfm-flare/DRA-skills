---
name: slurm-job
description: "Create or edit Alliance Canada sbatch scripts. Use for job directives, resource sizing, or launch commands; use submit-experiment to submit a run."
allowed-tools: Read Edit Write Glob Grep Bash(bash -n *) Bash(ssh *) Bash(sshare *) Bash(sacctmgr *) Bash(sinfo *) Bash(hostname *)
---

# Prepare an Alliance Sbatch Script

Produce a script at the requested path (default `job.sh`) for the user's target
cluster and workload. Use the supplied command, config, and existing script to
resolve requirements; ask only for choices that cannot be inferred safely.
This skill prepares scripts. Use `submit-experiment` for an authorized submission.

Load `ccdb-clusters` for the target cluster's directives and resource sizing.
Use its template reference for a new script or complex launch, billing guidance
when choosing an account, and storage guidance when staging data. Do not load
unrelated references for a small script edit.

## Required properties

- An eligible account, explicit time limit, and workload-appropriate CPU, memory,
  and GPU requests. Respect an explicit eligible account; otherwise query current
  associations/fair share on the cluster. Mark unresolved values as placeholders.
- On Fir, request GPUs only with `--gpus-per-node=<gpu_type>:<count>`, never
  `--partition`, `--gres`, or `--constraint`. Omit GPU directives for CPU-only jobs.
- Persistent stdout/stderr paths such as `logs/%x_%j.out` and `.err`. Ensure their
  parent directory exists **before sbatch**; creating it inside the job is too late.
- Module/venv setup, correct working directory, and the user's actual launch command.
  Preserve an existing script's error handling; use appropriate failure propagation
  in a new script.
- Large outputs go to `$SCRATCH` or `$PROJECT`. Copy required node-local results
  back before exit. Do not treat scratch as a permanent archive.

Use measurements from a prior run or an authorized smoke test to size new work.
Preparing a script alone does not authorize launching a sizing job. For unmeasured
workloads, explain provisional resource choices and the smoke test needed before scaling.

Check shell syntax after edits without executing the workload. Report the saved
script, unresolved inputs, and material sizing choices. Include post-run `seff`
guidance when resource tuning is relevant. Do not add arrays, email, distributed
launch, or other features unless the workload or request needs them.
