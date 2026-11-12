# Metals: mechanics, surfaces, grain boundaries

Three recipes for copper with the Foiles `Cu_u3.eam` potential (download it as on [Potentials](../lammps/potentials.md#download-on-hoffman2-in-your-run-folder)). All work for any EAM metal: change the lattice, lattice constant and potential file.

## Tensile test

File: [`in.cu_tensile`](../files/recipes/in.cu_tensile) · single-crystal Cu, 4,000 atoms, pulled along [100] at 300 K

1. Equilibrates at 300 K and zero pressure (NPT).
2. `fix deform 1 x erate ...` stretches the box along x at a constant engineering strain rate (default 10⁹ s⁻¹).
3. `fix npt ... y 0 0 1.0 z 0 0 1.0` lets the sides contract (zero lateral stress), as in a real tensile test.
4. Writes `stress_strain.dat`: strain and σₓₓ in GPa.

```bash
mpirun -n 8 $LMP -in in.cu_tensile -log log.lammps
# quick test (small box, to 5% strain):
mpirun -n 4 $LMP -in in.cu_tensile -var nx 6 -var neq 2000 -var strain 0.05 -log log.lammps
```

Check: in the quick test, the slope between 0.5% and 2% strain was 64 GPa, the elastic modulus of copper along [100] for this potential. At 25% strain (full run), the curve shows the yield point, where dislocations nucleate, and a stress drop.

Pressure sign: LAMMPS reports pressure, which is positive in compression, so the input uses stress = −pressure.

!!! note "Strain rates"

    MD strain rates (10⁸–10¹⁰ s⁻¹) are many orders of magnitude faster than lab tests, so MD yield stresses come out high. Perfect crystals with no defects also yield at stresses far above real metals. Compare trends (orientation, temperature, grain size), not absolute numbers.

Variations: polycrystals (build grains as in [Building structures](../lammps/building-structures.md)), other directions (rotate the lattice), compression (negative `erate`), shear (`fix deform ... xy erate`). Watch dislocations in OVITO with Dislocation analysis (DXA).

## Surface energies

File: [`in.cu_surface_energy`](../files/recipes/in.cu_surface_energy) · runs in under a second on one core

γ = (E_slab − N·E_bulk) / (2A): the extra energy of the two surfaces of a slab compared with the same atoms in bulk. All at 0 K after minimization.

| Surface | γ with Cu_u3.eam (this recipe) |
|---|---|
| (111) | 1.181 J/m² (lowest) |
| (100) | 1.288 J/m² |
| (110) | 1.412 J/m² |

This is why thin films tend toward (111): it has the lowest surface energy, so free surfaces favour it. It also explains why fully periodic boxes (no surfaces) don't select (111).

```bash
$LMP -in in.cu_surface_energy        # one core is plenty
cat surface_energies.txt
```

!!! danger "The bug this recipe avoids"

    The first version of this input sized the slabs in `units lattice` with rotated lattices. The (111) box then didn't fit whole crystal repeats, and γ(111) came out as 1.74 J/m², the *highest*, which is wrong. Box sizes are now in Å and set to whole repeats (a√2, a√6, a√3 for (111)), and the slab fills x and y completely (`INF INF`). Both are needed: with the box right but the region bounded at the box edge, 9 atoms went missing and γ(111) was still wrong (1.34).

To compare potentials, change `pair_style`/`pair_coeff` (e.g. Mishin `eam/alloy`) and rerun.

## Grain-boundary energy

File: [`in.cu_gb_energy`](../files/recipes/in.cu_gb_energy) · Σ5 (310)[001] symmetric tilt boundary · ~35 s on one core

Two grains, mirror images across the (310) plane, both with [001] along z (the tilt axis). The box is periodic in all directions, so it holds two boundaries: E_GB = (E − N·E_bulk) / (2A).

A boundary's energy depends on how the two grains are shifted against each other and which crowded atoms are removed. The recipe scans:

- 4 shifts along x × 2 shifts along z,
- 3 overlap-deletion cutoffs (1.6, 2.0, 2.2 Å),

relaxes each (including the boundary spacing with `fix box/relax y`), writes every trial to `gb_scan.txt`, and keeps the lowest.

| Result | Value |
|---|---|
| No shift (first trial) | 956.0 mJ/m² |
| Lowest found | 894.9 mJ/m² (shift 0.25 in x, 0.5 in z) |

```bash
$LMP -in in.cu_gb_energy
sort -t= -k5 -n gb_scan.txt | head        # lowest trials
```

The best structure is saved as `data.gb_best`; open it in OVITO (PTM shows the boundary as white atoms between two green grains).

For Shao et al.'s bicrystals ((111)/(569) and so on): the same approach, but the two grains have different in-plane repeat lengths, so the box has to fit both (often large), or one grain gets slightly strained. Shao et al. define E_GB = (E_p − N·E_coh) / 2S, which is the same formula. A finer shift grid gives a more reliable minimum.

## Other metal simulations

| Simulation | Start from |
|---|---|
| Nanoindentation | `fix indent` (spherical indenter) on a slab with a fixed bottom; LAMMPS `examples/indent` |
| Crack propagation | LAMMPS `examples/crack` (2D LJ) as a template |
| Melting point | Solid–liquid coexistence: half crystal, half liquid in one box, NPH or NPT; find T where the interface doesn't move |
| Vacancy / interstitial energy | Remove or add one atom in a bulk box, minimize, compare energies |
| Stacking-fault energy | Shift the top half of a (111) slab along [112]; energy per area vs shift |
| Alloys | `eam/alloy` file with several elements + `fix atom/swap` (MC package) for ordering |
| Deposition (film growth) | `fix deposit` onto a substrate |
