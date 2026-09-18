---
name: slurm-seff-report
description: "Add resource reporting to an existing Slurm script. Use for inline CPU/memory snapshots, step-aware monitoring, or requests to print seff before job exit."
allowed-tools: Read Edit Write Glob Grep Bash(bash -n *)
---

# Add Slurm Resource Reporting

Inspect the supplied job script and choose monitoring that measures the actual
workload. Preserve launch semantics, exit status, existing traps, and unrelated
job logic. Edit a supplied file in place; return the modified script for pasted input.

## Choose by job shape

| Workload | Guidance |
|---|---|
| Direct command in the batch shell | Use [the cgroup snapshot](references/direct-batch-snapshot.md) for immediate CPU/memory measurements. |
| `srun`, MPI, distributed or multiple steps | The batch shell's cgroup can miss workload steps. Instrument the relevant steps only when launch/exit semantics remain correct; otherwise give post-completion `seff` instructions. |
| GPU usage | Cgroups do not measure GPU efficiency. Add runtime GPU sampling when needed and available; report which metrics were actually collected. |

`seff` depends on finalized accounting: running it inside the still-running job
does not provide a final report. Use `seff <jobid>` after exit, and do not promise
GPU metrics when the site's accounting does not expose them.

Replace an existing report block rather than duplicating it. Recognize the current
`Inline cgroup snapshot` marker, the legacy `Self-contained cgroup-based usage report`
marker, and old in-script `seff "$SLURM_JOB_ID"` calls.

For scripts with `set -e`, an end-of-script block can be skipped after failure.
Use an EXIT trap only if existing cleanup and exit status can be preserved;
otherwise disclose that limit. Cgroup v1 or unreadable counters must be reported
as unavailable, not zero.

Finish with the edited path, selected strategy, report location, and relevant
measurement limits. This task edits reporting; it does not launch a job.
