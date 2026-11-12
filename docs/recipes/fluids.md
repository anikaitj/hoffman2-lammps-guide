# Fluids

Liquids, water, flow and transport coefficients. All inputs are in `docs/files/recipes/`. Every one ends by printing `=== DONE ===` and, where there's a number to compute, the exact next command to run.

!!! info "Reduced (LJ) units"

    Three recipes here use `units lj`: lengths in σ, energies in ε, masses in m, time in τ = σ√(m/ε). Results are general for any simple liquid. To get argon, for example, use σ = 3.405 Å, ε/k_B = 119.8 K, m = 39.95 u.

## Lennard-Jones liquid: structure and diffusion

File: [`in.lj_liquid`](../files/recipes/in.lj_liquid) · 4,000 atoms · T* = 1.0, ρ* = 0.8442

What it does: melts an FCC lattice at T* = 3, cools to T* = 1 with a thermostat, then switches the thermostat off (NVE) for production, so the dynamics aren't disturbed while measuring.

| Output | Meaning |
|---|---|
| `rdf.dat` | Radial distribution function g(r), averaged over production |
| `msd.dat` | Mean squared displacement vs time |
| log: `Diffusion coefficient D* = ...` | From the MSD slope: D = slope / 6 in 3D |

```bash
mpirun -n 4 $LMP -in in.lj_liquid -log log.lammps
# quick test:
mpirun -n 4 $LMP -in in.lj_liquid -var neq 2000 -var nprod 2000 -log log.lammps
```

The quick test gave D* = 0.060. Use the full run for a real value: the slope needs the MSD to be in its straight-line (diffusive) regime, and a few τ isn't long enough to be sure.

Things to change: `-var T 1.5`, `-var rho 0.7`. Plot `rdf.dat` to see the liquid's shell structure.

## Water (SPC/E)

File: [`in.water_spce`](../files/recipes/in.water_spce) + [`water.mol`](../files/recipes/water.mol) · 1,000 molecules · 300 K, 1 atm

The pattern for any molecular liquid with charges:

