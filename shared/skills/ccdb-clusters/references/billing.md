# Billing, Fairshare, and Account Selection on Alliance Canada

## Contents

- How Slurm bills jobs (MAX_TRES)
- Break-even CPU/Mem per GPU (general principle)
- What's billed: requested × wall-clock, NOT actual usage
- Fairshare / LevelFS
- Account selection before submission
- Group-wide efficiency visibility (limits)
- Useful commands

## How Slurm bills jobs (MAX_TRES)

Alliance uses **MAX_TRES** billing on every cluster: each second, a job's cost
equals the *maximum* of its TRES components — not the sum. You pay for whichever
dimension (CPU, Mem, or GPU) is most expensive; other dimensions are effectively
free up to that break-even point.

### Reading TRES weights for the current partition

Weights vary per cluster and per partition. Always look them up:

```bash
scontrol show partition <partition> | grep -i tresbill
```

Example (Fir, `gpubase_bygpu_b1`, observed 2026-04):

| Resource | Weight per unit |
|---|---|
| 1 CPU core | 1,016.67 |
| 1 GB RAM | 42.36 |
| 1× MIG 1g.10gb | 1,742.86 |
| 1× MIG 2g.20gb | 3,485.71 |
| 1× MIG 3g.40gb | 5,228.57 |
| 1× full H100 | 12,200 |

CPU-only partitions: `CPU=1000, Mem≈250/GB` (no GPU term).

The GPU weights are calibrated so the hardware-natural ratio (e.g. 48 CPU :
4 H100 per node → 12 CPU per H100 on Fir) matches the billing break-even
exactly. Your cluster's reference page has the break-even table for that
specific cluster.

## Break-even CPU/Mem per GPU (general principle)

Pick the CPU count that balances the GPU TRES weight. On Fir's H100 nodes:

| GPU | "Free" CPUs | "Free" Memory |
|---|---|---|
| 1g.10gb | **1** | ~41 GB |
| 2g.20gb | **3** | ~82 GB |
| 3g.40gb | **5** | ~123 GB |
| Full H100 | **12** | ~288 GB |

Request CPUs needed by the workload. Past break-even, CPU can become the billing
driver; this is a cost tradeoff, not a hard cap. Check the per-cluster reference
for that cluster's exact numbers.

## What's billed: requested × wall-clock, NOT actual usage

- `seff` efficiency is diagnostic only — low CPU% or idle GPU does **not** reduce your bill.
- TIMEOUT bills full wall-clock, not just useful runtime.
- Jobs that finish early are billed for actual elapsed (over-requesting `--time` is fine for billing, but hurts backfill priority).
- Idle reservations (an interactive job sitting empty) cost the SAME as a 100%-utilized training job.
- Memory over-request is billed if it tips past GPU-dominance.

## Fairshare / LevelFS

Check yours with `sshare -U -l`. Priority formula (simplified):
```
LevelFS = NormShares / EffectvUsage
```
- `LevelFS > 1` → under-used → high priority
- `LevelFS < 1` → over-used → queued longer
- `EffectvUsage` decays with a **1-week half-life** — idle 1 week ≈ LevelFS doubles
- Slurm can't tell idle from productive; both burn LevelFS equally

**Nothing you do in-job increases LevelFS.** Only time (via decay) recovers it.

### Use efficiency measurements for the next run

Shared allocations make waste relevant to the lab. Review final `seff` and any
available GPU trace after a run, then adjust requests where the evidence supports
it. No single CPU/memory/utilization threshold fits every workload, and low
utilization alone does not authorize cancellation or a change to the experiment.

- Memory: use a representative peak with headroom; investigate OOM before merely
  increasing the request. Confirm whether the measurement covers all job steps.
- CPU/GPU: compare throughput and bottlenecks before reducing CPUs, increasing
  workers, or changing profiles. These choices can affect both speed and memory.
- Time: estimate from measured runtime plus variability; preserve checkpoint/resume
  behavior for jobs that may hit the limit. Do not change convergence criteria
  solely to improve an efficiency percentage.

Use [pipeline-iteration.md](pipeline-iteration.md) for unmeasured workloads.

## Account selection before submission

Check that the account is eligible for the project and job type. Respect an
explicit eligible account; do not silently replace it with a different project's
allocation. If selection is open, inspect current `sshare -U -l --parsable2`.

Typical names include `def-<pi>_gpu`, `rrg-<pi>_gpu`, `def-<pi>_cpu`, and
`rpp-<pi>`. The bundled `pick-gpu-account.sh` ranks visible `*_gpu` accounts by
**FairShare** by default, not LevelFS. It does not decide project eligibility or
cover every account naming scheme; inspect other eligible associations separately.

Resolve helper paths from the loaded skill directory and run them on the cluster.
Check the helper exit status before constructing an sbatch command. Never submit
with an empty account after a failed lookup. Personal account names belong in
local configuration, not this shared reference.

## Group-wide efficiency visibility (limits)

- `seff <jobID>` — your jobs only; teammates' jobs return "no data"
- `sacct -a` — restricted on Alliance, shows only your own jobs even with `-a`
- `sreport cluster AccountUtilizationByUser Accounts=<acct>` — works for group totals (CPU-hours per user)
- `sshare -A <acct>` — group LevelFS; no per-user breakdown
- `scripts/group-seff.sh` — loop `seff` over your recent jobs

For group-wide `seff` aggregates you must ask each member to run `seff`
themselves, or request a report from Alliance technical support.

## Useful commands

```bash
seff <jobID>                                    # post-hoc efficiency (your own)
sshare -U -l                                    # your fairshare state
sshare -A def-<pi>_gpu                          # whole group's LevelFS
sreport cluster AccountUtilizationByUser \
  Accounts=def-<pi>_gpu Start=2026-04-01 -t Hours    # per-user CPU-hours
scontrol show partition <partition> | grep TRESBillingWeights   # verify weights
```
