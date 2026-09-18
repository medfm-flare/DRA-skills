---
name: slurm-resource
description: "List the user’s Alliance Canada accounts and requestable GPU types and limits. Use for resource eligibility; use slurm-status for live Fir availability."
allowed-tools: Read Bash(ssh *) Bash(whoami) Bash(hostname *) Bash(sshare *) Bash(sacctmgr *) Bash(sinfo *)
---

# Inspect Resource Eligibility

Identify the target cluster and its remote username. Use `connect` if SSH access
is needed and `ccdb-clusters` for that site's GPU types, limits, and billing.
Run only the queries needed for the question:

```bash
sshare -U -l --parsable2
sacctmgr show association user="$(whoami)" format=account%30,qos%30 --noheader
sinfo -o '%P %G %m %l %T' --noheader
```

Report the user's eligible accounts, GPU profiles, request syntax, and relevant
limits. Associations and configured hardware describe what can be requested;
they do not establish how many GPUs are free now. Use `slurm-status` for live Fir
availability. Flag unavailable queries and unresolved limits instead of guessing.

Respect the user's project/account choice when eligible. The account helper ranks
visible `*_gpu` accounts by FairShare; verify project suitability before recommending
its result. On Fir, request GPUs only with `--gpus-per-node=<gpu_type>:<count>`,
never `--partition`, `--gres`, or `--constraint`. Recommend sizing from workload
needs and measurements; a resource listing does not authorize a sizing job.
