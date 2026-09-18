---
name: slurm-debug
description: "Diagnose a failed, killed, timed-out, or pending Slurm job using accounting and logs. Use when investigating a specific job problem."
allowed-tools: Read Edit Write Glob Grep Bash(bash -n *) Bash(ssh *) Bash(sacct *) Bash(scontrol *) Bash(squeue *) Bash(sinfo *) Bash(tail *) Bash(head *) Bash(hostname *) Bash(whoami)
---

# Diagnose a Slurm Job

Use the supplied job ID or logs. If neither is given, inspect recent problematic
jobs and select the evident target; ask when several candidates remain plausible.
Run scheduler queries on the job's cluster, using `connect` if remote access is
needed. A supplied log may be enough without a new cluster connection.

## Evidence to collect

For a pending/running job, use `scontrol show job <id>` and, when relevant:

```bash
squeue -j <id> --format='%i %j %P %q %T %r %S %V' --noheader
```

For a finished job, inspect job and step records:

```bash
sacct -j <id> --format=JobID%20,State%40,ExitCode,DerivedExitCode,Elapsed,Timelimit,MaxRSS,ReqMem,AllocTRES%40 --parsable2
```

Find logs through `StdOut`/`StdErr`/`WorkDir`, the submit script, or run metadata.
Start with relevant tails; read further only when needed. A failed query is not
evidence that the job or log does not exist.

Use [diagnostic patterns](references/diagnostic-patterns.md) when interpreting
state, exit codes, or memory/CUDA errors. Keep observed facts separate from likely
causes. Do not diagnose OOM from exit 137 or the word `Killed` alone, promise a
start time from `Priority`, or infer memory peaks from a blank parent-job field.

## Finish

Explain the cause or current blocker, cite the decisive log/accounting evidence,
and give the smallest useful correction. Size resource changes from measurements
and workload needs rather than an automatic percentage increase. When a fix is
requested, make and validate the relevant edit; diagnosis alone does not authorize
resubmission. Use `submit-experiment` for a requested new attempt and preserve lineage.
