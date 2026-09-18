---
name: ccdb-clusters
description: "Alliance Canada cluster rules and references for Slurm resources, software, storage, and billing. Use when cluster-specific guidance is needed for HPC work."
allowed-tools: Read Bash(hostname *) Bash(ssh *) Bash(sshare *) Bash(sinfo *) Bash(scontrol *) Bash(seff *) Bash(${CLAUDE_SKILL_DIR}/scripts/*)
---

# Alliance Canada Cluster Guidance

Use the user's target cluster. Identify it from `$CC_CLUSTER`, the SSH target,
or hostname; do not switch clusters based only on job duration. A local `/home`
or `/scratch` path alone does not establish an Alliance environment.

## Operating constraints

- Check hostname and `SLURM_JOB_ID` before expensive execution. Login nodes are
  for light work and Slurm control; run workloads and heavy installs in allocations.
- Use `$SCRATCH` for active I/O, `$PROJECT` for durable data, and `$HOME` for small
  configuration. Node-local results must be copied back before the job exits.
- Load the required modules and use a virtual environment. For Python installs,
  read the CCDB wheel guidance below before choosing package sources.
- On Fir, use only `--gpus-per-node=<gpu_type>:<count>` to request GPUs; never
  select them with `--partition`, `--gres`, or `--constraint`.

## Read for the task

Resolve these paths from this skill directory. Read only the relevant reference;
load a cluster page when hardware, limits, or site-specific behavior matters.

| Task | Reference |
|---|---|
| Cluster hardware, GPU profiles, network access, limits | `references/clusters/<cluster>.md`; supported names in [cluster index](references/clusters/README.md) |
| Account choice, fair share, resource billing | [Billing](references/billing.md) |
| Sbatch, multi-node launch, torchrun ports | [Templates](references/templates.md) |
| Queue, accounting, cancellation commands | [Slurm](references/slurm.md) |
| Modules, venvs, CCDB wheels | [Python installs](references/python-installs.md) |
| Quotas, caches, node-local staging | [Storage](references/storage.md) |
| New workload sizing and smoke tests | [Iteration](references/pipeline-iteration.md) |

Before submission, verify the account is appropriate for this project and job
type. Respect an explicitly selected eligible account; otherwise inspect current
fair share. Size resources from measurements or a bounded smoke test, considering
the cluster's billing break-even points. Import checks that may initialize a
workload also belong in an allocation. After completion, use `seff` and available
GPU measurements to tune subsequent requests.

## Helpers

Run helpers on the cluster, using their resolved absolute paths (or stream the
script over SSH when installed only on the laptop).

| Helper | Purpose |
|---|---|
| [pick-gpu-account.sh](scripts/pick-gpu-account.sh) | Rank visible `*_gpu` accounts by FairShare; verify project eligibility before using the result |
| [show-fairshare.sh](scripts/show-fairshare.sh) | Inspect account shares |
| [group-seff.sh](scripts/group-seff.sh) | Summarize your recent completed jobs |

Treat dated resource tables as reference observations; query live Slurm state
for availability and current limits. Record unknowns instead of inventing values.
Keep personal accounts and paths in local configuration, not this shared bundle.
