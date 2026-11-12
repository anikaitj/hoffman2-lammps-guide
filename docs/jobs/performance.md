# Performance & sizing

## Estimate how long a run will take

After every `run`, LAMMPS prints a line like this (real output from the film example on 1 core):

```
Performance: 11.477 ns/day, 2.091 hours/ns, 132.833 timesteps/s, 1.293 Matom-step/s
```

- hours/ns is the number to use. Total time ≈ (simulated ns) × (hours/ns).
- Example: the full film schedule is 0.6 ns (100 + 400 + 100 ps). At 2.09 hours/ns on 1 core, that's ~1.3 h on 1 core, before any speed-up from more cores.
- Matom-step/s (million atom-steps per second) lets you compare runs of different sizes. Time scales roughly linearly with atom count for EAM.

!!! tip "Measure before a long run"

    Run 2,000–5,000 steps of your real input in a short job with the cores you plan to use, read `hours/ns`, multiply, and ask for ~1.5× that wall time.

## How many cores? Do a quick scaling test

In an [interactive session](interactive.md) or a short job:

```bash
for n in 4 8 16 24; do
  mpirun -n $n $LMP -in in.film_template -var heat_ps 2 -var hold_ps 0 -var cool_ps 0 \
         -log log.n$n -screen none
  echo "$n cores: $(grep '^Performance' log.n$n | tail -1)"
done
```

Pick the core count where doubling cores stops nearly halving the time. Parallel efficiency = (time on n₁ × n₁) / (time on n₂ × n₂); below ~70% you're mostly wasting cores and waiting longer in the queue.

## The breakdown table

After each run, `log.lammps` also shows where time went:

```
Section |  min time  |  avg time  |  max time  |%varavg| %total
Pair    | ...                                             | 80.x
Neigh   | ...
Comm    | ...
```

- Pair dominant (typical for EAM): healthy.
- Comm large: too many cores for the system size.
- Big min/max spread in Pair: load imbalance, common with films (half the box is vacuum). Try `processors * * 1` so LAMMPS doesn't split along z, or `balance`.

## Things that make runs faster

| Change | Effect |
|---|---|
| Dump less often (`dump ... 20000` not `1000`) | Less I/O, smaller files |
| `thermo 1000` instead of `thermo 10` | Less output |
| `neigh_modify every 1 delay 0 check yes` | Rebuilds only when needed (default-like, safe) |
| `processors * * 1` for films | Don't waste cores on vacuum along z |
| Smaller system | Linear saving. Make sure grains are still big enough for the question |
| Keep the job on one node (`--nodes=1`) | Faster communication |

Don't increase the timestep above 1 fs for Cu at high temperature to "go faster"; energy conservation and the physics suffer.

## Reference points from lab runs

| System | Cores | Simulated time | Wall time |
|---|---|---|---|
| 8-grain Cu polycrystal anneal, legacy cluster | 8 | full anneal schedule | 3 h 43 min |
| Film example (9,734 atoms), workstation test | 1 | 1 ps | ~7.6 s per 1,000 steps (2.09 h/ns) |

Add your own rows as you go: they're the best guide for the next person.

## Queue time matters too

A smaller, shorter request usually starts sooner. Sometimes 8 cores starting now beats 24 cores starting in 6 hours. `h2 why-pending <id>` explains waits on Slurm.
