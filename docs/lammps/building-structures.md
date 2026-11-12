# Building structures

How to build the starting configurations the lab uses: oriented single crystals, polycrystals, thin films with vacuum, and (111) templates. A complete, tested version of all of this is [`in.film_template`](../files/in.film_template) ([walkthrough](../examples/film-template.md)).

## Miller indices in one minute

- (hkl) names a crystal plane; [hkl] names a direction. In cubic crystals, [hkl] is perpendicular to (hkl).
- A "(111) film" means the (111) planes are parallel to the surface, so [111] points along z (up).
- In FCC copper, (111) planes are the most tightly packed layers. (111) has the lowest surface energy, which is why free films tend to prefer it and why it's the target for graphene growth.
- Cubic symmetry makes [569], [659], [−9 5 6] and so on equivalent. Sort the absolute values (h ≥ k ≥ l, or the reverse) to name the family.

## Orienting a crystal: `lattice ... orient`

```
lattice  fcc 3.615  orient x 1 -1 0  orient y 1 1 -2  orient z 1 1 1
```

This says which crystal direction lies along each box axis. Rules (LAMMPS errors otherwise):

1. The three vectors must be mutually perpendicular (dot products = 0).
2. They must be right-handed: x × y points along z.
3. Integers only.

### Orientation sets for every grain type we use

All checked: orthogonal and right-handed. "Angle" is the tilt from (111), which is how "far" a grain is from the target.

| Up (z) | `orient x` | `orient y` | `orient z` | Angle from (111) |
|---|---|---|---|---|
| (111) | `1 -1 0` | `1 1 -2` | `1 1 1` | 0° |
| (111), alt. in-plane | `1 0 -1` | `-1 2 -1` | `1 1 1` | 0° |
| (569) | `3 -1 -1` | `3 32 -23` | `5 6 9` | 14.3° |
| (122) | `0 1 -1` | `-4 1 1` | `1 2 2` | 15.8° |
| (112) | `1 -1 0` | `1 1 -1` | `1 1 2` | 19.5° |
| (236) | `0 2 -1` | `-15 2 4` | `2 3 6` | 24.9° |
| (188) | `0 1 -1` | `-16 1 1` | `1 8 8` | 30.2° |
| (110) | `0 0 1` | `1 -1 0` | `1 1 0` | 35.3° |
| (100) | `1 0 0` | `0 1 0` | `0 0 1` | 54.7° |

To make your own: pick z = [hkl]; pick any small integer x with x·z = 0; set y = z × x and divide by common factors.

