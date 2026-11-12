# Submit & monitor

## Commands side by side

| Task | Slurm | Legacy Grid Engine |
|---|---|---|
| Check a script | `h2 validate job.slurm` | — |
| Submit | `sbatch job.slurm` | `qsub job.sh` |
| My jobs | `squeue --me` | `qstat -u $USER` / `myjobs` |
| Why is it waiting? | `h2 why-pending <id>` | `qstat -j <id>` |
| Cancel | `scancel <id>` | `qdel <id>` |
| Cancel all mine | `scancel -u $USER` | `qdel -u $USER` |
| After it finished | `sacct -j <id> --format=JobID,JobName,State,Elapsed,ExitCode` or `h2 diagnose <id>` | `qacct -j <id>` |
| Change a waiting job | `scontrol update JobId=<id> TimeLimit=...` | `modify_resources_of_pending_job` |

## Job states

Slurm (`squeue`, column `ST`):

| State | Meaning |
|---|---|
| `PD` | Pending (waiting). The `NODELIST(REASON)` column says why, e.g. `(Priority)`, `(Resources)` |
| `R` | Running |
| `CG` | Completing |
| *(gone from list)* | Finished: check `sacct` for `COMPLETED`, `FAILED`, `TIMEOUT`, `OUT_OF_MEMORY` |

Grid Engine (`qstat`): `qw` waiting, `r` running, `Eqw` error (`qstat -j <id>` to see why), gone = finished.

## Is it actually running properly?

```bash
tail -5 log.lammps          # step numbers going up = working
grep DONE log.lammps        # === DONE === when finished (lab convention)
grep -i -E "error|warning" log.lammps
```

`log.lammps` shows a line every `thermo` steps. If it hasn't changed in a long time, the job may be stuck or very slow.

## Reading `log.lammps`

Excerpt from a real test run of the [film example](../examples/film-template.md) (1 core, shortened schedule):

```
LAMMPS (22 Jul 2025 - Update 4)                 ← version
Created 2016 atoms                              ← structure building (one line per grain)
Deleted 687 atoms, new total = 9734             ← overlap removal
...
   Step          Time           Temp          PotEng       v_pe_atom       c_msd[4]
         0   0              300            -33405.836     -3.4318714      0
      1000   1              488.81121      -32905.086     -3.380428       0.13595515
...
Loop time of 15.0566 on 1 procs for 2000 steps with 9734 atoms
Performance: 11.477 ns/day, 2.091 hours/ns, 132.833 timesteps/s, 1.293 Matom-step/s
...
=== DONE ===
```

The `Performance:` line after each `run` is the fastest way to estimate how long a full run will take ([Performance](performance.md)).

## When a job disappears from the queue

| What you see | Meaning | Next step |
|---|---|---|
| `log.lammps` ends with `=== DONE ===` | Success | [Download results](moving-files.md) |
| `log.lammps` exists, no DONE | LAMMPS died or hit the time limit | `tail -30 log.lammps`; `cat joblog.<id>`; Slurm: `sacct -j <id>` (look for `TIMEOUT`) |
| No `log.lammps` at all | Crashed before LAMMPS started | `cat joblog.<id>` → [Troubleshooting](../help/troubleshooting.md) |
| `ERROR: ...` at the end of `log.lammps` | Input problem | Read the error and the `Last input line:` below it |

## Watching several runs at once

```bash
cd $SCRATCH
for d in template_T*; do
  printf "%-25s %s\n" "$d" "$(tail -1 $d/log.lammps | cut -c1-60)"
done
```

## Rules

- Never run `mpirun` or `lmp` on a login node. Use a job or an [interactive session](interactive.md).
- Test one job before submitting twenty.
- Cancel jobs you know are wrong; don't let them hold cores.