1. `atom_style full` (bonds, angles and charges).
2. A molecule template (`water.mol`) holds one molecule's geometry, charges, bonds and SHAKE info.
3. `create_atoms 0 random N seed NULL mol h2o ...` scatters N molecules in the box.
4. `kspace_style pppm 1.0e-4` handles long-range electrostatics.
5. `fix shake` keeps O–H bonds and the H–O–H angle rigid (that's what SPC/E assumes), which allows a 2 fs timestep.
6. Minimize (random placement leaves close contacts), then NPT at 300 K and 1 atm, then NVT production.

| Output | Meaning |
|---|---|
| log: `Final density` | Should approach ~1 g/cm³ (the quick test with 216 molecules and 4 ps of NPT gave 0.983) |
| `rdf_OO.dat` | Oxygen–oxygen g(r): first peak near 2.8 Å |
| `msd_O.dat` | Oxygen MSD → self-diffusion |
| `traj.lammpstrj` | Trajectory with molecule IDs and charges |

```bash
mpirun -n 8 $LMP -in in.water_spce -log log.lammps
# quick test:
mpirun -n 4 $LMP -in in.water_spce -var nmol 216 -var nnpt 2000 -var nprod 1000 -log log.lammps
```

`WARNING: Using fix shake with minimization` is expected: SHAKE constraints are only approximately enforced during the minimize step.

Other molecules: write a molecule file for them (coordinates, types, charges, bonds, angles, dihedrals) and the force-field parameters (`pair_coeff`, `bond_coeff`, ...). For anything bigger than a few atoms, generate the data file with a tool such as moltemplate, Packmol + a force-field assigner, or CHARMM-GUI / LigParGen, then `read_data` it.

## Pressure-driven flow in a channel

File: [`in.poiseuille`](../files/recipes/in.poiseuille) · LJ fluid between two rigid FCC walls

A constant force on every fluid atom along x stands in for a pressure gradient. In steady state the velocity profile across the channel is a parabola (Poiseuille flow), and its curvature gives the viscosity.

Points worth copying for any flow simulation:

- `boundary p f p`: walls bound the channel in y.
- Walls are atoms held in place with `fix setforce 0 0 0`.
- Thermostat only the directions without flow: `compute temp/partial 0 1 1` + `fix langevin` with `fix_modify ... temp`. Thermostatting x would fight the flow.
- `fix ave/chunk` with `compute chunk/atom bin/1d y` builds the velocity profile layer by layer.

```bash
mpirun -n 4 $LMP -in in.poiseuille -log log.lammps
python3 fit_profile.py vprofile.dat --parabola --force 0.02     # the log prints this line
```

`fit_profile.py` fits vx(y) = c₀ + c₁y + c₂y² and uses η = −ρF / (2c₂).

Tested result (full default settings, 100,000 production steps, about 4 minutes on one core): the profile is a clean parabola, and the fit gives η\* = 2.86 at mean density ρ\* ≈ 0.83 and T\* = 1.0. The layers next to each wall are less dense (fluid layering at a wall), so the fit skips the outermost layer on each side.

## Viscosity (Müller-Plathe)

File: [`in.viscosity_mp`](../files/recipes/in.viscosity_mp) · LJ liquid, T* = 1.0, ρ* = 0.8442

`fix viscosity` repeatedly swaps x-momentum between a slab at the bottom and one in the middle of the box. That imposes a known momentum flux; the fluid responds with a linear velocity profile, and η = |flux / (dvₓ/dz)|.

```bash
mpirun -n 4 $LMP -in in.viscosity_mp -log log.lammps
# the log ends with the exact fit command, e.g.:
python3 fit_profile.py vx_profile.dat --flux -0.0305 --length 33.59
```

Tested result (60,000 production steps, about 4 minutes on one core): a clean zig-zag velocity profile (linear between the slabs), and the fit gives η\* = 2.41 at ρ\* = 0.8442, T\* = 1.0.

Two independent methods, same fluid: Poiseuille flow gave 2.86 at ρ\* ≈ 0.83, and Müller-Plathe gave 2.41. They agree to within ~15%, with different densities and short runs on both sides. Agreement between methods like this is a good sanity check before trusting any transport number.

Keep the swap rate gentle (the `100` and `20` in `fix viscosity 100 x z 20`): swapping too often pushes the fluid out of the linear-response regime.

## Thermal conductivity

File: [`in.thermal_conductivity`](../files/recipes/in.thermal_conductivity) · LJ liquid, T* = 1.35, ρ* = 0.6

Same idea with kinetic energy: `fix thermal/conductivity` swaps hot and cold atoms between two slabs, creating a steady temperature gradient, and κ = |flux / (dT/dz)|.

```bash
mpirun -n 4 $LMP -in in.thermal_conductivity -log log.lammps
python3 fit_profile.py temp_profile.dat --flux <flux> --column v_temp --length <Lz>   # printed by the log
```

Tested result (60,000 production steps, about 3 minutes on one core): a linear temperature profile from T\* ≈ 1.23 at the cold slab to ≈ 1.49 at the hot one, and κ\* = 3.72. Longer runs and several seeds narrow the error bar.

!!! warning "Metals and thermal conductivity"

    The same recipe works for a crystal (e.g. Cu with EAM), but classical MD only includes heat carried by atomic vibrations (phonons). In metals, electrons carry most of the heat, so MD badly underestimates a metal's thermal conductivity. It's meaningful for insulators, semiconductors and the phonon part only.

## `fit_profile.py`

[`fit_profile.py`](../files/recipes/fit_profile.py) reads the last block of any `fix ave/chunk` file and fits it. It runs on macOS, Windows and Linux with plain Python 3 (no packages needed).

=== "macOS"

    ```bash
    python3 fit_profile.py vx_profile.dat --flux -0.0305 --length 33.59
    python3 fit_profile.py vprofile.dat --show
    ```

=== "Windows"

    ```powershell
    py fit_profile.py vx_profile.dat --flux -0.0305 --length 33.59
    py fit_profile.py vprofile.dat --show
    ```

=== "Linux"

    ```bash
    python3 fit_profile.py vx_profile.dat --flux -0.0305 --length 33.59
    python3 fit_profile.py vprofile.dat --show
    ```

| Option | Meaning |
|---|---|
| `--flux F` | Flux printed by the recipe → prints the transport coefficient |
| `--length L` | Box length along the profile (for files with reduced 0–1 coordinates) |
| `--column NAME` | Which column to fit (default: last) |
| `--parabola --force F` | Poiseuille mode: quadratic fit → viscosity |
| `--show` | Print the profile table |

For the Müller-Plathe recipes it fits the straight part of the lower half of the box, skipping two bins next to each swap slab.