!!! note "In-plane rotation matters"

    Choosing x picks the grain's rotation *around* z. Papers often don't report it (Shao et al. didn't), and it can change how grains interact. Random rotations or the smallest whole-number x (as in the table) are both reasonable; always record which you used.

## Regions: use `units box` with rotated lattices

```
region   g1 block 0 30.7 0 31.0 6.0 31.0 units box     # Å
```

!!! danger "`units lattice` + `orient` = misplaced regions"

    With a rotated lattice, "one lattice unit" isn't along the box axes, so `units lattice` regions end up the wrong size or in the wrong place. Always give regions in Å (`units box`) when using `orient`.

## Polycrystal: several grains in one box

The recipe:

1. `create_box` once (with enough atom types).
2. For each grain: `lattice ... orient ...` → `region ...` → `create_atoms 1 region gN`.
3. Delete atoms that ended up too close across grain boundaries.
4. Minimize.

```
create_box      2 box

lattice         fcc 3.615 orient x 1 0 0 orient y 0 1 0 orient z 0 0 1
region          g1 block 0 30.7 0 31.0 6 31 units box
create_atoms    1 region g1

lattice         fcc 3.615 orient x 3 -1 -1 orient y 3 32 -23 orient z 5 6 9
region          g4 block 30.7 61.3 31.0 62.0 6 31 units box
create_atoms    1 region g4
# ... more grains ...

delete_atoms    overlap 2.0 film all
minimize        1e-6 1e-8 1000 10000
```

### Why `delete_atoms overlap` is essential

Where two differently oriented grains meet, atoms from both can land closer than ~2 Å (normal Cu neighbours are 2.56 Å apart). Huge forces then blow the simulation up. `delete_atoms overlap 2.0 A B` removes one atom of every pair closer than 2.0 Å. The lab uses 2.0–2.2 Å. The log reports `Deleted N atoms`. A few percent is normal (687 of ~10,400 in the film example).

!!! warning "Don't leave gaps between grains"

    A gap of a few Å between grains is about one Cu neighbour distance, well inside the potential's range (4.95 Å for Cu_u3). Gaps slam shut during minimization and the first picoseconds, which twists the grains and can destroy small ones. Build grains touching and delete overlaps instead.

### Periodic images

With periodic x/y, grains also meet their neighbours across the box edge. Two grains with the same orientation touching across the edge are one grain to OVITO (a 3×3 layout with repeated orientations can show 6 grains instead of 9). Plan the layout with that in mind.

## Thin films: vacuum and free surfaces

```
boundary        p p f
region          box block 0 ${lx} 0 ${ly} -25 60 units box    # film from z=0 to ~31 Å, vacuum above and below
```

- Periodic in x and y (an infinite sheet), non-periodic in z with ≥ 25 Å of empty space above and below.
- Use NVT for films (pressure along z isn't meaningful with vacuum). The lab relaxed x/y for 20 ps at 300 K with NPT in x and y only, then locked the box and switched to NVT.
- No gravity in MD, and `velocity ... mom yes` zeroes total momentum, so the film doesn't fall or drift.

### Make x/y match whole crystal repeats

A periodic box must fit a whole number of repeats of any crystal that spans it (e.g. a template), or there's a seam at the edge. For (111) with x = [1 −1 0] and y = [1 1 −2]:

| Direction | Repeat length |
|---|---|
| [1 −1 0] | a√2 = 5.112 Å |
| [1 1 −2] | a√6 = 8.855 Å |

```
variable  lx equal 12*3.615*sqrt(2)     # 61.35 Å
variable  ly equal 7*3.615*sqrt(6)      # 61.98 Å
```

(111) layers are a/√3 = 2.087 Å apart, so 3 template layers fit in ~6 Å.

## Templates and seeds

A template is a few layers of Cu(111) under the film, standing in for a (111)-textured substrate or Chen's Cu₂O(111) layer.

```
lattice         fcc 3.615 orient x 1 -1 0 orient y 1 1 -2 orient z 1 1 1
region          rtmpl block INF INF INF INF -0.1 6.0 units box
create_atoms    2 region rtmpl              # type 2 = template
group           tmpl type 2
```

Frozen template (forces zeroed, never moves):

```
fix             hold tmpl setforce 0.0 0.0 0.0
velocity        tmpl set 0.0 0.0 0.0
```

Then thermostat only the mobile atoms (`fix ... mobile nvt ...`, `compute ... mobile temp`).

Mobile template: don't add `setforce`; include the template in the mobile group. A mobile template is more realistic than a frozen one (a real substrate moves too); a frozen template is an idealization worth checking against.

## Other ways to build structures

- Atomsk (free, command line): Voronoi polycrystals, bicrystals, dislocations; writes LAMMPS data files. Shao et al. built their models with it. <https://atomsk.univ-lille.fr/>
- `read_data`: read any structure written by Atomsk, Python (ASE, pymatgen) or a previous run's `write_data`.
- OVITO Basic can't generate structures (those data sources need OVITO Pro). Build in LAMMPS or Atomsk instead.

## Checklist before running a new structure

1. `log.lammps`: do `Created N atoms` / `Deleted N atoms` make sense?
2. OVITO frame 0, with PTM: are grains where you expect? Any holes or overlaps?
3. Grain segmentation at frame 0: right number of grains?
4. After minimization, energy per atom should be a bit above the perfect-crystal value of −3.54 eV/atom, because surfaces and grain boundaries cost energy. The film example gives −3.43 eV/atom. Much higher means overlaps or a broken structure.
