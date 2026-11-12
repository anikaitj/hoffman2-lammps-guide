# MD basics in plain language

New to molecular dynamics? Read this first. No equations needed.

## What a simulation actually does

Molecular dynamics (MD) is a movie of atoms. You give the computer:

1. Where the atoms start (a crystal, several grains, a film...)
2. How atoms push and pull on each other (the *potential*)
3. The conditions (temperature, pressure, how long)

Then it repeats one simple loop millions of times:

```
for each tiny time step (1 femtosecond = 0.000000000000001 s):
    work out the force on every atom from its neighbours
    move every atom a tiny bit according to that force (Newton's F = ma)
```

After a million steps you've simulated 1 nanosecond. That sounds short, but it's long enough to see melting, grains growing and crystals reorganising at the atomic scale.

LAMMPS is the program that runs this loop, very fast and on many CPU cores at once.

## Basic concepts

### Atoms and the box

Atoms sit in a 3D box. Each side of the box is either:

- Periodic: an atom leaving one side comes back on the opposite side, like Pac-Man. This mimics an infinite material with no edges.
- Non-periodic with empty space (vacuum): the material has a real surface.

Our thin films are periodic sideways (an infinite sheet) with vacuum above and below (real top and bottom surfaces).

### The potential

A formula plus a data file that gives the energy of any arrangement of atoms. The forces come from it. For copper we use EAM (embedded-atom method) potentials. Different potentials give slightly different physics; for example, the melting point. See [Potentials](potentials.md).

### Temperature = how much atoms jiggle

Hotter atoms vibrate harder. A thermostat gently speeds atoms up or slows them down to hold the temperature you asked for. To heat, you ramp the thermostat's target, e.g. from 300 K to 1100 K over 100 ps.

### Ensembles: what's held fixed

| Name | Fixed | Use for |
|---|---|---|
| NVT | number of atoms, volume, temperature | Films (vacuum makes pressure meaningless) |
| NPT | number of atoms, pressure, temperature | Bulk material; the box can expand as it heats |

### Minimization: relax before you start

Freshly built structures have atoms in awkward spots, especially where grains meet. Minimization nudges atoms to the nearest comfortable position before the movie starts. Skip it and the first steps can "explode".

### Random seed

Starting velocities are random. The seed number picks which random set. Same seed = identical run; different seed = an independent repeat. Because grain growth involves chance, one run is an anecdote; three or more is a result.

## Crystals in 60 seconds

- Copper atoms pack in an FCC (face-centred cubic) crystal.
- The crystal can point in any direction. We name directions and planes with Miller indices: (111), (100), (569)...
- (111) planes are the most densely packed layers of FCC. A "(111) film" has those layers lying flat, parallel to the surface. That's what the lab wants (good for growing graphene).
- (111) layers stack in an ABCABC pattern. Mistakes in the pattern are stacking faults (ABCAB|ABC) or twins (ABC|CBA).
- A grain is a chunk of crystal pointing one way. Grain boundaries are where grains meet.

## What comes out

| File | What it is | Look at it with |
|---|---|---|
| `log.lammps` | Table of temperature, energy, etc. over time + messages | `tail`, [`plot_thermo.py`](../files/plot_thermo.py) |
| `traj.lammpstrj` | Atom positions at many moments (the "movie") | OVITO, [`analyze_orientation.py`](../files/analyze_orientation.py) |
| `data.*` | Snapshot of all atoms at one moment | OVITO, or `read_data` to continue |
| `joblog.*` | Messages from the cluster's scheduler | `cat` (look here when a job fails) |

## How we judge results

- Did it melt? Watch MSD (how far atoms have wandered). Thousands of Å² = liquid. See [Melting checks](../analysis/melting-and-thermo.md).
- What structure? OVITO's PTM colours each atom: green FCC, red HCP (faults), white disordered/surface.
- Which way does the crystal face? PTM's per-atom orientation: count atoms with (111) within 5° of up. See [Measuring orientation](../analysis/orientation.md).

## How long do things take?

| | Simulated time | Typical wall time (8 cores) |
|---|---|---|
| Cu test (4,000 atoms) | 50 ps | minutes |
| Film example (~10,000 atoms) | 0.6 ns | well under an hour (estimate from a 1-core timing) |
| Lab production films (10k–30k atoms) | 1–9 ns | hours to a day |

Real experiments anneal for minutes to hours. MD covers nanoseconds, so we heat faster, use smaller grains, and sometimes go hotter. Always keep that gap in mind when comparing with experiments.
