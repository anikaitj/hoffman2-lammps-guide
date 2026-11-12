# Input scripts

A LAMMPS input script (usually `in.something`) is a list of commands run top to bottom, one per line. `#` starts a comment; `&` at the end of a line continues it on the next. The full command reference is the [LAMMPS manual](https://docs.lammps.org/Commands_all.html).

Every input has the same skeleton:

1. Setup: units, atom style, boundaries
2. Structure: build atoms or read them from a file
3. Physics: potential, neighbor list
4. Settings: groups, computes, output
5. Dynamics: minimize, velocities, fixes, `run`
6. Save: write data/restart files

## A complete small example

[`in.cu_test`](../files/in.cu_test): ~4,000 Cu atoms at 300 K and 0 bar for 50 ps.

```
units           metal
atom_style      atomic
boundary        p p p

lattice         fcc 3.615
region          box block 0 10 0 10 0 10
create_box      1 box
create_atoms    1 box

pair_style      eam/alloy
pair_coeff      * * Cu_mishin1.eam.alloy Cu

velocity        all create 300 482917 mom yes rot yes
fix             1 all npt temp 300 300 0.1 iso 0 0 1.0
timestep        0.001

thermo          1000
thermo_style    custom step time temp press pe vol density
dump            1 all custom 5000 traj.lammpstrj id type x y z

run             50000
print           "=== DONE ==="
```

The rest of this page explains each piece.

---

## 1. Setup

### `units`

| Style | Distance | Time | Energy | Temperature | Pressure | Use for |
|---|---|---|---|---|---|---|
| `metal` | Å | ps | eV | K | bar | EAM metals (our Cu work) |
| `real` | Å | fs | kcal/mol | K | atm | ReaxFF, molecules |

!!! warning "Timestep units change with `units`"

    In `metal`, `timestep 0.001` = 1 fs. In `real`, `timestep 1.0` = 1 fs. Copying a timestep between unit styles is a classic 1000× error.

### `atom_style`

- `atomic`: just positions and types (EAM).
- `charge`: adds a charge per atom (ReaxFF).

### `boundary`

Three letters for x, y, z:

- `p` = periodic: an atom leaving one side enters the other. No surfaces.
- `f` = fixed non-periodic: atoms past the edge are lost. With vacuum around the material, gives free surfaces.
- `s` = shrink-wrapped non-periodic: the box follows the atoms.

| Setup | `boundary` | Has surfaces? |
|---|---|---|
| Bulk crystal | `p p p` | No |
| Thin film (lab's main setup) | `p p f` with vacuum above and below | Top and bottom |

!!! info "This choice decides surface-driven results"

    Free surfaces are what favour (111) in Cu films, because (111) is the lowest-energy surface ([surface energies](../recipes/metals.md#surface-energies)). A fully periodic box has no surfaces, so it removes that driving force. Use a film whenever surfaces matter.

---

## 2. Building structures

```
lattice         fcc 3.615                       # crystal type + lattice constant (Å)
region          box block 0 10 0 10 0 10        # a 10×10×10 block, in lattice units by default
create_box      1 box                           # simulation box with 1 atom type
create_atoms    1 box                           # fill it with type-1 atoms
```

- `region ... units lattice` (default) counts in unit cells. `units box` uses Å.
- To read an existing structure: `read_data data.file` (instead of `create_box`/`create_atoms`).
- Rotated crystals, polycrystals, films and templates have their own page: [Building structures](building-structures.md).

---

## 3. Physics

```
pair_style      eam
pair_coeff      * * Cu_u3.eam
neighbor        2.0 bin
neigh_modify    every 1 delay 0 check yes
```

- See [Potentials](potentials.md) for `pair_style` / `pair_coeff`.
- `neighbor 2.0 bin`: neighbor lists include atoms within (cutoff + 2.0 Å). The default skin for `metal` units is 2.0 Å.
- `neigh_modify ... check yes` rebuilds lists only when atoms have moved enough. Safe default.
- `mass * 63.546`: sets Cu mass for all types (needed when the potential file doesn't set it, or to be explicit).

---

## 4. Groups, computes, variables

### Groups

```
group           film  type 1
group           tmpl  type 2
group           top   region rtop
group           mobile subtract all tmpl
```

Groups let you apply fixes or computes to just some atoms (e.g. freeze a template, thermostat only the film).

### Computes (calculate something)

| Compute | Gives | Used for |
|---|---|---|
| `compute t mobile temp` | temperature of a group | Thermostat/report only moving atoms |
| `compute m film msd com yes` | mean squared displacement; `c_m[4]` = total, Å² | Melting check |
| `compute r all rdf 100` | radial distribution function | Structure (not orientation!) |
| `compute pe all pe/atom` | energy per atom | Dumps, analysis |
| `compute cs all centro/atom fcc` | centrosymmetry | Defect detection |

`com yes` in `msd` removes centre-of-mass drift, so the number reflects real atom motion.

### Variables

```
variable        T_hold  index 1100          # can be overridden: lmp -var T_hold 1200 ...
variable        n_heat  equal 100*1000      # evaluated formula
variable        pe_atom equal pe/atoms
print           "Holding at ${T_hold} K"
```

- `index` variables can be set from the command line with `-var NAME value`. This is how one input file serves a whole temperature sweep.
- `${name}` substitutes the value immediately; `v_name` refers to it in thermo/fix commands.
- `$(expression)` evaluates inline: `region r block 0 $(v_lx/2) ...`.

---

## 5. Output

### Thermo (the `log.lammps` table)

```
thermo          1000                                            # print every 1000 steps
thermo_style    custom step time temp press pe vol density c_m[4]
thermo_modify   temp tmob flush yes
```

- `thermo_modify temp tmob` makes the `temp` column use compute `tmob`. ⚠️ The `thermo_style` must contain the keyword `temp` for this to work, otherwise: `ERROR: Thermo style does not use temp`.
- `flush yes` writes each line immediately so `tail log.lammps` is up to date.

### Dumps (trajectory for OVITO)

```
dump            d1 all custom 20000 traj.lammpstrj id type x y z
dump_modify     d1 sort id
```

- `20000` = every 20,000 steps (20 ps at 1 fs). Too frequent = huge files ([Storage](../getting-started/storage.md#what-fills-space)).
- `sort id` keeps atom order stable between frames; OVITO and MSD analysis like this.
- One file with all frames is easiest for OVITO. `dump.*.lammpstrj` (with `*`) writes one file per frame.

### Data and restart files

```
write_data      data.after_heat      # text snapshot; can be read with read_data
write_restart   restart.after_heat   # binary, exact state; read with read_restart
```

Write one after each stage. Then you can restart a later stage without redoing earlier ones ([Restarts & long runs](../jobs/restarts-long-runs.md)).

---

## 6. Dynamics

### Energy minimization

```
minimize        1e-6 1e-8 1000 10000
reset_timestep  0
```

Relaxes atoms to the nearest energy minimum. Always minimize after building grain boundaries or deleting overlapping atoms, or the first steps can explode. Arguments: energy tolerance, force tolerance, max iterations, max force evaluations.

### Initial velocities

```
velocity        all create 300 482917 mom yes rot yes dist gaussian
```

Gives atoms random velocities for 300 K. The number is the random seed: change it to get an independent repeat of the same run. `mom yes rot yes` removes net drift and spin.

### Integrators and thermostats (`fix`)

| Fix | Ensemble | What's held constant | Use when |
|---|---|---|---|
| `fix 1 all nve` | NVE | Energy, volume | Rarely alone; ReaxFF example pairs it with a thermostat |
| `fix 1 all nvt temp T1 T2 0.1` | NVT | Volume, temperature (ramps T1→T2) | Films (vacuum makes pressure meaningless) |
| `fix 1 all npt temp T1 T2 0.1 iso P1 P2 1.0` | NPT | Pressure, temperature | Bulk at zero pressure |
| `fix 1 all npt temp ... x 0 0 1.0 y 0 0 1.0` | NPT in x,y only | In-plane stress | Relaxing a film's area before switching to NVT |
| `fix 1 tmpl setforce 0.0 0.0 0.0` | — | Freezes atoms | Frozen templates/seeds |

- The `0.1` (ps) is the thermostat damping time; `1.0` (ps) is the barostat damping time. ~100 and ~1000 timesteps are standard choices.
- `nvt temp 300 1100 0.1` ramps the target from 300 to 1100 K over the `run`. The heating rate = ΔT / run time.
- Only one time-integrating fix (nve/nvt/npt) per atom. To change stage: `unfix 1`, then a new `fix`.

### Timestep

```
timestep        0.001       # metal units: 0.001 ps = 1 fs  (standard for Cu)
```

1 fs is standard for metals. ReaxFF needs ~0.25 fs (`real` units: `timestep 0.25`).

### `run`

```
run             100000      # 100,000 steps × 1 fs = 100 ps
```

---

## 7. A multi-stage schedule (heat → hold → cool)

The pattern behind almost every lab run:

```
variable        n_heat equal ${heat_ps}*1000
fix             int mobile nvt temp 300 ${T_hold} 0.1
run             ${n_heat}
unfix           int
write_data      data.after_heat

variable        n_hold equal ${hold_ps}*1000
fix             int mobile nvt temp ${T_hold} ${T_hold} 0.1
run             ${n_hold}
unfix           int
write_data      data.after_hold

variable        n_cool equal ${cool_ps}*1000
fix             int mobile nvt temp ${T_hold} 300 0.1
run             ${n_cool}
unfix           int
write_data      data.final
print           "=== DONE ==="
```

Heating/cooling rate = ΔT / time. Example: 1300 → 300 K over 1,000 ps is 1 K/ps. MD rates are always enormously faster than experiments; slower is more realistic but costs more time.

!!! tip "Finish every input with `print "=== DONE ==="`"

    Lab convention. `grep DONE log.lammps` tells you instantly whether a run reached the end.

---

## 8. Running the same input with different settings

```bash
mpirun -n 8 lmp -in in.film_template -var T_hold 1200 -var vseed 111234 -log log.lammps
```

Combined with `variable ... index` defaults in the input, one file covers a whole sweep. See [Job scripts: Slurm](../jobs/slurm.md#temperature-sweeps-and-repeats-with-job-arrays) for running a sweep as a job array.

## 9. Check an input before a long run

- Run it with a tiny `run` (e.g. `-var hold_ps 1`) in an [interactive session](../jobs/interactive.md) or a 10-minute job.
- Read the top of `log.lammps`: atom counts (`Created N atoms`, `Deleted N atoms`), warnings.
- Look at frame 0 in OVITO before trusting anything else.

## Gotchas we've hit

- Rotated lattices + `units lattice` regions → regions in the wrong place. Use `units box` (Å) for regions whenever you use `orient`.
- `thermo_modify temp X` needs `temp` in `thermo_style` (see above).
- MSD reference is taken when `compute msd` is defined. Define it after `minimize`, or the minimization movement is counted.
- `WARNING: Temperature for thermo pressure is not for group all` after `thermo_modify temp` with a subgroup. Harmless for films (pressure isn't meaningful with vacuum anyway).
- Dumping too often fills scratch.
