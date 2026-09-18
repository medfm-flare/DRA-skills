# Direct batch-step cgroup snapshot


Add the block **after** the main workload command, before any final `echo "End"` line if present.
Keep the marker comment exactly as written so future runs of this skill find and update the block
instead of duplicating it. If the script uses `set -e`, explain that failures before this block may
skip the snapshot unless the script adds an `EXIT` trap; do not silently promise failed-job reports.

```bash
# ---- Inline cgroup snapshot (CPU/memory only; not a seff replacement) ----
REPORT_DIR="${SLURM_SUBMIT_DIR:-$PWD}/logs"
mkdir -p "$REPORT_DIR"
USAGE_REPORT="${REPORT_DIR}/${SLURM_JOB_NAME:-job}_${SLURM_JOB_ID}_usage.txt"

# Resolve the job's own cgroup-v2 path (the "0::/..." line in /proc/self/cgroup)
JOB_CG=$(awk -F: '/^0::/{print $3; exit}' /proc/self/cgroup 2>/dev/null)

# Peak memory in bytes and total CPU microseconds (both kernel-tracked continuously)
MEM_PEAK="unavailable"; CPU_USEC="unavailable"
[ -n "$JOB_CG" ] && [ -r "/sys/fs/cgroup${JOB_CG}/memory.peak" ] && \
  MEM_PEAK=$(cat "/sys/fs/cgroup${JOB_CG}/memory.peak")
[ -n "$JOB_CG" ] && [ -r "/sys/fs/cgroup${JOB_CG}/cpu.stat" ] && \
  CPU_USEC=$(awk '/^usage_usec/{print $2}' "/sys/fs/cgroup${JOB_CG}/cpu.stat")

# Format the report in seff-like style: GB / HH:MM:SS / efficiency lines
awk -v jid="$SLURM_JOB_ID" -v jname="${SLURM_JOB_NAME:-?}" \
    -v host="$(hostname)" -v gen="$(date -Iseconds)" \
    -v cpus="${SLURM_CPUS_PER_TASK:-1}" -v mem_req_mb="${SLURM_MEM_PER_NODE:-0}" \
    -v gpu_req="${SLURM_GPUS_PER_NODE:-?}" \
    -v mem_peak="$MEM_PEAK" -v cpu_usec="$CPU_USEC" -v wall_sec="${SECONDS:-0}" \
'function hms(s,    h,m,ss){ h=int(s/3600); m=int((s%3600)/60); ss=int(s%60);
  return sprintf("%02d:%02d:%02d", h, m, ss) }
 BEGIN{
  print "Slurm job usage snapshot (cgroup-direct, end-of-script)"
  printf "  Job ID    : %s\n  Job name  : %s\n  Host      : %s\n  Generated : %s\n\n", \
    jid, jname, host, gen
  print "== Resources requested =="
  printf "  --cpus-per-task : %s\n  --mem (per node): %s MB\n  --gpus-per-node : %s\n\n", \
    cpus, mem_req_mb, gpu_req
  print "== Cgroup measurements (kernel-direct; accurate at end of script) =="
  if (mem_peak == "unavailable") {
    print "  Memory Utilized  : unavailable (cgroup v1 / EL7 cluster?)"
  } else {
    mb = mem_peak/1048576; gb = mb/1024
    if (gb >= 1) printf "  Memory Utilized  : %.2f GB\n", gb
    else         printf "  Memory Utilized  : %.2f MB\n", mb
    if (mem_req_mb+0 > 0)
      printf "  Memory Efficiency: %.1f%% of %.2f GB (requested)\n", mb/mem_req_mb*100, mem_req_mb/1024
  }
  if (cpu_usec == "unavailable") {
    print "  CPU Utilized     : unavailable"
  } else {
    printf "  CPU Utilized     : %s\n", hms(cpu_usec/1000000)
  }
  if (wall_sec+0 > 0) printf "  Wall-clock time  : %s\n", hms(wall_sec)
  if (cpu_usec != "unavailable" && wall_sec+0 > 0 && cpus+0 > 0) {
    cw  = wall_sec * cpus
    eff = (cpu_usec/1000000) / cw * 100
    printf "  CPU Efficiency   : %.2f%% of %s core-walltime (wall * %s cpus)\n", eff, hms(cw), cpus
  }
  print ""
  print "Note: this is an inline cgroup snapshot, not a seff replacement. It may"
  print "under-report srun/multi-step jobs. For finalized accounting including GPU"
  print "efficiency, run after the job exits:"
  printf "  seff %s\n", jid
}' > "$USAGE_REPORT"
echo "Usage report -> $USAGE_REPORT"
# ---- End cgroup snapshot ----
```
