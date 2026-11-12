# Restarts & long runs

## Time limits

| Where | Max wall time |
|---|---|
| Slurm campus / shared | 24 h |
| Slurm `--qos=highp` (group nodes) | 14 days |
| Slurm default if you don't set `--time` | 2 h |
| Legacy, default if you don't set `h_rt` | 2 h |

A job that hits its limit is killed immediately, mid-step. Anything not written to disk is lost.

## Save state as you go

### At stage boundaries (lab convention)

```
write_data      data.after_heat
...
write_data      data.after_hold
...
write_data      data.final
```

Text files you can open in OVITO or read back with `read_data`. They store positions (and velocities), but not fix internal state.

### Periodically during a long stage

```
restart         100000 restart.a restart.b        # every 100k steps, alternating two files
```

Binary restart files hold the exact state. Alternating two names means a crash while writing one still leaves the other intact.

## Continuing from a restart

Make a new input that reads the state instead of building it. You must redefine the potential, computes, fixes, thermo and dumps; they aren't carried over. Groups survive `read_restart` (but not `read_data`), and redefining them is harmless, so the snippet below does it anyway. This snippet was tested: it continued a run from step 200 to 400.

```
read_restart    restart.b           # or: read_data data.after_heat

pair_style      eam
pair_coeff      * * Cu_u3.eam
neighbor        2.0 bin
neigh_modify    every 1 delay 0 check yes

group           film type 1
group           tmpl type 2
group           mobile subtract all tmpl
fix             hold tmpl setforce 0.0 0.0 0.0

compute         tmob mobile temp
thermo_style    custom step time temp pe
thermo_modify   temp tmob flush yes
thermo          1000
dump            d1 all custom 20000 traj_part2.lammpstrj id type x y z
dump_modify     d1 sort id

fix             int mobile nvt temp 1100 1100 0.1
run             2000000 upto           # "upto" = run until step 2,000,000 total
```

Notes:

- `run N upto` continues to an absolute step number, so stages line up with the original timeline.
- Don't call `velocity ... create` again; velocities come from the restart/data file.
- Write to a new dump file name so you don't overwrite the first part.
- After `read_data`, an MSD compute starts from the restart positions, not the original ones. Keep that in mind when you compare MSD across parts.

## Chain the parts automatically (Slurm)

```bash
jid=$(sbatch --parsable part1.slurm)
sbatch --dependency=afterok:$jid part2.slurm
```

## Or use the group's nodes

If the group's nodes are on Slurm, `--qos=highp` allows up to 14 days in one job. Still write restarts: nodes fail, and a 10-day run lost on day 9 hurts.
