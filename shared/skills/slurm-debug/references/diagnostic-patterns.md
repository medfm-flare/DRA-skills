# Interpreting Slurm Failures

Read when state and logs need interpretation. These are diagnostic clues, not a
substitute for the job's evidence.

| Evidence | Interpretation / next check |
|---|---|
| `OUT_OF_MEMORY` or a step's explicit `oom-kill` record | Check host-memory limits and measured usage; inspect data loading and node-local storage choices. |
| `CUDA out of memory` | GPU VRAM exhaustion; consider batch size, checkpointing, or a larger profile. More GPUs help only if the workload distributes memory. |
| `TIMEOUT` | Wall-time limit reached; assess progress, checkpoint/resume, and an appropriate time request. |
| `CANCELLED` | Cancellation, not proof of OOM; inspect recorded actor and logs. |
| `NODE_FAIL`, `BOOT_FAIL` | Infrastructure failure; inspect partial outputs and retry only within authorization. |
| `PREEMPTED` | Inspect whether the scheduler requeued it before treating it as terminal or proposing a new job. |
| `FAILED` | Nonzero script/step outcome; inspect logs and step accounting. |
| `No space left on device` | Check quota, inode usage, filesystem capacity, and output paths. |
| `ModuleNotFoundError` | Check module/venv activation and the installed environment. |
| NCCL/distributed errors | Inspect rank/world-size, launch commands, connectivity, and rendezvous settings. |
| Segmentation fault or bus error | Inspect the stack and environment; do not assume a CUDA mismatch or memory shortage without evidence. |

Slurm `ExitCode` is `exit_status:signal`: `0:9` reports signal 9; `9:0` is exit
status 9, not a signal. Shell status 137 may reflect a killed subprocess but does
not identify who killed it. Use step records and `DerivedExitCode` when a batch
shell returned success despite a failed workload.

For pending jobs, `Priority` and `Resources` explain scheduling constraints, not
guaranteed start times. `QOSGrpMemLimit` or `AssocGrpMemLimit` warrants inspecting
the relevant account's usage; `ReqNodeNotAvail` warrants checking node state;
`DependencyNeverSatisfied` warrants inspecting the dependency job.

Sources: [Slurm exit codes](https://slurm.schedmd.com/job_exit_code.html) and
[Slurm job states](https://slurm.schedmd.com/job_state_codes.html).
