# Shared HPC Configuration

These rules apply to Alliance Canada work. Load `ccdb-clusters` when the task needs
cluster-specific resources, software, storage, or billing guidance.

- Before expensive execution, check the actual hostname and `SLURM_JOB_ID`.
  On a cluster host without an allocation, allow only lightweight inspection,
  editing, Git, and Slurm control. Training, inference, compilation, heavy installs,
  test suites, and sustained processing belong in `sbatch`, `salloc`, or `srun`.
  On a laptop, run cluster commands on the intended cluster over SSH.
- Keep config and small scripts in `$HOME`; place active-job data and logs in
  `$SCRATCH` (purgeable, not permanent storage), and durable datasets/checkpoints
  in `$PROJECT`. Copy required node-local outputs back before the allocation ends.
- Use module-provided software and virtual environments; do not install globally.
- Track Slurm experiments with config snapshots, seeds, hyperparameters, and Git
  provenance. `metadata.yaml` owns run status; Markdown reports are derived.
  Use `submit-experiment` for tracked submission and `harvest` for final results.
- Keep passwords, key passphrases, and Duo passcodes out of chat and files created
  by the assistant. The user completes authentication on their own device.
