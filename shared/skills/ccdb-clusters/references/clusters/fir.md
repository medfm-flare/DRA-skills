# Fir Cluster

> Sourced from live Fir session (2026-05) + Alliance wiki mirror oldid=164899 (June 2025).
> Status: **Operational.** `$CC_CLUSTER=fir`, `$CC_RESTRICTED=true`.

## Contents

- At a glance
- Hardware
- GPU sizing — MIG slice names
- Storage
- Fir-specific quirks
- Partitions and wall-time
- TRES weights (observed 2026-04, partition `gpubase_bygpu_b1`)
- Daily cost (12h, requested vs used)
- Account selection — eligibility and fair share
- Common pitfalls on Fir

## At a glance

| Item | Value |
|---|---|
| Location | Simon Fraser University (Burnaby, BC) |
| Login host | Set by Alliance (check with `echo $HOSTNAME` from a login session) |
| Globus endpoint | (verify) |
| OS | AlmaLinux 9.6 |
| Special | `$CC_RESTRICTED=true` — export-control rules apply |
| Best for | **Long jobs (≥1 day)** on H100 |

## Hardware

| Nodes | Cores | Memory | CPU | GPU |
|---|---|---|---|---|
| 860 | 192 | 768 GB DDR5 | 2× AMD EPYC 9655 (Zen 5) @ 2.7 GHz, 384 MB L3 | — |
| 160 | 48 | 1 TB DDR5 | 1× AMD EPYC 9454 (Zen 4) @ 2.4 GHz, 256 MB L3 | 4× NVIDIA H100 SXM5 (80 GB) |

H100s on the GPU nodes support **MIG slicing**, so a single 80 GB GPU can be
partitioned into smaller virtual GPUs.

## GPU sizing — MIG slice names

| Slice | VRAM | `--gpus-per-node=` value | Break-even CPUs | Break-even Mem |
|---|---|---|---|---|
| 1g.10gb | 10 GB | `nvidia_h100_80gb_hbm3_1g.10gb:1` | 1 | ~41 GB |
| 2g.20gb | 20 GB | `nvidia_h100_80gb_hbm3_2g.20gb:1` | 3 | ~82 GB |
| 3g.40gb | 40 GB | `nvidia_h100_80gb_hbm3_3g.40gb:1` | 5 | ~123 GB |
| Full H100 | 80 GB | `h100:1` (or `h100:4` for whole node) | 12 | ~288 GB |

Choose the smallest profile that fits measured memory and throughput needs with
headroom. Duration alone does not determine the required VRAM; verify the relevant
wall-time limits and scheduling tradeoffs before choosing a full GPU.

## Storage

| Mount | Variable | Volume | Purge |
|---|---|---|---|
| `/home/$USER` | `$HOME` | small fixed (~48 GB) | persistent |
| `/scratch/$USER` | `$SCRATCH` | large fixed | inactive purge (60 days) |
| `/project/<group>` | `$PROJECT` | RAC | persistent |
| `/localscratch/<user>.<jobid>.0/` | (see below) | per-node NVMe (~7 TB) | per-job, auto-cleaned |
| `/cvmfs/soft.computecanada.ca/...` | — | shared software stack | read-only |

Total cluster storage: 51 PB (2 PB NVMe + 49 PB SAS).

### `/localscratch` — Fir-specific job-local NVMe

Each Fir compute node has a `/localscratch` mount on local NVMe — observed
on `fc10920` (2026-05-06) at **7.0 TB / 6.8 TB free**, mounted xfs with
`noquota`. SLURM auto-creates `/localscratch/$USER.$SLURM_JOB_ID.0/` for
every job; the directory is owned by you and writable. Contents are wiped at
job exit by the SLURM epilog.

Two important quirks vs. the generic `$SLURM_TMPDIR` pattern:

1. **`$SLURM_TMPDIR` is not always exported on Fir.** The dir exists, but if
   you `echo $SLURM_TMPDIR` from inside a job and get nothing, build the
   path yourself: `LOCAL_SCRATCH=/localscratch/${USER}.${SLURM_JOB_ID}.0`.
   The recipe in `references/storage.md` uses `${SLURM_TMPDIR:-…}` for
   safety.
2. **`/localscratch` does not count against `--mem=`** — it's real NVMe
   disk, not tmpfs. By contrast `/tmp` on Fir compute nodes IS tmpfs
   (RAM-backed) and bytes there ARE charged to `--mem=`. Staging a big
   dataset to `/tmp` on a small `--mem=` allocation will OOM-kill the job
   (observed on Fir 2026-05-06: a 28 GB `cp` of NPZ files into /tmp on a
   `--mem=64G` allocation triggered a cgroup-OOM SIGKILL; sacct showed
   `State=CANCELLED` with `ExitCode=0:0`).
   Stage to `/localscratch` instead.

`--tmp=200G` in the sbatch header is recommended even though the node has
~7 TB free — it documents intent for the scheduler and survives any future
node-pool rebalancing.

## Fir-specific quirks

- **Compute-node internet IS available** — `pip install`, `wandb online`, and
  `huggingface_hub` calls work inside `sbatch`. (Most Alliance clusters block
  this; Fir does not.)
