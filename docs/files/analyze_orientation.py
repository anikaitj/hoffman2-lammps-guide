#!/usr/bin/env python3
"""
analyze_orientation.py: measure crystal structure and (111) orientation
in a LAMMPS trajectory or data file, frame by frame, the way the lab reports it.

For every frame it reports:
  * FCC / HCP / BCC / Other fractions (Polyhedral Template Matching)
  * % of FCC atoms with a <111> direction within WINDOW degrees of z  -> "(111) %"
  * % of FCC atoms with a <100> direction within WINDOW degrees of z  -> "(100) %"
  * number of grains (OVITO grain segmentation, minimum grain size 50), optional

Works on macOS (Apple silicon), Windows and Linux.
Needs: Python 3.11+ and the OVITO module   ->   pip install ovito numpy

Usage:
    python3 analyze_orientation.py traj.lammpstrj
    python3 analyze_orientation.py traj.lammpstrj --type 1          # only film atoms (type 1)
    python3 analyze_orientation.py traj.lammpstrj --grains          # also count grains (slower)
    python3 analyze_orientation.py traj.lammpstrj --every 5         # every 5th frame
    python3 analyze_orientation.py data.final --window 15           # different angle window
    python3 analyze_orientation.py traj.lammpstrj --rmsd 0          # classify every atom (hot frames)
    (On Windows use "python" or "py" instead of "python3".)

Output: a table on screen and <name>_orientation.csv next to the input file.
"""
import argparse
import csv
import math
import os
import sys

try:
    import numpy as np
    from ovito.io import import_file
    from ovito.modifiers import (PolyhedralTemplateMatchingModifier as PTM,
                                 GrainSegmentationModifier)
except ImportError as e:
    sys.exit(f"Missing module ({e.name}). Install with:  pip install ovito numpy\n"
             "(OVITO's Python module needs Python 3.11+; no wheel for Intel Macs.)")


def z_direction(q):
    """Crystal-frame direction that points along lab z, for PTM quaternions (X,Y,Z,W).

    This is the third row of the rotation matrix, i.e. the same formulas used in
    the OVITO Compute-property recipe in the guide (zx, zy, zz).
    """
    x, y, z, w = q[:, 0], q[:, 1], q[:, 2], q[:, 3]
    zx = 2 * (x * z - w * y)
    zy = 2 * (y * z + w * x)
    zz = 1 - 2 * (x * x + y * y)
    return np.stack([zx, zy, zz], axis=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="LAMMPS dump (traj.lammpstrj) or data file (data.final)")
    ap.add_argument("--type", type=int, nargs="*",
                    help="only count these atom types (e.g. --type 1 to skip a type-2 template)")
    ap.add_argument("--window", type=float, default=5.0,
                    help="angle window in degrees (default 5; lab standard)")
    ap.add_argument("--grains", action="store_true",
                    help="also count grains (grain segmentation, min size 50); slower")
    ap.add_argument("--rmsd", type=float, default=0.1,
                    help="PTM RMSD cutoff (default 0.1 = OVITO default). 0 = no cutoff: every "
                         "atom is forced into some structure, which inflates HCP/BCC at grain "
                         "boundaries but keeps hot vibrating atoms classified")
    ap.add_argument("--every", type=int, default=1, help="analyse every Nth frame")
    ap.add_argument("--out", help="CSV file name (default: <input>_orientation.csv)")
    args = ap.parse_args()

    if not os.path.exists(args.file):
        sys.exit(f"File not found: {args.file}")

    pipe = import_file(args.file)
    pipe.modifiers.append(PTM(rmsd_cutoff=args.rmsd, output_orientation=True))
    if args.grains:
        pipe.modifiers.append(GrainSegmentationModifier(min_grain_size=50))

    cos_w = math.cos(math.radians(args.window))
    d111 = np.array([[1, 1, 1], [1, 1, -1], [1, -1, 1], [-1, 1, 1]]) / math.sqrt(3)

    if args.out:
        out = args.out
    else:  # next to the input: traj.lammpstrj -> traj_orientation.csv, data.final -> data_final_orientation.csv
        folder, base = os.path.split(args.file)
        for ext in (".gz", ".lammpstrj", ".dump", ".lmp", ".data"):
            if base.endswith(ext):
                base = base[: -len(ext)]
        out = os.path.join(folder, base.replace(".", "_") + "_orientation.csv")
    cols = ["frame", "timestep", "atoms", "FCC_%", "HCP_%", "BCC_%", "Other_%",
            f"111_of_FCC_%", f"100_of_FCC_%"] + (["grains"] if args.grains else [])

    print(f"{args.file}: {pipe.num_frames} frame(s); window {args.window:g} deg; PTM RMSD cutoff {args.rmsd:g}"
          + (f"; atom types {args.type}" if args.type else ""))
    print("  ".join(f"{c:>12}" for c in cols))

    rows = []
    for frame in range(0, pipe.num_frames, args.every):
        data = pipe.compute(frame)
        st = np.asarray(data.particles["Structure Type"])
        q = np.asarray(data.particles["Orientation"])
        keep = np.ones(len(st), bool)
        if args.type:
            keep = np.isin(np.asarray(data.particles["Particle Type"]), args.type)
        st, q = st[keep], q[keep]
        n = len(st)
        if n == 0:
            sys.exit("No atoms left after --type filter. Check the type numbers.")

        frac = lambda k: 100.0 * np.count_nonzero(st == k) / n  # 0 other,1 FCC,2 HCP,3 BCC
        fcc = st == 1
        nf = np.count_nonzero(fcc)
        if nf:
            zdir = z_direction(q[fcc])
            zdir /= np.linalg.norm(zdir, axis=1, keepdims=True)
            is111 = np.max(np.abs(zdir @ d111.T), axis=1) >= cos_w
            is100 = np.max(np.abs(zdir), axis=1) >= cos_w
            p111 = 100.0 * np.count_nonzero(is111) / nf
            p100 = 100.0 * np.count_nonzero(is100) / nf
        else:
            p111 = p100 = 0.0

        ts = data.attributes.get("Timestep", frame)
        row = [frame, ts, n, frac(1), frac(2), frac(3), frac(0), p111, p100]
        if args.grains:
            row.append(int(data.attributes.get("GrainSegmentation.grain_count", 0)))
        rows.append(row)
        print("  ".join(f"{v:>12.1f}" if isinstance(v, float) else f"{v:>12}" for v in row))

    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerows([[f"{v:.2f}" if isinstance(v, float) else v for v in r] for r in rows])
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
