# Measuring orientation

"Is it (111)?" is the main question in the lab's Cu work. This page is how to answer it rigorously.

## What does NOT count as evidence

!!! danger "RDF peaks are not orientation"

    RDF peaks at 2.55, 3.63 and 4.45 Å show FCC copper with the right lattice constant. Any orientation and any number of grains gives the same peaks. Early lab reports used RDF as "agreement with Chen Fig. 3b"; that doesn't show (111).

Also not enough: "mostly green in PTM" (that's FCC, any orientation), or a single picture.

## The metric: PTM orientation per atom

With Lattice orientations on, PTM gives each FCC atom a quaternion (`Orientation.X/Y/Z/W`): the rotation from a reference cube to that atom's crystal. From it you can compute which crystal direction points along z (the film normal); that's the third row of the rotation matrix:

```
zx = 2*(Orientation.X*Orientation.Z - Orientation.W*Orientation.Y)
zy = 2*(Orientation.Y*Orientation.Z + Orientation.W*Orientation.X)
zz = 1 - 2*(Orientation.X^2 + Orientation.Y^2)
```

An atom is (111) if one of its four ⟨111⟩ directions is close to z. Since ⟨111⟩ = (±1, ±1, ±1)/√3, that's:

```
max(|zx+zy+zz|, |zx+zy−zz|, |zx−zy+zz|, |−zx+zy+zz|) / √3  ≥  cos(θ)
```

### Use a 5° window, not 15°

| Window | cos θ × √3 | Problem |
|---|---|---|
| 15° | 1.673 | Counts (569) grains (14.3° off) as (111): 99.3% of a perfect (569) crystal in our check. Also counted twinned (111) crystal, which leaves [115] along z, as (100). |
| 5° | 1.7255 | Separates (111) from (569) and (122). Current lab standard. |

The lab first used 15° and switched to 5° after finding those miscounts. Report which window you used.

Report: "X% of FCC atoms have a ⟨111⟩ direction within 5° of z."

## With a script: every frame, every run, same numbers

[`analyze_orientation.py`](../files/analyze_orientation.py) does the whole measurement and writes a CSV. It runs on macOS (Apple silicon), Windows, Linux and Hoffman2 (needs Python 3.11+ and `pip install ovito numpy`).

=== "macOS"

    ```bash
    python3 analyze_orientation.py traj.lammpstrj --type 1 --grains
    ```

=== "Windows"

    ```powershell
    py analyze_orientation.py traj.lammpstrj --type 1 --grains
    ```

=== "Linux"

    ```bash
    python3 analyze_orientation.py traj.lammpstrj --type 1 --grains
    ```

`--type 1` counts only film atoms (skips a type-2 template). The default PTM RMSD cutoff is 0.1 (`--rmsd 0` to change; see [OVITO basics](ovito.md#rmsd-cutoff-0-vs-01)). Options and expected output: [Files & scripts reference](../help/files-reference.md#analyze_orientationpy).

Checked on perfect crystals: (111) → 100% (111); (100) → 100% (100); (569), (122), (110) → 0% (111) at 5°. At 15°, a perfect (569) crystal counts as 99.3% (111).

## In OVITO: highlight the (111) atoms

1. PTM with Lattice orientations on.
2. Add modification → Expression selection, paste the contents of [`select_111_atoms.txt`](../files/select_111_atoms.txt) (one long line, 5° window).
3. Optionally Assign color (e.g. blue).

The selection count at the bottom of the panel is the number of (111) atoms. Divide by the FCC count from PTM for the percentage.

The expression selects all atoms of a perfect (111) crystal and none of perfect (100) or (110) crystals (checked when it was written).

### Readable version (three Compute property modifiers)

Add three Compute property modifiers with output names `zx`, `zy`, `zz` and the formulas above, then:

```
(111), 5°:   StructureType==1 && max(abs(zx+zy+zz),abs(zx+zy-zz),abs(zx-zy+zz),abs(-zx+zy+zz)) >= 1.7255
(100), 5°:   StructureType==1 && max(abs(zx),abs(zy),abs(zz)) >= 0.9962
```

## Which plane is facing up?

To label a grain as (569), (122) etc., compare its z-direction with each candidate plane and take the nearest. The lab's list: (111), (100), (110), (112), (113), (114), (122), (133), (123), (569), (188), (236), (012), (013), (023), (135).

Angles from (111) for the planes in Shao et al.:

| Plane | Angle from (111) | |
|---|---|---|
| (569) | 14.3° | closest to (111) of the paper's grains |
| (122) | 15.8° | |
| (112) | 19.5° | |
| (236) | 24.9° | |
| (188) | 30.2° | |
| (110) | 35.3° | |
| (100) | 54.7° | square surface pattern |

## Stacking faults vs twins vs grain boundaries

| Defect | What it is | In PTM | Grain segmentation |
|---|---|---|---|
| Stacking fault | One layer in the wrong position: ABCAB\|ABC | 2 red (HCP) layers | Same grain |
| Twin | Stacking order reverses: ABCABC\|BACBAC; both sides (111) up but rotated 60° about [111] | 1 red layer at the boundary | Two grains, misorientation 60° about [111] |
| Grain boundary | Two differently oriented crystals meet | White | Two grains |

Report the HCP fraction alongside the (111) fraction, measured with PTM RMSD cutoff 0.1 on a cooled frame ([why](ovito.md#rmsd-cutoff-0-vs-01)). "(111) texture with 7–45% faulted atoms" is a different result from "twin-free single crystal".

## A complete orientation report

For each run, give:

1. (111) fraction of FCC atoms (5° window), at the start and end
2. FCC / HCP / Other fractions (PTM)
3. Number of grains (min size 50) and whether the main ones are twins
4. Whether the run melted ([MSD](melting-and-thermo.md))
5. Number of repeats (different `vseed`) and the spread
