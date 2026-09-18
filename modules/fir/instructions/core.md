# Fir Configuration

Configured target: **Fir** (`fir.alliancecan.ca`); this does not mean the current
shell is on Fir. Saved GPU account: `{{FIR_ACCOUNT}}`; check its eligibility and
current fair share at submission time. Fir uses restricted software access.

- Request GPUs only with `--gpus-per-node=<gpu_type>:<count>`; do not select them
  with `--partition`, `--gres`, or `--constraint`.
- Use `ccdb-clusters/references/clusters/fir.md` for H100/MIG profiles and sizing.
  Smoke-test an unmeasured workload on the smallest feasible profile before scaling.
- Check `slurm-status` before large submissions. After completion, use `seff` to
  inform the next run's CPU, memory, time, and GPU requests.
- Use `connect` for SSH reuse from a laptop; use `onboard` for first-time setup.
