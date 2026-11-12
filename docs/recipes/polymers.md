# Polymers

File: [`in.polymer_melt`](../files/recipes/in.polymer_melt) · 200 chains × 20 beads (4,000 beads) · `lj` units · needs MOLECULE

The Kremer–Grest bead-spring model is the standard coarse-grained polymer: each bead stands for a few monomers, neighbours along a chain are joined by FENE springs, and all beads repel each other with a purely repulsive LJ (WCA) potential. It reproduces generic polymer physics (entanglement, Rouse and reptation dynamics, glass transition) without chemical detail.

## How the input works

1. Writes its own chain template. A loop in the input writes `chain.mol`, a straight chain of `nbeads` beads 0.97σ apart with bonds 1–2, 2–3, ... Changing `-var nbeads 50` changes the chain length; no other file to edit.
2. Scatters chains randomly: `create_atoms 0 random ...`. They overlap, which a normal potential can't handle.
3. Soft push-off: `pair_style soft` with a prefactor ramped from 0 to 60, `fix nve/limit` (caps how far atoms move per step) and a Langevin thermostat. Overlapping beads slide apart gently.
4. Real model: `pair_style lj/cut 1.12246` with `pair_modify shift yes` (the WCA potential), FENE bonds (`bond_coeff 1 30.0 1.5 1.0 1.0`, the standard K = 30, R₀ = 1.5), `special_bonds fene`, timestep 0.01τ.
5. Measures the mean radius of gyration of the chains (`compute gyration/chunk`) as it relaxes.

```bash
mpirun -n 4 $LMP -in in.polymer_melt -log log.lammps
# quick test (50 chains, short):
mpirun -n 4 $LMP -in in.polymer_melt -var nchains 50 -var nsoft 2000 -var neq 5000 -log log.lammps
```

In the quick test, the mean Rg fell from 4.07 to 3.34σ over 5,000 steps as the initially straight chains started to coil. It needs the full run (or much longer for long chains) to level off. Wait for Rg to stop drifting before measuring anything.

## Key settings

| Line | Why |
|---|---|
| `comm_modify cutoff 2.0` | FENE bonds stretch up to 1.5σ, longer than the short pair cutoff; without this LAMMPS warns about bonds crossing processor boundaries |
| `special_bonds fene` | Bonded neighbours still feel the WCA repulsion (weights 0 1 1), as the model requires |
| `fix nve/limit 0.1` | Only during push-off: stops atoms shooting off while overlaps are huge |
| `dump ... xu yu zu` | Unwrapped coordinates, so chains don't look broken across periodic boundaries in OVITO |

## Equilibration takes long

Polymer relaxation times grow quickly with chain length: roughly N² for unentangled chains and N³ or worse once they're entangled. 20-bead chains relax in ~10³–10⁴ τ; 200-bead chains take orders of magnitude longer. For long chains, use established methods (e.g. the "double-bridging" Monte Carlo moves in `fix bond/swap`, or pre-built equilibrated configurations).

## Going further

| Goal | What to add |
|---|---|
| Glass transition | Add a weak attraction (`lj/cut` with cutoff 2.5), then cool slowly at constant pressure (`fix npt`) and watch density vs T |
| Diffusion | `compute msd` on chain centres of mass (`compute com/chunk`) |
| Real chemistry | All-atom force fields (OPLS-AA, PCFF via the CLASS2 package) in `real` units; build the data file with moltemplate or similar |
| Crosslinking / curing | `fix bond/create`, or `fix bond/react` (REACTION package) |
| Polymer under flow | `fix deform` with `remap v` + `fix nvt/sllod` |

Visualise in OVITO: load `traj.lammpstrj` and add Create bonds. Colouring by the `mol` column gives each chain its own colour.
