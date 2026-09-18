# Example Use Case: MedGemma-FLARE-2D

The repository of this example is located at https://github.com/ATATC/MedGemma-FLARE-2D.

## Context

Before using DRA-config, you need to have a fully functional codebase first. In this example, the engine is already
implemented so that the codebase already works locally (see [MLE](https://github.com/ProjectNeura/MLE)). We want to
adapt our codebase to execute on the Fir cluster by adding SBATCH bash scripts that utilize the existing codebase.

In this example, we will be using Codex only, but Claude Code would work in a very similar way.

## Generate the SBATCH Scripts

Use `slurm-job` (`$slurm-job` in Codex or `/slurm-job` in Claude) to prepare the scripts.

> Prepare Fir job scripts for preprocessing, fine-tuning, inference, and evaluation using this project's existing commands. My GPU account is `rrg-<pi>`, my CPU account is `def-<pi>_cpu`, and my cluster username is `<username>`. Save the scripts, check their syntax, and explain any resource estimates that still need measurement. Wait for my review before launching jobs.

Substitute your own values — don't hardcode an account you aren't a member of. To find your accounts
and their priority, run `sshare -U -l` (or the `/slurm-status` skill); the `ccdb-clusters` skill bundles
`pick-gpu-account.sh` (best GPU account by FairShare) and `show-fairshare.sh` (usage/priority per
account). Use an allocation eligible for your project.

![scripts generation](assets/generate-scripts.png)

There is a little typo in the prompt in the screenshot, but Codex caught it: it should be "four" scripts, not "three".

## Include Usage Report Generation

Then use `slurm-seff-report` to add monitoring suited to the scripts' launch pattern.
A batch-shell cgroup snapshot can miss separate `srun` steps; run `seff <jobid>`
after completion for final accounting.

> Add useful resource reporting to these scripts while preserving their launch commands and exit behavior. Identify any measurements that require post-completion accounting.

![include report generation](assets/include-report-generation.png)

## Smoke Test to Determine the Required Resources

Use `slurm-job` to prepare a bounded test and `submit-experiment` when ready to
launch it. Use `slurm-debug` if the test reveals a problem.

> Prepare a smoke test that exercises the existing pipeline on representative small inputs and measures CPU, host memory, GPU memory, and runtime where available. Propose the smallest feasible Fir profile and a short time bound for review. Use the measurements to recommend full-run resources.

![smoke test](assets/smoke-test.png)

## Execute the Jobs

After reviewing the concrete scripts and resource bounds:

> Submit the reviewed run with the same account and resource limits. Keep config and code snapshots, record the scheduler job IDs, and show me the log paths. If submission is uncertain, check the scheduler before retrying.

After the jobs finish:

> Harvest the finished runs, update their metadata and experiment reports, and rebuild the index. Explain missing results or failed stages from the logs.

Add “preview only; do not change files” when you want a read-only harvest.
