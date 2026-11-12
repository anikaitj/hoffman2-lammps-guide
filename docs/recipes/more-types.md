# More simulation types

LAMMPS covers far more than this guide's recipes. For each type below there's an official example in the LAMMPS source (`examples/` folder) that you can copy, run, and adapt. With your own build ([`build_lammps.sh`](../files/build_lammps.sh)) they're in `~/software/lammps/examples/`. You can also browse them on [GitHub](https://github.com/lammps/lammps/tree/develop/examples).

Before using one, check your LAMMPS has the package (`lmp -h`), and run the example unchanged first.

## Materials and solids

| Simulation | Package | Key commands | Example folder |
|---|---|---|---|
| Metals and alloys (EAM, MEAM) | MANYBODY, MEAM | `pair_style eam/alloy`, `meam` | `meam`, `min` |
| Silicon, semiconductors | MANYBODY | `pair_style tersoff`, `sw` | `tersoff`, `threebody` |
| Carbon, graphene, nanotubes, hydrocarbons | MANYBODY | `pair_style airebo`, `tersoff` | `airebo` |
| Oxides with charge transfer | MANYBODY, QEQ | `pair_style comb`, `coul/streitz` | `comb`, `streitz` |
| Machine-learned potentials (near-DFT accuracy) | ML-SNAP, ML-IAP | `pair_style snap`, `mliap` | `snap`, `mliap` |
| Elastic constants | core | small strains + stress | `ELASTIC` (0 K), `ELASTIC_T` (finite T) |
| Nanoindentation | core | `fix indent` | `indent` |
| Crack growth | core | `fix setforce`, `velocity ... ramp` | `crack` |
| Shear / friction | core | `fix deform`, walls | `shear`, `friction` |
| Film growth by deposition | core | `fix deposit` | `deposit` |
| Electrons in metals (laser heating, two-temperature model) | EXTRA-FIX | `fix ttm` | `ttm` |
| Thermal transport | EXTRA-FIX, core | `fix thermal/conductivity`, `fix heat`, Green–Kubo | `KAPPA`, `HEAT` |
| Shock waves | SHOCK | `fix msst`, `fix nphug` | `PACKAGES/` (SHOCK) |
| Phonons | PHONON | `fix phonon`, `dynamical_matrix` | `PACKAGES/` (PHONON) |
| Local structure order parameters | EXTRA-COMPUTE | `compute orientorder/atom` | `steinhardt`, `rdf-adf` |

## Fluids, soft matter, biomolecules

| Simulation | Package | Key commands | Example folder |
|---|---|---|---|
| Simple liquids | core | `pair_style lj/cut` | `melt` |
| Flow past obstacles, Couette and Poiseuille flow | core | walls, `fix addforce`, `velocity ... set` | `flow`, `obstacle` |
| Viscosity (NEMD, Müller-Plathe, Green–Kubo) | core, EXTRA-FIX | `fix deform` + `nvt/sllod`, `fix viscosity` | `VISCOSITY`, `nemd` |
| Diffusion | core | `compute msd`, `compute vacf` | `DIFFUSE` |
| Water and solvents | MOLECULE, KSPACE, RIGID | `fix shake` / `fix rigid`, `pppm` | `rigid`, `peptide` |
| Proteins, peptides (CHARMM) | MOLECULE, KSPACE | `pair_style lj/charmm/coul/long` | `peptide`, `charmmfsw` |
| Surfactants / bead-spring molecules | MOLECULE | bonds + LJ | `micelle` |
| Colloids | COLLOID | `pair_style colloid` | `colloid` |
| Granular flow, powders | GRANULAR | `pair_style granular`, `fix pour`, `fix wall/gran` | `granular`, `granregion`, `pour` |
| Coarse-grained fluids (DPD) | DPD-BASIC | `pair_style dpd` | `PACKAGES/` (DPD) |
| Smoothed-particle hydrodynamics | SPH | `pair_style sph/taitwater` | `PACKAGES/` (SPH) |
| Stochastic rotation dynamics (solvent for big particles) | SRD | `fix srd` | `srd` |
| Electrolytes at electrodes | ELECTRODE | `fix electrode/conp` | `PACKAGES/` (ELECTRODE) |
| Liquid crystals, ellipsoids | ASPHERE | `pair_style gayberne` | `ellipse`, `ASPHERE` |

## Methods

| Method | Package | Key commands | Example folder |
|---|---|---|---|
| Energy barriers (nudged elastic band) | REPLICA | `neb`; run with `-partition` | `neb` |
| Accelerated dynamics (rare events) | REPLICA | `prd`, `tad`, `hyper` | `prd`, `tad`, `hyper` |
| Monte Carlo (swaps, insertion) | MC | `fix atom/swap`, `fix gcmc` | `mc`, `MC-LOOP` |
| Re-analysing an old trajectory | core | `rerun` | `rerun` |
| Free energy (FEP) | FEP | `fix adapt/fep`, `compute fep` | `PACKAGES/` (FEP) |
| Enhanced sampling, collective variables | COLVARS | `fix colvars` | `PACKAGES/` (COLVARS) |
| Reactive chemistry | REAXFF, REACTION | `pair_style reaxff`, `fix bond/react` | `reaxff`, `PACKAGES/` (REACTION) |
| Python inside LAMMPS | PYTHON | `python`, `fix python/invoke` | `python` |
| Charge equilibration | QEQ | `fix qeq/point` etc. | `qeq` |

Folder names checked against the LAMMPS manual's [Examples page](https://docs.lammps.org/Examples.html). Package-specific examples live under `examples/PACKAGES/<package name>`.

## How to adapt an example

1. Copy the whole example folder to `$SCRATCH` (it often has data and potential files):
    ```bash
    cp -r ~/software/lammps/examples/indent $SCRATCH/indent_test && cd $SCRATCH/indent_test
    ls                         # in.* = input, log.* = reference output
    ```
2. Run it unchanged with a short job and compare your `log.lammps` with the reference `log.*` in the folder. Same numbers means your setup works.
3. Change one thing at a time: units/structure → potential → ensemble → run length.
4. Add the lab conventions: `print "=== DONE ==="` at the end, `-var` defaults for settings you'll sweep, `write_data` after each stage.

## Multi-replica runs on Hoffman2 (NEB, tempering)

These run several copies of the system at once with `-partition`. With 4 replicas × 2 cores each:

```bash
#SBATCH --ntasks=8
mpirun -n 8 $LMP -partition 4x2 -in in.neb -log log.lammps
```

Each replica writes its own `log.lammps.N` and `screen.N`.

## Asking for help

- LAMMPS manual pages: each command's page lists its restrictions and which package it needs.
- [MatSci LAMMPS forum](https://matsci.org/lammps): search before posting; include your input, LAMMPS version and the exact error.
- Lab: post the input, `log.lammps` tail and job script in the group chat.
