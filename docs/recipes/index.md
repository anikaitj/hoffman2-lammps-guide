# Simulation recipes

Ready-to-run inputs for the most common kinds of LAMMPS work, beyond the lab's Cu films. Each recipe was run before being added here (short versions, LAMMPS 22 Jul 2025), and each file says how to run it, how to do a quick test, and what it outputs.

All recipe files are in `docs/files/recipes/` (on Hoffman2: `~/hoffman2-lammps-guide/docs/files/recipes/`). They run the same way as the other examples: copy into a run folder in `$SCRATCH`, add a potential file if needed, and submit with [`run_lammps.slurm`](../files/run_lammps.slurm) (change the `-in` line) or [`make_jobscript_sge.sh`](../files/make_jobscript_sge.sh) on the legacy cluster.

## Pick a recipe

| You want to simulate | Recipe | Units | Key commands | Packages |
|---|---|---|---|---|
| A simple liquid: structure and diffusion | [LJ liquid](fluids.md#lennard-jones-liquid-structure-and-diffusion) | `lj` | `pair_style lj/cut`, `compute rdf`, `compute msd` | core |
| Water (or any molecular liquid with charges) | [SPC/E water](fluids.md#water-spce) | `real` | `atom_style full`, `kspace_style pppm`, `fix shake`, `molecule` | MOLECULE, KSPACE, RIGID |
| Flow in a channel | [Poiseuille flow](fluids.md#pressure-driven-flow-in-a-channel) | `lj` | `fix addforce`, walls, `fix ave/chunk` | core |
| Viscosity | [Müller-Plathe viscosity](fluids.md#viscosity-muller-plathe) | `lj` | `fix viscosity` | EXTRA-FIX |
| Thermal conductivity | [Müller-Plathe κ](fluids.md#thermal-conductivity) | `lj` | `fix thermal/conductivity` | EXTRA-FIX |
| Polymers | [Bead-spring melt](polymers.md) | `lj` | `bond_style fene`, `pair_style soft` → `lj/cut` | MOLECULE |
| Strength / stress–strain of a metal | [Cu tensile test](metals.md#tensile-test) | `metal` | `fix deform`, `compute pressure` | MANYBODY |
| Surface energies | [Cu surface energies](metals.md#surface-energies) | `metal` | slabs + `minimize` | MANYBODY |
| Grain-boundary energy | [Cu Σ5 GB](metals.md#grain-boundary-energy) | `metal` | bicrystal + shift scan | MANYBODY |
| Annealing / recrystallizing a film | [Film on a (111) template](../examples/film-template.md) | `metal` | `boundary p p f`, `fix nvt` ramps | MANYBODY |
| Chemistry (bonds breaking) | [ReaxFF C/H/O](../examples/reaxff-cho.md) | `real` | `pair_style reaxff`, `fix qeq/reaxff` | REAXFF |
| Anything else | [More simulation types](more-types.md) | | Pointers to official examples | various |

## The four choices behind every simulation

Every input is these four decisions, plus the structure:

| Decision | Options | Rule of thumb |
|---|---|---|
| Units | `metal` (Å, ps, eV), `real` (Å, fs, kcal/mol), `lj` (reduced) | Use what the potential was written in. EAM → `metal`; most molecular force fields and ReaxFF → `real`; generic physics → `lj` |
| Atom style | `atomic`, `charge`, `bond`, `molecular`, `full` | Just atoms → `atomic`; charges → `charge`; bonds only → `bond`; bonds + angles + charges (water, organics) → `full` |
| Interactions | `pair_style` (+ `bond_style`, `angle_style`, `kspace_style`) | Long-range charges need `kspace_style pppm` |
| Ensemble | `nve`, `nvt`, `npt`, plus special fixes | Bulk at fixed pressure → `npt`; films, walls, vacuum → `nvt`; transport measurements → `nve` during production |

## Timesteps that work

| System | Typical timestep |
|---|---|
| Metals with EAM (`metal`) | 1 fs = `timestep 0.001` |
| LJ fluids (`lj`) | `timestep 0.005` |
| Rigid water with SHAKE (`real`) | 2 fs = `timestep 2.0` |
| Flexible molecules with H atoms (`real`) | 0.5–1 fs |
| ReaxFF (`real`) | 0.1–0.25 fs |
| Bead-spring polymers (`lj`) | `0.01` (after the soft push-off stage) |

If the energy drifts or atoms fly apart (`Lost atoms`, `nan`), halve the timestep first.

## Get the packages

Each recipe needs certain LAMMPS packages. Check what your LAMMPS has:

```bash
lmp -h | sed -n '/Installed packages/,/^$/p'
```

[`build_lammps.sh`](../files/build_lammps.sh) builds with LAMMPS's "most" preset plus every package these recipes use. `pip install lammps` also includes them (used for testing this guide).

## Also from the LAMMPS source

The LAMMPS source has an `examples/` folder with ~100 more working inputs (crack, indent, shear, granular flow, NEB, and more). If you built LAMMPS with `build_lammps.sh`, they're in `~/software/lammps/examples/`. Many are a better starting point than writing from scratch: see [More simulation types](more-types.md).
