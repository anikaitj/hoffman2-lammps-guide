# OVITO basics

[OVITO](https://www.ovito.org/) is how the lab looks at and measures structures. OVITO Basic (free) does everything on this page. Install it on your laptop and open `traj.lammpstrj` (or any `data.*` file) with File → Load File.

## The modifier stack

OVITO applies modifiers to your data, top to bottom of the pipeline. Add them with Add modification…. The lab's standard stack:

1. Polyhedral template matching (PTM): what structure each atom is in
2. Grain segmentation: which grain each atom belongs to
3. Expression selection (+ Assign color): highlight (111) atoms
4. Optional: Slice to see a cross-section, Expression selection + Delete selected to hide non-FCC atoms

## Polyhedral template matching (PTM)

Compares each atom's neighbours to perfect FCC, HCP, BCC, icosahedral and simple cubic templates.

Settings the lab uses:

| Setting | Value | Why |
|---|---|---|
| Structure types | FCC, HCP, BCC on | |
| Output → Lattice orientations (sometimes labelled "Output orientations") | on | Everything about orientation and grains depends on it |
| RMSD cutoff | 0.1 (default) for structure fractions; 0 only to see orientation of hot frames | See below: cutoff 0 inflates HCP |

Colours:

| Colour | Structure | In our Cu |
|---|---|---|
| Green | FCC | Crystal |
| Red | HCP | Stacking faults and twin boundaries inside FCC |
| Blue | BCC | Rare in Cu; usually a sign of a problem |
| White | Other | Grain boundaries, surfaces, liquid / amorphous atoms |

Surface atoms are always white, because they're missing neighbours. A perfect film still has a white skin on top and bottom.

!!! danger "Use PTM, not CNA"

    Common Neighbor Analysis (CNA) often mislabels FCC copper as HCP and gives no orientation. Shao et al. used CNA; the lab uses PTM. Don't mix the two when comparing numbers.

## RMSD cutoff: 0 vs 0.1

The RMSD cutoff decides how well an atom must match a template to be classified. Above it, the atom is "Other" (white).

- 0.1 (OVITO default): atoms at grain boundaries and in disordered regions are "Other". At high temperature, some vibrating crystal atoms also become "Other".
- 0 (no cutoff): *every* atom is forced into its closest template, including grain-boundary atoms, which often land in HCP or BCC.

Measured on frame 0 of the [film example](../examples/film-template.md) (film atoms only, 300 K, freshly built grains):

| Cutoff | FCC | HCP | BCC | Other |
|---|---|---|---|---|
| 0.1 | 48.3% | 3.6% | 0.3% | 47.9% |
| 0 | 59.5% | 27.0% | 5.2% | 8.3% |

!!! warning "Don't count stacking faults with cutoff 0"

    With cutoff 0, grain-boundary atoms show up as HCP, so "HCP fraction" overstates stacking faults and twins: here 27% versus 3.6%. Before quoting fault fractions, re-measure the final, cooled frame with cutoff 0.1, or report both.

Use 0.1 for structure fractions (FCC/HCP/Other) on cooled frames. Cutoff 0 is useful to watch orientation through hot frames, where the (111) selection only looks at FCC atoms anyway.

## Grain segmentation

Groups atoms with the same crystal orientation into grains.

| Setting | Value |
|---|---|
| Requires | PTM with lattice orientations |
| Minimum grain size | 50 atoms (10 gives noise "grains") |
| Color particles by grain | On |

Things to know:

- Colours aren't fixed between frames. OVITO re-picks colours each frame. Compare *how many* grains, not which colour.
- Twins count as two grains. Two (111) regions rotated 60° about [111] are twins; both face up, but segmentation splits them. A (111) film that formed from several grains often ends up as two twin domains: two grains to OVITO, one orientation.
- Grains touching across the periodic boundary with the same orientation are one grain.

The grain list (in the modifier panel) gives each grain's atom count and orientation.

## Looking at the structure

- Top view (looking down z): (111) shows a triangular / hexagonal atom pattern, (100) a square grid, tilted grains show rows at odd angles.
- Side view: a (111) film shows flat horizontal layers stacked ABCABC. A red (HCP) layer is a stacking fault or twin boundary.
- To see only crystal atoms: Expression selection `StructureType != 1` → Delete selected.
- Slice modifier (normal = z, slab width a few Å) shows one layer at a time.

## Exporting

- Render tab → render the active viewport to PNG, or an animation over all frames (MP4/GIF).
- File → Export File → "Table of values" exports per-frame numbers (e.g. PTM counts, selection count) as text for plotting.
- Python: `pip install ovito` gives the same modifiers in scripts, useful for analysing many runs the same way.

## Frame timing

Each frame is one dump. With `dump ... 20000` and a 1 fs timestep, one frame = 20 ps. Say this when you show frames: "frame 10 = 200 ps".

Next: [Measuring orientation](orientation.md).
