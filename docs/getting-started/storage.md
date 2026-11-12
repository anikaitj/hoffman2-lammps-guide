# Storage

Values from OARC's [Storage page](https://www.hoffman2.idre.ucla.edu/Using-H2/Storage/Storage.html). The same folders appear on both the Slurm and legacy clusters.

| Space | Path | Quota (size / files) | Kept for | Backed up | Use it for |
|---|---|---|---|---|---|
| Home | `$HOME` = `/u/home/<l>/<user>` | 60 GB / 1,000,000 | Forever | Yes (daily, 30-day versions) | Scripts, potentials, your own LAMMPS build, small results |
| Scratch | `$SCRATCH` = `/u/scratch/<l>/<user>` | 2 TB / 5,000,000 | Files older than 14 days may be deleted | No | Running jobs, trajectories, logs |
| Project | `/u/project/<group>/<user>` | Bought per TB/year | Forever | Yes | Shared group data (if the PI buys it) |
| $TMPDIR | `/work` on each compute node | Varies | Deleted when the job ends | No | Fast temporary files inside a job |

## The rules that matter

1. Run jobs in scratch. It's big and meant for job I/O.
2. Scratch purges after 14 days, and sooner if space runs low. After a run finishes, download what you need ([Moving files](../jobs/moving-files.md)) or copy it to home/project.
3. Home is small. A few big trajectories will fill 60 GB.
4. Backups don't save you from `rm`. They protect against hardware failure, not accidental deletion. Scratch has no backup at all.

## Check your usage

```bash
myquota                 # quotas and usage for home, scratch, project
du -sh $SCRATCH/*       # which runs are big
ls -l $HOME | grep project-   # any project-space links you have
```

## A folder layout that works

```
$HOME/
├── software/lammps/          # your LAMMPS build (if you build it)
├── potentials/               # Cu_u3.eam, Cu_mishin1.eam.alloy, ...
└── hoffman2-lammps-guide/    # this repo (git clone)

$SCRATCH/
├── 2026-11-10_cu_test/
├── 2026-11-12_template_T1100_s1/
└── 2026-11-12_template_T1100_s2/
```

Name run folders with the date and what changed. You'll thank yourself when comparing 30 runs.

## What fills space

| File | Typical size | Tips |
|---|---|---|
| `traj.lammpstrj` (dump) | 10s of MB to many GB | Dump less often; dump only `id type x y z`; use `dump_modify ... sort id` |
| `core.*` crash dumps | GBs each | Delete them (see [Troubleshooting](../help/troubleshooting.md#illegal-instruction-signal-4-and-huge-core-files-appear)) |
| restart / `data.*` files | ~size of one frame | Keep only the ones you need |
| `log.lammps` | small | Always keep |

Rough rule for dumps: each atom per frame with `id type x y z` is about 30 bytes as text (measured on the film example). 20,000 atoms × 250 frames ≈ 150 MB. Adding more columns (velocities, per-atom energy) grows it proportionally.
