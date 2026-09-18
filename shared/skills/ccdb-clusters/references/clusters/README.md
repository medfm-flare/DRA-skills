# Per-Cluster Reference Index

Each file documents one Alliance cluster. The skill's top-level `SKILL.md`
routes here via `$CC_CLUSTER` when available, otherwise by hostname or other
Alliance-specific context.

## Cluster summary (as of 2026-05)

| Cluster | Location | GPUs | Use for | Status | Notes |
|---|---|---|---|---|---|
| [Fir](fir.md) | SFU | H100 SXM5 80GB (4/node, MIG-enabled) | Long jobs (≥1 day), H100 training | Operational | `$CC_RESTRICTED=true` |
| [Trillium](trillium.md) | UToronto/SciNet | H100 (verify) | Short jobs (<1 day) | Operational | **VERIFY all facts** |
| [Rorqual](rorqual.md) | Calcul Québec | H100 SXM5 80GB (4/node, 81 nodes) | Long jobs, successor to Béluga | Likely operational | **VERIFY** |
| [Cedar](cedar.md) | SFU | P100 (12/16GB), V100 (32GB) | General GPU + CPU | Operational | Older GPUs, large capacity |
| [Graham](graham.md) | UWaterloo | V100 (NVLink), T4, A100, A5000 | General — **retiring, replaced by Nibi** | Reduced capacity since 2025-01 | No compute-node internet |
| [Béluga](beluga.md) | ÉTS Montréal | V100SXM2 16GB (4/node, NVLink, 172 nodes) | General GPU + CPU | Operational | No compute-node internet |
| [Narval](narval.md) | ÉTS Montréal | A100SXM4 40GB (4/node, NVLink, 159 nodes) | General GPU + CPU | Operational | AMD CPUs, AVX2 only (no AVX512) |
| [Niagara](niagara.md) | UToronto/SciNet | None (Mist is the GPU partition) | Large CPU-parallel (≥40 cores) | Operational | Whole-node scheduling, opt-in |
| [Killarney](killarney.md) | UToronto (Vector + SciNet) | L40s 48GB (168 std nodes), H100 80GB (10 perf nodes) | AI workloads | TBA in mirror — verify | PAICE / Pan-Canadian AI Compute |

## Choosing a cluster

Use the user's selected cluster when specified. If choosing a target is part of
the request, compare eligible allocations, required hardware/software, data
location, current service status, and job limits. The dated table above is a
starting point, not an instruction to move an experiment or a current status feed.

## How these pages are sourced

- **Mirror snapshot**: most facts come from
  [github.com/ermingpei/docs-alliancecan](https://github.com/ermingpei/docs-alliancecan)
  (parsed June 2025). Each per-cluster file ends with the source MediaWiki
  `oldid=` so you can spot when content has drifted from the live wiki.
- **Live experience**: Fir's operational details (MIG slice naming, account
  conventions, `$CC_RESTRICTED` semantics) come from a working Claude
  session on Fir.
- **VERIFY-marked sections**: drafted from training data because the mirror
  doesn't cover them (Trillium, parts of Rorqual / Killarney). Confirm
  against the live wiki on first use.

When you re-pull a cluster's facts from the live wiki, update the page and
bump the date stamp at the top.
