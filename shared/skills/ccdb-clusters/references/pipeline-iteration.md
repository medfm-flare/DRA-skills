# Size a New Workload with a Smoke Test

Read when a new or materially changed workload lacks useful measurements. Reuse
recent measurements for an unchanged workload. Match the smoke test to the user's
experiment; it does not require a particular tracker, framework, or training metric.

## Bounded test

Choose a representative small input and enough steps to exercise loading, forward
and backward passes when applicable, output writing, and the relevant evaluation
path. Run inside an authorized Slurm allocation, on the smallest profile expected
to fit. On Fir use the exact GPU type from [fir.md](clusters/fir.md), such as
`nvidia_h100_80gb_hbm3_2g.20gb`, not an invented abbreviated type.

Define time/resource bounds before launch. Preserve the experiment's seeds,
config, and code provenance. Use the project's existing logging; adding a tracker
account or external upload is a separate choice. A small training test should
show plausible behavior, not necessarily convergence or perfect accuracy.

## Measurements that inform the next request

| Measurement | Decision |
|---|---|
| Peak GPU memory, where available | Choose a profile with adequate headroom for representative full-run shapes. |
| GPU utilization over time | Investigate input/communication bottlenecks before assuming a larger GPU helps. |
| CPU usage and throughput | Size CPUs for useful work; compare against billing break-even without treating it as a hard performance cap. |
| Job/step memory peak | Choose host memory with justified headroom; whole-node `free -h` is not the job's peak. |
| Representative step/epoch time | Estimate full-run duration and uncertainty; include checkpoint and evaluation overhead. |

Use step-aware monitoring for `srun` or distributed jobs; see `slurm-seff-report`.
Use final `seff` after job exit. GPU metrics may require separate sampling and
may not be available for every profile. Missing counters are unknown, not zero.

## Scale within the experiment's bounds

Resolve errors and verify required outputs before scaling. Neither 95% VRAM use,
90% GPU utilization, nor perfect training-set metrics is a universal acceptance
criterion. Keep enough memory headroom for larger inputs and later phases.

If the estimated run exceeds the user's time budget, present relevant options:
checkpoint/resume, a smaller experiment, or measured distributed scaling. Do not
assume that adding GPUs halves runtime, change the scientific objective, or switch
clusters automatically. Follow an existing authorized stop rule; new early-stopping
criteria or cancellation decisions need a basis in the user's experiment.

Record the measurements and resulting resource choices in the run record. Use
[billing.md](billing.md) for cost tradeoffs and the target cluster page for limits.
