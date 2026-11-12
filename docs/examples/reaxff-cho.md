# Example: ReaxFF (C/H/O)

ReaxFF is a reactive force field: bonds can break and form, and charges change as atoms move. The `ffield.reax.cho` file that ships with LAMMPS is from Chenoweth, van Duin & Goddard (2008), fitted for hydrocarbon oxidation.

Input: [`in.cho`](../files/in.cho), adapted from LAMMPS's official `examples/reaxff/CHO` (stable 29 Sep 2021, the legacy module's version). 105 atoms at 500 K for 0.75 ps.

!!! success "Tested"

    Runs to `=== DONE ===` with LAMMPS 22 Jul 2025 on a workstation. ⚠️ Not confirmed whether the legacy `lammps/29Sep2021_MB` module includes REAXFF. A self-built LAMMPS from [`build_lammps.sh`](../files/build_lammps.sh) turns it on.

## How ReaxFF differs from the Cu EAM runs

| | EAM (Cu) | ReaxFF |
|---|---|---|
| `units` | `metal` (Å, ps, eV) | `real` (Å, fs, kcal/mol) |
| `atom_style` | `atomic` | `charge` |
| Extra fix | — | `qeq/reaxff` charge equilibration, required |
| Timestep | `0.001` (= 1 fs) | `0.25` (= 0.25 fs) |
| Cost per atom | Low | Much higher (charges solved every step) |
| Analysis | PTM in OVITO | Create bonds; colour by charge `q` |

## The input

```
units           real
atom_style      charge
read_data       data.CHO

pair_style      reaxff NULL
pair_coeff      * * ffield.reax.cho H C O     # order must match atom types: 1=H 2=C 3=O

neighbor        2 bin
neigh_modify    every 10 delay 0 check no

fix             1 all nve
fix             2 all qeq/reaxff 1 0.0 10.0 1e-6 reaxff
fix             3 all temp/berendsen 500.0 500.0 100.0

timestep        0.25
thermo          100
thermo_style    custom step time temp pe press
dump            1 all custom 30 traj.lammpstrj id type q x y z

run             3000
print           "=== DONE ==="
```

- `pair_coeff * * ffield.reax.cho H C O`: element names must follow the atom-type order in the data file. A wrong order does not crash; it silently gives wrong chemistry.
- `qeq/reaxff ... reaxff`: recomputes charges every step from the parameters in the ffield file.
- `temp/berendsen` + `nve`: pulls the temperature toward 500 K. There's no `velocity` command, so it starts at 0 K and climbs (~550 K at step 3000 in our test). A Berendsen thermostat is fine for a demo; production work usually uses `nvt` plus a `velocity ... create` line.
- 3000 steps × 0.25 fs = 0.75 ps.

## Running it

```bash
mkdir -p $SCRATCH/reax_test && cd $SCRATCH/reax_test
curl -sL -o data.CHO \
  https://raw.githubusercontent.com/lammps/lammps/stable_29Sep2021/examples/reaxff/CHO/data.CHO
curl -sL -o ffield.reax.cho \
  https://raw.githubusercontent.com/lammps/lammps/stable_29Sep2021/examples/reaxff/CHO/ffield.reax.cho
head -12 data.CHO          # 105 atoms, 3 atom types
cp ~/hoffman2-lammps-guide/docs/files/in.cho .
```

Then submit with [`run_lammps.slurm`](../files/run_lammps.slurm) (input `in.cho`, 4 cores, 30 minutes) or, on the legacy cluster, `bash make_jobscript_sge.sh reax in.cho 4 00:30:00`.

If you get `Unrecognized pair style 'reaxff'`, that LAMMPS build doesn't have the REAXFF package.

## Using your own system

- Data file in `atom_style charge` format: columns `id type charge x y z`.
- `pair_coeff` element order = your type order.
- Use an ffield file fitted for your elements and chemistry; ReaxFF parameter sets aren't transferable.
- To track molecules forming and breaking: `fix reaxff/species`.
- Older inputs use `reax/c` and `qeq/reax`. These were renamed `reaxff` and `qeq/reaxff` in 2021.
