---
name: harvest
description: "Collect finished Slurm experiment results, update run metadata, and rebuild the report index. Use after tracked runs finish."
argument-hint: "[--auto] [run_code]"
allowed-tools: Read Edit Write Glob Grep Bash(sacct *) Bash(scontrol *) Bash(squeue *) Bash(ssh *) Bash(tail *) Bash(hostname *)
---

# Harvest Experiment Results

Resolve tracked runs from scheduler evidence, update their metadata and narrative,
and rebuild the derived index. Use the project's existing paths; the default is
`experiment/<run_code>/metadata.yaml`, `docs/experiments/<run_code>.md`, and
`docs/experiments.md`. The schema is in the installed `submit-experiment` skill's
`references/experiment-layout.md`; locate that skill before opening it.

## Scope

- A run code limits the work to that run; otherwise inspect submitted/running runs.
- A request to harvest or update reports authorizes those file updates. `--auto`
  remains a compatible explicit form of the same authorization.
- For a preview or read-only summary, report findings without writing. Never
  submit, resubmit, cancel, delete artifacts, or launch expensive post-processing
  merely to complete a harvest.

Read relevant run metadata, result paths, and reporting conventions. Reuse an
existing completed narrative as a style reference only when needed. Parse YAML
as structured data and preserve unrelated fields and researcher-written notes.

## Resolve status

Query on the recorded cluster, locally or through the established SSH connection:

```bash
sacct -X -j <job_id> --format=JobID,State%40,ExitCode,Elapsed,End --noheader --parsable2
```

| Evidence | Action |
|---|---|
| `COMPLETED` | Set `completed`; collect available metrics. |
| `FAILED`, `NODE_FAIL`, `BOOT_FAIL`, `DEADLINE` | Set `failed`; retain the exact scheduler state and reason in notes. |
| `TIMEOUT`, `CANCELLED`, `OUT_OF_MEMORY` | Set `timeout`, `cancelled`, or `oom`. |
| Running, pending, completing, requeued, suspended, or uncertain state | Keep the run open; report current evidence. |
| Successful query with no retained record | Use a matching `.done.json` completion marker if available and identify it as fallback evidence. |
| Query/authentication failure | Report the failure separately from an empty result. Do not infer completion from missing output. |

Normalize state suffixes without losing the original evidence. For a single-job
run use its recorded job ID. For retries use the recorded active attempt; for
multi-stage runs resolve required stages and dependencies. A numerically highest
job ID alone does not prove the whole experiment completed. If lineage is unclear,
report per-job states and leave the aggregate unresolved.

Never fabricate metrics or a terminal status. Preserve the scheduler or marker's
actual finish timestamp; leave an unknown finish time null rather than using now.
Prepared/rejected submissions are not finished workloads. Reconcile
`submission_unknown` through the submission workflow before harvesting it.

## Update and report

Collect the primary metric, checkpoint location, and relevant log evidence.
For unsuccessful runs, record the failure and any partial results. Missing results
do not justify invented values: report that none were found.

Update `metadata.yaml`, then the narrative's Results/Observations in the project's
style. Explain results against the recorded goal and decision rule when present.
Run only lightweight, authorized summary processing on a login node.

Regenerate the full index from metadata, sorted by `started_at` with unset dates
handled explicitly. Include run code, status, goal, key result, and narrative link.
Hold a lock across read/update/write operations (not just a separate lock command),
and use atomic replacement so parallel harvests cannot partially overwrite it.
Use a platform-supported lock if `flock` is unavailable.

Finish with updated runs, key results, failures, and still-open/unresolved runs.
Already resolved records are skipped unless the user requested a refresh.