- **`$CC_RESTRICTED=true`** — some software (CUDA toolkit, certain ML
  libraries) is gated; ITAR/EAR-style export-control rules. If a `module
  load` returns "permission denied", that's why; ask CCDB support.
- **Templates path** — example job templates live in `$SCRATCH/job_*.sh`
  (per-user; not shipped with this skill).
- **MASTER_PORT** — see `references/templates.md` for the torchrun pitfall;
  a documented case occurred on Fir.

## Partitions and wall-time

Fir has two banded GPU partition families; SLURM auto-picks the smallest band
that fits your `--time` (you normally do **not** set `--partition` yourself):

- `gpubase_bygpu_b<N>` — scheduled per **GPU** (MIG slices / single-GPU jobs)
- `gpubase_bynode_b<N>` — scheduled per **whole node** (multi-GPU / full-node jobs)

| Band | Wall-time |
|---|---|
| `b1` | 3 h |
| `b2` | 12 h |
| `b3` | 1 day |
| `b4` | 3 days |
| `b5` | 7 days |

GPU bands run **b1–b5 only (max 7 days)** — there is **no GPU `b6`**. (`b6` = 28 days
exists only for the *CPU* family `cpubase_bynode_b6`.) Also present: `gpubase_interac`
(interactive), plus two **scheduler-internal** lower-priority lanes you **cannot** target with
`--partition` (the `job_submit` lua plugin rejects explicit requests — keep submitting by
`--time` only): `gpubackfill` (PriorityTier 2, opportunistic, not preemptible) and `gpupreempt`
(PriorityTier 1, `PreemptMode=REQUEUE` — jobs are requeued when a higher-tier job needs the node).
Their partition configs list longer `MaxTime` (1 day / 122 days), but the plugin still enforces the
**7-day user cap** regardless. Verified 2026-05-25: `sbatch --test-only --partition=gpupreempt
--time=10-0` → rejected *"exceeds the maximum walltime of 7.0 days"*; `--partition=gpubackfill` →
*"submit without the --partition option"*.

Verified live via `sinfo -o "%.30P %.14l"` (2026-05-25). Re-verify before sizing a
long job — bands have shifted before.

## TRES weights (observed 2026-04, partition `gpubase_bygpu_b1`)

| Resource | Weight per unit |
|---|---|
| 1 CPU core | 1,016.67 |
| 1 GB RAM | 42.36 |
| 1× MIG 1g.10gb | 1,742.86 |
| 1× MIG 2g.20gb | 3,485.71 |
| 1× MIG 3g.40gb | 5,228.57 |
| 1× full H100 | 12,200 |

Re-verify with `scontrol show partition gpubase_bygpu_b1 | grep -i tresbill`.

## Daily cost (12h, requested vs used)

| GPU | Daily cost |
|---|---|
| 1g.10gb | ~75M / day |
| 2g.20gb | ~150M / day |
| 3g.40gb | ~226M / day |
| Full H100 | ~527M / day |

(Numbers are billing units, not currency; useful for relative comparison.)

## Account selection — eligibility and fair share

Check that the account covers this project and workload. Respect an explicit
eligible account. When choosing between eligible accounts, inspect current fair
share and allocation conditions; RRG/RPP awards may be appropriate for their
designated projects. Follow [billing guidance](../billing.md) rather than choosing
an account solely from its prefix.

Submit-priority benefit, not just policy: on Fir the SLURM FAIRSHARE
priority component is dominated by the *FairShare* score (multi-level
FairTree), not by LevelFS. RRG accounts typically have higher FairShare
because their parent group has a larger root-level share allocation —
*even when LevelFS at the leaf account is lower*. Real numbers from a
def-* + rrg-* pair on Fir (2026-05-06, account names anonymised):

| Account | LevelFS | FairShare | FAIRSHARE priority |
|---|---|---|---|
| `def-<pi>-<sub>_gpu` | 2.998 | 0.337 | 1.68 M |
| `rrg-<pi>_gpu`       | 0.431 | **0.498** | **2.50 M** (1.48× ↑) |

`scripts/pick-gpu-account.sh` ranks by FairShare since 2026-05-06; the
older LevelFS-based behaviour is preserved behind `PICK_BY=levelfs`.

For a requested account correction to a pending job, verify the job and eligible
replacement account before using the scheduler update below. A status query does
not authorize changing the account; acceptance and scheduling effects depend on
current cluster policy.

```bash
scontrol update JobId=<jobid> Account=rrg-<pi>_gpu
```

Verify the account and scheduler response after an authorized update.

## Common pitfalls on Fir

- **Idle full-H100 reservation while AFK** — bills the same as 100%-utilized.
  Cancel with `scancel` when you step away.
- **PyTorch < 2.2** — H100 is sm_90, needs PyTorch ≥ 2.2.
- **Hard-coded `os.environ['MASTER_PORT']` in `main.py`** — overwrites
  torchrun's port and hangs `dist.init_process_group` for 1800 s. See
  `templates.md`.
- **Submitting from `/home`** — fails with "Submitting jobs from
  directories residing in /home is not permitted". `cd $SCRATCH/<project>` first.
